import os
import streamlit as st
from streamlit_theme import st_theme
import pandas as pd
import plotly.express as px
import geopandas as gpd
from geojson import load
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from utils.map_settings import update_color_map
from utils.filter import clean_raw_data, process_merged_data
from utils.metrics import (
    calculate_avg_rent_cost_per_sqm,
    get_max_rentable, 
    get_max_housing,
    get_max_bedrooms,
    get_max_bathrooms
)
from utils.scam_algorithm import get_district_ci, calculate_scam_properties

# Directory pathing
curr_dir = os.path.dirname(__file__)
merged_dataset_path = os.path.relpath('./data/merged_dataset.xlsx', start=curr_dir)
geojson_path = os.path.relpath('./data/paris_arrondisements.geojson')

# Page configs
st.set_page_config(
    page_title="Main",
    layout="wide",
    page_icon="📈",
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
    options=('Price Ratio', 'Potential Scam Properties', 'Count', 'Cost', 'Area Size'),
    help="This updates the visual color data shown on the map based on your preferences"
)

district_ci_df = get_district_ci(cleaned_df, rent_or_buy)

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
filtered_df = calculate_scam_properties(filtered_df, district_ci_df)

# Create three columns for the KPI cards using HTML
with st.container():
    if not filtered_df.empty:
        col1, col2, col3 = st.columns(3)

        with col1:
            total_properties_found_html = f"""
            <div style="text-align: center; color: white; background-color: #90d08c; padding: 10px; border-radius: 10px;">
                <p style="font-size: 24px; margin: 0;"><strong>Total Properties Found</strong></p>
                <p style="font-size: 36px; margin: 0;">{len(filtered_df):,}</p>
            </div>
            """
            st.markdown(total_properties_found_html, unsafe_allow_html=True)

        with col2:
            avg_rentcost_ratio = calculate_avg_rent_cost_per_sqm(filtered_df)

            avg_rentcost_ratio_html = f"""
            <div style="text-align: center; color: white; background-color: #90d08c; padding: 10px; border-radius: 10px;">
                <p style="font-size: 24px; margin: 0;"><strong>Average {rent_or_buy} per Area</strong></p>
                <p style="font-size: 36px; margin: 0;">{'€' + str(avg_rentcost_ratio) + '/m²' if avg_rentcost_ratio is not None else 'N/A'}</p>
            </div>
            """
            st.markdown(avg_rentcost_ratio_html, unsafe_allow_html=True)

        with col3:

            avg_area = filtered_df['area'].mean()

            avg_size_html = f"""
            <div style="text-align: center; color: white; background-color: #90d08c; padding: 10px; border-radius: 10px;">
                <p style="font-size: 24px; margin: 0;"><strong>Average Area</strong></p>
                <p style="font-size: 36px; margin: 0;">{f'{avg_area:.2f} m²'}</p>
            </div>
            """
            st.markdown(avg_size_html, unsafe_allow_html=True)
    else:
        st.warning("""
        ##### No properties found matching your criteria.
        ######  Please adjust your filters.
    """)        

