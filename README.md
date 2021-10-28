# Prediction of market premium
<p align="center">
<img src="./03_Image/client map.png" alt="SCOR-Datathon" width="1000">
</p>

<!-- markdown-toc start - Don't edit this section. Run M-x markdown-toc-refresh-toc -->

## Project context and objectives
In recent years, the gap between the amount of modeled premium and actual premium has been increasing for property damage and business interruption insurance policies, due to the increase of unpredictable catastorophic events. Thus, as a reninsurance comany, they want to minimize the gap as much as possible to reduce the losses, by leveraging the data science.<br>
<br>
The difficulty was lying on:
- Large variation in categorical variables (country and industry), which increases the variance and could not be simply one-hot-encoded 
- Extreme values which could not be treated as outliers and high variance in target data with relatively small number of observations
- One premium value contanis several detailed regions or business unites, which have to be captured somehow.
*Since the data is confidencial, this repository represents only part of our work.<br>

## Solution highlishts
- Feeded NASA natural disaster data (earthquake)
- To reduce variance, rigorously selected only the features that has significant marginal effect
- Applied label encoding and hashing for encoding
- To reduce overfitting, stacked combined Boostong and Bagging

<p align="center">
<img src="./03_Image/EarthquakeRisk.png" alt="Earthquake risk and premium" width="600">
</p>
<br><br><br>
<p align="center">
<img src="./03_Image/ModelBuildingApproach.png" alt="Approach" width="800">
</p>
<br><br><br>
<p align="center">
<img src="./03_Image/ShapValue.png" alt="Model interpretation" width="800">
</p>

## Further work
- Although our model score was one of the top, there was problem in hasing of categorical variables - it was very specific to training data - thus, fix the hashing problem
- Retain detail information by weight the value insured value etc.
- Earthquake shap value has non linearity, it can be assumed from the data analysis that impact of earthquake is depending on the industry and country of the client, 
for example Japan is faced with numerous earthquake risks but at the same time the infrustructure is one of the strongest in the world so would not cause property damage.
