import os
import streamlit as st
from streamlit_theme import st_theme
import pandas as pd
import plotly.express as px
from geojson import load
from utils.filter import clean_raw_data, process_merged_data

# Directory pathing
curr_dir = os.path.dirname(__file__)
merged_dataset_path = os.path.relpath('./data/merged_dataset.xlsx', start=curr_dir)
geojson_path = os.path.relpath('../map-data/paris_arrondisements.geojson')

# Page configs
st.set_page_config(
    page_title="Main",
    menu_items={
        'About': """
        
        #### About
        This dashboard was made with the help of volunteer from Omdena as part of the France's Local Chapter Challenge.

        """
    }
)

# Get theme
theme = st_theme()
st.write(theme)

# Reading GeoJSON
with open(geojson_path) as f:
    gj = load(f)

# Data filtering
# df = pd.read_csv(csv_path)
df = pd.read_excel(
  merged_dataset_path,
  # rent in euros, area in sq. m
  names=['rent/cost', 'zipcode', 'arrondissement', 'area', 'rooms', 'bedrooms', 'bathroom', 'type'],
  dtype={
    'zipcode': 'string',
    'type': 'string'
  }
)
cleaned_df = clean_raw_data(df)
st.write(cleaned_df.head(5))

# Streamlit UI
st.title('Paris Property Listings')

# Sidebar for user inputs, the right portion would be dedicated for user-preview
st.sidebar.header('Please Provide your preferences')


rent_or_buy_help = """
    This option lets you filter which types of housing will appear on your map. 
"""
# Initial choice of rent/purchase
# Docs:- https://docs.streamlit.io/develop/api-reference/widgets/st.radio
rent_or_buy = st.sidebar.radio(
    'Do you want to rent or buy a property?', 
    ('Rent', 'Buy'),
    help=rent_or_buy_help)

min_max_rooms_help = """
    This slider filters for the acceptable number of rooms that a property can have on the map.
"""
# Rooms range
min_max_rooms = st.sidebar.slider(
    'Number of Rooms:',
    min_value=1,
    max_value=10,
    value=(1, 2),
    step=1,
    help=min_max_rooms_help
)

# District preference
# Docs:- https://docs.streamlit.io/develop/api-reference/widgets/st.multiselect

# Budget range slider
# Docs:- https://docs.streamlit.io/develop/api-reference/widgets/st.slider
if rent_or_buy == 'Rent':
    budget_range = st.slider(
    'Select your budget range (in euros):', 
    min_value=0, 
    max_value=10000, 
    value=(500, 2000), # Default Range
    step=100, # Increase by 100 Euros
)

if rent_or_buy == 'Buy':
    budget_range = st.slider(
    'Select your budget range (in euros):', 
    min_value=100000, 
    max_value=500000, 
    value=(100000, 200000), # Default Range
    step=10000 # Increase by 10000 Euros
)

districts = st.multiselect(
    'Preferred Arrondissement/District:', 
    options=cleaned_df['arrondissement'].unique(), 
    default=cleaned_df['arrondissement'].unique() # Select all by default
)


# Call the function to Filter data, All options to filter data should be made available before this step
filtered_df = process_merged_data(cleaned_df, budget_range, rent_or_buy, min_max_rooms, districts)

st.divider()
# Create three columns for the KPI cards
col1, col2, col3 = st.columns(3)


with col1:
    st.metric(
        label="Total Properties Found",
        value=f"{len(filtered_df)}"
    )

with col2:
    st.metric(
        label=f"Average {rent_or_buy}",
        value=f"{round(filtered_df['rent' if rent_or_buy == 'Rent' else 'cost'].mean())} euros"
    )

with col3:
    st.metric(
        label="Average size",
        value=f"{round(filtered_df['area'].mean())} sq. m."
    )

# If no properties found
if filtered_df.empty:
    st.warning('No properties found matching your criteria. Please adjust your filters.')

size_data = pd.DataFrame(filtered_df.groupby(['arrondissement']).size().reset_index())
size_data.rename(
    columns={0: 'count'},
    inplace=True
)
st.write(size_data)

fig = px.choropleth_mapbox(
  size_data,
  geojson=gj,
  color='count',
  locations='arrondissement',
  featureidkey='properties.cartodb_id',
  color_continuous_scale="Viridis",
  range_color=(0,110),
  zoom=10,
  opacity=0.5
  )
fig.update_layout(
  mapbox_center={'lat': 48.8566, 'lon': 2.3522},
  margin={'r':0,'t':0,'l':0,'b':0}
)

if theme['backgroundColor'] == "#ffffff":
    fig.update_layout(mapbox_style="carto-positron")
if theme['backgroundColor'] == "#0e1117":
    fig.update_layout(mapbox_style='carto-darkmatter')

# mapbox-layers :- https://plotly.com/python/mapbox-layers/
fig.update_layout(
    modebar={
        'orientation': 'v',
    },
    legend_title='Property Type',
    legend_y=0.5,
    uirevision='constant'
)
fig.update_geos(
    showcountries=True
)

fig.update_mapboxes(
    bounds={
        'north': 51.138093815546775,
        'west': -5.979299805444654,
        'south': -42.11925588687173,
        'east': 8.401274768380318
    }
)

st.plotly_chart(fig)

st.divider()

# Display additional data about the filtered properties
# TODO: update dashboard according to PowerBI uttility?
if not filtered_df.empty:
    st.subheader('Top 5 options for you would be')
    st.dataframe(filtered_df[:5])

    # Download button for filtered data
    # Generate a printable PDF file with necessary information about the properties
    st.download_button(
        label='Download Filtered Data',
        data=filtered_df.to_csv(index=False),
        file_name='filtered_properties.csv',
        mime='text/csv',
    )

    # Display summary statistics
    # Could generate an statistical numeric / Index to find out which would be the best option
    # Which one would have the most:- Size, Number of rooms, Lease Length at the least cost - Use this information to plot a scatter plot
    # Example from KF24 PG54
    st.subheader('Summary Statistics')
    st.write(filtered_df.describe())

    # Histogram of property prices
    
    # st.subheader('Price Distribution')
    # price_column = 'Cost' if rent_or_buy == 'Buy' else 'Rent'
    # fig_hist = px.histogram(filtered_df, x=price_column, nbins=20, title='Price Distribution')
    # st.plotly_chart(fig_hist)