st.write('######')

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
    'bathroom': ['min', 'max'],
    'price/sqm': ['min', 'max', 'mean'],
    'potential_scam_property': ['sum', lambda x: x.mean()]
})
grouped_agg_data.columns = [
    'rent/cost_mean',
    'area_mean',
    'rooms_min', 'rooms_max', 'rooms_mean',
    'bedrooms_min', 'bedrooms_max', 'bedrooms_mean',
    'bathroom_min', 'bathroom_max',
    'price/sqm_min', 'price/sqm_max', 'price/sqm_mean',
    'potential_scam_count', 'potential_scam_proportion'
]

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
      'price/sqm_mean': 'Average Price per Area (€/m<sup>2</sup>)',
      'rent/cost_mean': 'Average Price (€)',
      'area_mean': 'Average Area Size (m<sup>2</sup>)',
      'price/sqm_min': 'Highest Price per Area (€/m<sup>2</sup>)',
      'price/sqm_max': 'Lowest Price per Area (€/m<sup>2</sup>)',
      'potential_scam_count': 'Potential Scam Properties',
      'potential_scam_proportion': 'Scam Proportion'
  },
  hover_name='name',
  hover_data={
    "count": True,
    "price/sqm_mean": ":,.2f",
    "rent/cost_mean": ":,.2f",
    'area_mean': ":.2f",
    'price/sqm_min': ':,.2f',
    'price/sqm_max': ':,.2f',
    'potential_scam_count': True,
    'potential_scam_proportion': ':.3f'
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

with st.container():
    col1, col2, col3 = st.columns(3)
    with col1:
        scam_properties_html = f"""
        <div style="text-align: center; color: white; background-color: #ac1111; padding: 10px; border-radius: 10px;">
            <p style="font-size: 20px; margin: 0;"><strong>Potential Scam Properties</strong></p>
            <p style="font-size: 36px; margin: 0;">{filtered_df['potential_scam_property'].sum()}</p>
        </div>"""
        st.markdown(scam_properties_html, unsafe_allow_html=True)

st.divider()

st.write("""
    ### Insights & Summary Statistics
""")


# Define a dictionary to map metric_view options to corresponding DataFrame columns
metric_columns = {
    'Potential Scam Properties': 'potential_scam_property',
    'Price Ratio': 'price/sqm',
    'Count': None, 
    'Cost': 'rent/cost', 
    'Area Size': 'area'  
}

# Select the appropriate column based on metric_view
selected_metric = metric_columns[metric_view]

# Group by arrondissement and calculate mean and standard error of mean
if metric_view == 'Count':
    grouped_df = filtered_df.groupby('arrondissement').size().reset_index(name='count')
    y_data = grouped_df['count']
    error_y = None
    y_axis_title = 'Count'
elif metric_view == 'Potential Scam Properties':
    grouped_df = filtered_df.groupby('arrondissement')[selected_metric].agg(['count', lambda x: x.mean(), 'sem']).reset_index()
    grouped_df.columns = ['arrondissement', 'count', 'proportion', 'sem']
    y_data = grouped_df['proportion']
    error_y = dict(type='data', array=grouped_df['sem'], visible=True)
    y_axis_title = "Percent Potential Scams per District (%)"
else:
    grouped_df = filtered_df.groupby('arrondissement')[selected_metric].agg(['mean', 'sem']).reset_index()
    grouped_df.columns = ['arrondissement', 'mean', 'sem']
    y_data = grouped_df['mean']
    error_y = dict(type='data', array=grouped_df['sem'], visible=True)
    y_axis_title = f'Average {metric_view}'

# Create bar chart with error bars
fig = go.Figure()

fig.add_trace(
    go.Bar(
        x=grouped_df['arrondissement'],
        y=y_data,
        name=y_axis_title,
        marker_color='#90d08c',
        error_y=error_y
    )
)

# Update layout
fig.update_layout(
    title=f'{y_axis_title} by Arrondissement',
    xaxis_title='Arrondissement',
    yaxis_title=y_axis_title,
    font=dict(color='white'),
    xaxis=dict(
        tickcolor='white',
        tickfont=dict(color='white', size=14)
    ),
    yaxis=dict(
        tickcolor='white',
        tickfont=dict(color='white', size=14)
    ),
    title_font=dict(size=24),
    xaxis_title_font=dict(size=18),
    yaxis_title_font=dict(size=18),
)

st.plotly_chart(fig)

# Define a dictionary for the boxplots
boxplot_columns = {
    'Potential Scam Properties': 'potential_scam_property',
    'Price Ratio': 'price/sqm',
    'Cost': 'rent/cost',
    'Area Size': 'area'
}

# Select the appropriate column based on metric_view
if metric_view == 'Potential Scam Properties':
    grouped_df = filtered_df[['rooms', 'arrondissement', 'potential_scam_property']].groupby('rooms').sum().reset_index()
    y_data = grouped_df['potential_scam_property']
    y_axis_title = f'{metric_view}'
elif metric_view != 'Count':
    selected_metric = metric_columns[metric_view]
    y_data = filtered_df[selected_metric]
    y_axis_title = f'{metric_view}'
else:
    # For 'Count', we'll need to handle it differently
    grouped_df = filtered_df.groupby('rooms').size().reset_index(name='count')
    y_data = grouped_df['count']
    y_axis_title = 'Count'

# Create the figure
fig = go.Figure()

if metric_view not in ['Count', 'Potential Scam Properties']:
    # Add box plot for selected metric vs. Rooms
    fig.add_trace(
        go.Box(
            y=y_data,
            x=filtered_df['rooms'],
            name=y_axis_title,
            marker_color='#90d08c',
            boxmean='sd'
        )
    )
else:
    # For 'Count', we'll use a bar plot instead of a box plot
    fig.add_trace(
        go.Bar(
            y=y_data,
            x=grouped_df['rooms'],
            name='Count',
            marker_color='#90d08c'
        )
    )

# Update layout with dark background and white text
fig.update_layout(
    title_text=f'{y_axis_title} by Number of Rooms',
    font=dict(color='white'),
    xaxis_title='Number of Rooms',
    yaxis_title=y_axis_title,
    xaxis=dict(
        tickcolor='white',
        tickfont=dict(color='white', size=14)
    ),
    yaxis=dict(
        tickcolor='white',
        tickfont=dict(color='white', size=14)
    ),
    title_font=dict(size=24),
    xaxis_title_font=dict(size=18),
    yaxis_title_font=dict(size=18),
)

st.plotly_chart(fig)


st.write("""
    #### Distribution of Price and Area
""")

# Display charts with adjusted ratios
col1, col2 = st.columns(2)  # 2/3 for bar chart, 1/3 for donut chart

with col1:
    # Determine the column to use based on the user's choice
    column_to_use = 'rent' if rent_or_buy == 'Rent' else 'cost'

    # Create the histogram based on the selected column
    fig1 = px.histogram(filtered_df, x=filtered_df[column_to_use], nbins=15)

    fig1.update_layout(
        xaxis_title="Price (€)",
        yaxis_title="Number of Properties",
        font=dict(color='white'),
        xaxis_title_font=dict(size=18),
        yaxis_title_font=dict(size=18),
        height = 300
    )

    # Update the color of the histogram bars
    fig1.update_traces(
        marker=dict(color='#90d08c')  # Set the color of the bars
    )

    st.plotly_chart(fig1)  

with col2:
    fig2 = px.histogram(filtered_df, x=filtered_df['area'], nbins=15)

    fig2.update_layout(
        xaxis_title="Area (m²)",
        yaxis_title="Number of Properties",
        font=dict(color='white'),
        xaxis_title_font=dict(size=18),
        yaxis_title_font=dict(size=18),
        height = 300
    )

    # Update the color of the histogram bars
    fig2.update_traces(
        marker=dict(color='#90d08c')  # Set the color of the bars
    )

    st.plotly_chart(fig2)



# Group by rooms and calculate mean for bedrooms and bathrooms
grouped_df = filtered_df.groupby('rooms').agg({
    'bedrooms': 'mean',
    'bathroom': 'mean'
}).reset_index()

# Sort by number of rooms
grouped_df = grouped_df.sort_values('rooms')

# Create the figure
fig = go.Figure()

# Add trace for bedrooms if checkbox is checked
if consider_bedroom:
    fig.add_trace(go.Scatter(
        x=grouped_df['rooms'],
        y=grouped_df['bedrooms'],
        mode='lines+markers',
        name='Bedrooms',
        line=dict(color='#90d08c', width=2, shape='spline', smoothing=1.3),
        marker=dict(size=8, color='#90d08c'),
        fill='tozeroy',
        fillcolor='rgba(144, 208, 140, 0.3)'
    ))

# Add trace for bathrooms if checkbox is checked
if consider_bathroom:
    fig.add_trace(go.Scatter(
        x=grouped_df['rooms'],
        y=grouped_df['bathroom'],
        mode='lines+markers',
        name='Bathrooms',
        line=dict(color='#5d8aa8', width=2, shape='spline', smoothing=1.3),
        marker=dict(size=8, color='#5d8aa8'),
        fill='tozeroy',
        fillcolor='rgba(93, 138, 168, 0.3)'
    ))

# Update layout
fig.update_layout(
    title='Average Number of Bedrooms and Bathrooms by Total Rooms',
    xaxis_title='Total Number of Rooms',
    yaxis_title='Average Number',
    paper_bgcolor='#0E1117',
    plot_bgcolor='#0E1117',
    font=dict(color='white'),
    xaxis=dict(
        tickcolor='white',
        tickfont=dict(color='white', size=12),
        title_font=dict(size=14),
        tickmode='array',
        tickvals=grouped_df['rooms'],
        ticktext=[f'{i}' for i in grouped_df['rooms']]
    ),
    yaxis=dict(
        tickcolor='white',
        tickfont=dict(color='white', size=12),
        title_font=dict(size=14)
    ),
    legend=dict(
        font=dict(color='white', size=12),
        bgcolor='rgba(0,0,0,0)'
    ),
    title_font=dict(size=20),
    hovermode='x unified'
)

# Add custom hover template
fig.update_traces(
    hovertemplate="<b>Total Rooms: %{x}</b><br>" +
                  "Average: %{y:.2f}<br>" +
                  "<extra></extra>"
)

# Display the plot in Streamlit only if at least one of bedroom or bathroom is considered
if consider_bedroom or consider_bathroom:
    st.plotly_chart(fig)
else:
    st.write("Please select at least one of 'Prefer unique bedrooms?' or 'Consider bathroom/s?' to display the graph for bedroom/bathroom.")

st.sidebar.write("""
    #### Note
    - :warning: This app is a helpful tool to complement your search, but it's not a definitive guide for choosing the best property listings for your needs.
    
    #### Guide             
    - Use the filters at the top of the page to identify which districts (arrondisements) are most likely to
    contain your properties of choice
    - Hover on the :grey_question: symbol in each filter to know more about what that filter does
""")