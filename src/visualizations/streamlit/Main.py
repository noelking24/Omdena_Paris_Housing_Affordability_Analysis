import os
import streamlit as st
from streamlit_theme import st_theme
import pandas as pd
import plotly.express as px
import geopandas as gpd
from geojson import load
from utils.map_settings import update_color_map
from utils.filter import clean_raw_data, process_merged_data
from utils.metrics import (
    calculate_avg_rent_cost, 
    get_max_rentable, 
    get_max_housing,
    get_max_bedrooms,
    get_max_bathrooms
)

# Directory pathing
curr_dir = os.path.abspath('.')
merged_dataset_path = os.path.relpath('./data/merged_dataset.xlsx', start=curr_dir)
geojson_path = os.path.relpath('./data/paris_arrondisements.geojson')

# Page configs
st.set_page_config(
    page_title="Main",
    layout="wide",
    menu_items={
        'About': """
        
        #### About
        This dashboard was made with the help of volunteer from Omdena as part of the France's Local Chapter Challenge.

        """
    }
)

# Get theme
theme = st_theme()

# Reading GeoJSON
with open(geojson_path) as f:
    gj = load(f)

# Get GDF
gdf = gpd.read_file(geojson_path, columns=['name', 'cartodb_id'])
gdf_id_name_only = gdf[['name', 'cartodb_id']]
gdf_id_name_only = gdf_id_name_only.rename({
    'arrondissement': 'cartodb_id'
})

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

# Streamlit UI
st.title('Paris Property Listings')
st.divider()

# Sidebar for user inputs, the right portion would be dedicated for user-preview
st.subheader('Please provide your preferences')

min_max_rooms_help = """
    This slider filters for the acceptable number of rooms that a property can have on the map.
"""
# Rooms range
min_max_rooms = st.slider(
    'Number of Rooms:',
    min_value=1,
    max_value=10,
    value=(1, 2),
    step=1,
    help=min_max_rooms_help
)

rent_or_buy_column, budget_range_column = st.columns([0.3, 0.7])

with rent_or_buy_column:
    rent_or_buy_help = """
        This option lets you filter which types of housing will appear on your map. 
    """
    # Initial choice of rent/purchase
    # Docs:- https://docs.streamlit.io/develop/api-reference/widgets/st.radio
    rent_or_buy = st.radio(
        'Do you want to rent or buy a property?', 
        ('Rent', 'Buy'),
        help=rent_or_buy_help)

# Budget range slider
# Docs:- https://docs.streamlit.io/develop/api-reference/widgets/st.slider
with budget_range_column:
    if rent_or_buy == 'Rent':
        budget_range = st.slider(
        'Select your budget range (in euros):', 
        min_value=0, 
        max_value=get_max_rentable(cleaned_df), 
        value=(500, 2000), # Default Range
        step=100, # Increase by 100 Euros
    )

    if rent_or_buy == 'Buy':
        budget_range = st.slider(
        'Select your budget range (in euros):', 
        min_value=0, 
        max_value=get_max_housing(cleaned_df), 
        value=(100000, 200000), # Default Range
        step=10000 # Increase by 10000 Euros
    )

bedroom_checkbox_col, has_bedroom_col = st.columns([0.3, 0.7])

with bedroom_checkbox_col:
    consider_bedroom = st.checkbox(
        "Prefer unique bedrooms?",
        value=False,
        help="""
        - Check this if you'd like to consider for unique bedrooms
        - :warning: Listings may not include bedrooms, but MAY have single rooms
        that can be used as sleeping quarters
        """
    )

with has_bedroom_col:
    min_max_bedrooms = st.slider(
        "Select range of preferred bedrooms",
        min_value=1,
        # max_value=10,
        max_value=get_max_bedrooms(cleaned_df),
        value=(1, 2),
        disabled=not consider_bedroom
    )    

bathroom_checkbox_col, has_bathroom_col = st.columns([0.3, 0.7])

with bathroom_checkbox_col:
    consider_bathroom = st.checkbox(
        "Consider bathroom/s?",
        value=False,
        help="""
        - Check this if you'd like to consider for bathrooms when checking for properties
        """
    )

with has_bathroom_col:
    min_max_bathroom = st.slider(
        "Select range of preferred bathrooms",
        min_value=1,
        max_value=get_max_bathrooms(cleaned_df),
        value=(1, 2),
        disabled=not consider_bathroom
    )    

districts = st.multiselect(
    'Preferred Arrondissement/District:', 
    options=cleaned_df['arrondissement'].unique(), 
    default=cleaned_df['arrondissement'].unique(), # Select all by default
    format_func=lambda option: f"{gdf_id_name_only[gdf_id_name_only['cartodb_id'] == option]['cartodb_id'].values[0]} ({gdf_id_name_only[gdf_id_name_only['cartodb_id'] == option]['name'].values[0]})"
)

metric_view = st.selectbox(
    "View based on?",
    options=('Count', 'Cost', 'Area Size'),
    help="This updates the visual color data shown on the map based on your preferences"
)

