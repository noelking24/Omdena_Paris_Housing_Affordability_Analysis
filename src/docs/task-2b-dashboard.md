## Documentation Notes - Dashboard

#### Streamlit Dashboard
- **Important packages**:
  - Streamlit (dashboard construction)
  - st-theme (dynamic theme manipulation)
  - plotly, pandas (Data manipulation and visualization)
  - geopandas, geojson (loading GeoJSON data)
  - numpy (numerical calculation)

- **Source of data**:
  - Merged dataset
  - GeoJSON data of Paris districts

- **Algorithm summary**
  1. Merged dataset and GeoJSON data are first read using pandas and geopandas
  2. Merged dataset is cleaned and filtered of null values in relevant columns
  3. Merged dataset is filtered accordingly based on Streamlit components
  4. Resulting dataset, after being aggregated with additional GeoJSON data, is used as reference for producing necessary visual data and other relevant insights