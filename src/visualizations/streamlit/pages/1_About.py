import streamlit as st
import pandas as pd

test_data = {
    'index': [3606, 3611, 3612, 3614, 3617],
    'arrondissement': [1, 1, 1, 1, 1],
    'area': [26, 23, 31, 32, 40],
    'rooms': [1, 1, 1, 1, 1],
    'bedrooms': [0, 2, 1, 1, 2],
    'bathroom': [0, 0, 0, 0, 0],
    'type': ['Monthly Rent', 'Monthly Rent', 'Monthly Rent', 'Monthly Rent', 'Monthly Rent'],
    'rent': [1950, 1380, 1848, 1848, 1990],
    'cost': [None, None, None, None, None]
}
df = pd.DataFrame(test_data).set_index('index')

st.set_page_config(
  page_title="Guide",
  layout="wide",
  initial_sidebar_state="expanded",
)

st.title("About")

st.write("""
  ## How this works
  
  This dashboard is meant to give users additional information on the districts (arrondissements) by showing
  where locations for viable and affordable housing are found based on the preferences set for the dashboard.

  ##### Data used
  - As of August 21, 2024, the initial data used for the dashboard consists of aggregated historical data
  of Paris Arrondissement Properties
  - Future iterations of this dashboard may involve updated sources of data, to the discretion of the maintainer

  ##### Data covered
  - Data refers to the 20 main districts (arrondissements) in Paris
  - Dashboard currently **does not** have any support for
  outer districts of Paris

  ##### Sample Data
""")

st.write(df)

st.write("""
  ##### Contributions
  Omdena Local France Chapter via volunteers
""")