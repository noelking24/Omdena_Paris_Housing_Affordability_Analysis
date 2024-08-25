# Documentation Notes - Data Analysis
## Python Code
* Important packages:
1. Pandas
2. Numpy
3. Matplotlib

* Sources of data:
1. Merged Dataset - Created using various datasets collated by the Data Collection Team

* Relevant Variables:
1. Price/Rent (Euros)
2. Zip Code
3. Arrondissement
4. Area (m²)
5. Rooms
6. Bedrooms
7. Bathroom
8. Type - Housing/Monthly Rent


* Exploratory Data Analysis
1. Data Cleaning and Preparation - Addressed missing values and outliers
2. Descriptive Statistics - Generated summary statistics to understand data distribution and central tendencies
3. Data Visualisation: Create histograms, scatter plots and heatmaps to visually explore relationships and patterns
4. Correlation Analysis: Analysed relationships between variables, such as income levels and housing prices

* Scam Identification:
1. Used a derived variable made using Price/Rent (Euros) and Area (m²) called Price/Sqm
2. Detected Outliers using statistical method called "Confidence Interval" keeping the parameter at 80% to establish lower and upper bounds for Price/Sqm in each arrondissement