# Call the function to Filter data, All options to filter data should be made available before this step
filtered_df = process_merged_data(
    cleaned_df, 
    budget_range, 
    rent_or_buy, 
    min_max_rooms,
    consider_bedroom,
    min_max_bedrooms,
    consider_bathroom,
    min_max_bathroom,
    districts
)

st.divider()
# Create three columns for the KPI cards
with st.container():
    if not filtered_df.empty:
        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric(
                label="Total Properties Found",
                value=f"{len(filtered_df)}"
            )

        with col2:
            avg_rent = calculate_avg_rent_cost(filtered_df, rent_or_buy)
            st.metric(
                label=f"Average {rent_or_buy}",
                value=f"{avg_rent} euros" if avg_rent is not None else "N/A"
            )

        with col3:
            st.metric(
                label="Average size",
                value=f"{round(filtered_df['area'].mean())} sq. m."
            )
    else:
        st.warning("""
        ##### No properties found matching your criteria.
        ######  Please adjust your filters.
    """)

size_data = pd.DataFrame(filtered_df.groupby(['arrondissement']).size().reset_index())
size_data.rename(
    columns={0: 'count'},
    inplace=True
)
grouped_agg_data = filtered_df.groupby(['arrondissement']).agg({
    'rent/cost': ['mean'],
    'area': ['mean'],
    'rooms': ['min', 'max', 'mean'],
    'bedrooms': ['min', 'max', 'mean'],
    'bathroom': ['min', 'max']
})

grouped_agg_data.columns = ['_'.join(col).strip() for col in grouped_agg_data.columns.values]
result = pd.DataFrame(grouped_agg_data)
result = size_data.merge(result, how='inner', on='arrondissement', validate='one_to_one')
result = result.join(gdf_id_name_only.set_index('cartodb_id'), how='inner', on='arrondissement', validate='1:1')

map_data = update_color_map(metric_view)
fig = px.choropleth_mapbox(
  result,
  geojson=gj,
  color=map_data['metric'],
  locations='arrondissement',
  featureidkey='properties.cartodb_id',
  color_continuous_scale=map_data['color_scale'],
  range_color=(
    result[map_data['metric']].min(),  
    result[map_data['metric']].max()
    ),
  zoom=8,
  opacity=0.5,
  labels={
      'count': 'Matching Properties',
      'rent/cost_mean': 'Average Price (euros)',
      'area_mean': 'Average Area Size (m<sup>2</sup>)'
  },
  hover_name='name',
  hover_data={
    "count": True,
    "rent/cost_mean": ":,.2f",
    'area_mean': ":.2f"
  }
  )
fig.update_layout(
  mapbox_center={'lat': 48.8566, 'lon': 2.3522},
  margin={'r':0,'t':0,'l':0,'b':0}
)

if theme['backgroundColor'] == "#ffffff":
    fig.update_layout(mapbox_style="carto-positron")
if theme['backgroundColor'] == "#0e1117":
    fig.update_layout(mapbox_style='carto-darkmatter')

fig.update_mapboxes(
    bounds={
        'north': 48.931178068288375,
        'west': 2.1891149795072145,
        'south': 48.77780516767416,
        'east':2.5015673458389447
    }
)

st.plotly_chart(fig)

st.divider()

st.write("""
    ### Insights & Summary Statistics
""")
st.write("""
    - TO BE ADDED SOON
""")

# Display additional data about the filtered properties
# TODO: update dashboard according to PowerBI uttility?
# if not filtered_df.empty:
    # st.subheader('Top 5 options for you would be')
    # st.dataframe(filtered_df[:5])

    # Download button for filtered data
    # Generate a printable PDF file with necessary information about the properties
    # st.download_button(
    #     label='Download Filtered Data',
    #     data=filtered_df.to_csv(index=False),
    #     file_name='filtered_properties.csv',
    #     mime='text/csv',
    # )

    # Display summary statistics
    # Could generate an statistical numeric / Index to find out which would be the best option
    # Which one would have the most:- Size, Number of rooms, Lease Length at the least cost - Use this information to plot a scatter plot
    # Example from KF24 PG54
    # st.subheader('Summary Statistics')
    # st.write(result.describe())

    # Histogram of property prices
    
    # st.subheader('Price Distribution')
    # price_column = 'Cost' if rent_or_buy == 'Buy' else 'Rent'
    # fig_hist = px.histogram(filtered_df, x=price_column, nbins=20, title='Price Distribution')
    # st.plotly_chart(fig_hist)
st.sidebar.write("""
    #### Note
    - :warning: This app is a helpful tool to complement your search, but it's not a definitive guide for choosing the best property listings for your needs.
    
    #### Guide             
    - Use the filters at the top of the page to identify which districts (arrondisements) are most likely to
    contain your properties of choice
    - Hover on the :grey_question: symbol in each filter to know more about what that filter does
""")