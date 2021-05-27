import pandas as pd
import numpy as np
from datetime import datetime
import time
from matplotlib import pyplot as plt
import statsmodels.api as sm
pd.set_option('precision', 2)
th_props = [('font-size', '14px'),('text-align', 'left'),('font-weight', 'bold'),
            ('color', 'white'),('background-color', 'darkcyan')]
td_props = [('font-size', '14px')]
styles = [dict(selector="th", props=th_props),dict(selector="td", props=td_props)]



def summary(df):
    """
    create styled table of data type, # unique values, available values/%
    """
    table = []
    for col in df.columns:
        table.append((col, df[col].dtype, df[col].nunique(), 
                      df.shape[0] - (df[col].isnull().sum()),
                      round(100 - (df[col].isnull().sum()*100/df.shape[0]), 2)))
    summary = pd.DataFrame(table, columns=['Column name','Type','unique value',
                                           'Available Value','% Availability']).set_index('Column name')
    
    return summary.style.set_table_styles(styles)


def remove_outliers(df, num):
    """
    remove outliers by quantile method
    """
    df_num = df[num]
    for col in df_num.columns:
        try:
            q_lower = df_num[col].quantile(0.01)
            q_upper = df_num[col].quantile(0.99)
            df = df[(df_num[col] < q_upper) & (df_num[col] > q_lower)]
        except Exception as e:
            print(col, e)
            
    return df



def preprocess(df):
    """
    preprocess main file column
    1. clean the deductible column which is text
    2. convert the dates to durations from today
    """
    df[['a', 'b']] = df.DEDUCTIBLES.str.split(', ',expand=True)
    df['pd_bi'] = ""
    df['pd'] = ""
    df['bi'] = ""
    
    # clean PD_BI
    for i, value in enumerate(df.a):
        try:
            if value[:6] == 'PD,BI:':
                df['pd_bi'][i] = value[6:]
                df['pd'][i] = np.nan
            elif value[:3] == 'PD:' and value[9:12] != 'BI:':
                df['pd_bi'][i] = np.nan
                df['pd'][i] = value[3:]
        except Exception: # pass NaNs
            pass 

    for i, value in enumerate(df.b):
        try:
            df['bi'][i] = value[4:]
        except Exception: # pass nans
            df['bi'][i] = np.nan
            
    for i, value in enumerate(df['pd_bi']):
        try:
            df['pd_bi'][i] = df['pd_bi'][i].replace(',','.')
            df['pd_bi'][i] = df['pd_bi'][i].replace('M','')
            df['pd_bi'] = df['pd_bi'].apply(pd.to_numeric)
        except Exception:
            pass
        
    # clean PD
    for i, value in enumerate(df['pd']):
        try:
            if 'M' in value:
                df['pd'][i] = df['pd'][i].replace(' ' and 'M', '')
                df['pd'][i] = df['pd'][i].replace(',','.')
            elif 'loss' in value:
                df['pd'][i] = df['pd'][i].replace('% of loss' or '%ofloss', '')
                df['pd'][i] = df['pd'][i].replace(',','.')
                df['pd'][i] = pd.to_numeric(df['pd'][i])
                df['pd'][i] = df['pd'][i] / 100
            elif 'tiv' in value:
                df['pd'][i] = df['pd'][i].replace('% of tiv' or '%oftiv', '')
                df['pd'][i] = df['pd'][i].replace(',','.')
                df['pd'][i] = pd.to_numeric(df['pd'][i])
                df['pd'][i] = df['pd'][i] / 100  
        except Exception as e:
            pass

    # clean BI
    for i, value in enumerate(df['bi']):
        try:
            df['bi'][i] = df['bi'][i].replace('M', '')
            df['bi'][i] = df['bi'][i].replace('Day(s)' and '% of loss', '')
            df['bi'][i] = df['bi'][i].replace('Day(s)' or '% of loss', '')
            df['bi'][i] = df['bi'][i].replace(',','.')
        except Exception as e:
            pass

    df['bi'] = df['bi'].apply(pd.to_numeric)
    df['pd'] = df['pd'].apply(pd.to_numeric)
    df.drop(['a','b'], axis=1, inplace=True)
    df.drop(['DEDUCTIBLES'], axis=1, inplace=True)
    
    # create new time related features
    df['inception_year'], df['inception_month'] = df['INCEPTION'].dt.year, df['INCEPTION'].dt.month
    df['inception_duration'], df['pricing_duration'] = datetime.now() - df['INCEPTION'], datetime.now() - df['PRICING_DATE']
    df['inception_duration'], df['pricing_duration'] = df['inception_duration'].dt.days, df['pricing_duration'].dt.days
    df['diff'] = (df['INCEPTION'] - df['PRICING_DATE']).dt.days
    
    df['UWYEAR']=pd.to_datetime(df.UWYEAR)
    df['UWYEAR']=df.UWYEAR.dt.year
    df.drop(['INCEPTION','PRICING_DATE'], axis=1, inplace=True)
    
    return df.head()


def feature_hash(df, cat, max_size):
    for col in cat:
        df[col+"_hash"] = df[col].apply(lambda x: hash(x)%max_size)
    return df


def plot_loss(fitted):
    plt.figure(figsize=(12,8))
    plt.plot(fitted.history['loss'], label='loss')
    plt.plot(fitted.history['val_loss'], label='validation_loss')
    plt.title('DNN MAE',fontsize=18)
    plt.xlabel('Epoch',fontsize=18)
    plt.ylabel('MAE',fontsize=18)
    plt.legend()
    plt.grid(True)
    
    
def stepwise(X, y, threshold_in = 0.05, threshold_out = 0.05, verbose = True):
    included = []
    while True:
        changed = False
        # forward step
        excluded = list(set(X.columns) - set(included))
        new_pval = pd.Series(index = excluded)
        
        for i in excluded:
            model = sm.OLS(y, sm.add_constant(pd.DataFrame(X[included + [i]]))).fit()
            new_pval[i] = model.pvalues[i]
            
        if new_pval.min() <= threshold_in:
            best_feature = new_pval.idxmin()
            included.append(best_feature)
            changed = True
            if verbose:
                print('Add  {:30} with p-value {:.6}'.format(best_feature, new_pval.min()))

        # backward step, use all coefs except intercept
        model = sm.OLS(y, sm.add_constant(pd.DataFrame(X[included]))).fit()
        pvalues = model.pvalues.iloc[1:]
        if pvalues.max() > threshold_out:
            changed = True
            worst_feature = pvalues.idxmax()
            included.remove(worst_feature)
            if verbose:
                print('Drop {:30} with p-value {:.6}'.format(worst_feature, new_pval.max()))
        if not changed:
            break
    return included


