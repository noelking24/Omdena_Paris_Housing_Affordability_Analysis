import streamlit as st

st.set_page_config(
  page_title="Ex-stream-ly Cool App",
    page_icon="🧊",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': 'https://www.extremelycoolapp.com/help',
        'Report a bug': "https://www.extremelycoolapp.com/bug",
        'About': "# This is a header. This is an *extremely* cool app!"
    }

)

st.title("Guide to using the Dashboard")

st.write("""
  ## How this works
  
  This dashboard is meant to give users additional information on the districts (arrondissements) by showing
  where locations for viable and affordable housing are found based on the preferences set for the dashboard.
         
  ## What this is not
         
  - To be updated later
""")