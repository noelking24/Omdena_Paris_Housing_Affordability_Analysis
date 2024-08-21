import streamlit as st
from Main import filtered_df

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

st.write(filtered_df.head(5))

st.write("""
  ##### Contributions
  Omdena Local France Chapter via volunteers
""")