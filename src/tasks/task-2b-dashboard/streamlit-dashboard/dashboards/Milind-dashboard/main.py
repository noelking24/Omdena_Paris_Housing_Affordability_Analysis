import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px

# Function to filter data
def filter_data(df, price_range, min_nights, max_nights, room_types, neighbourhoods, min_availability, max_availability, min_reviews, max_reviews, checkin_date, availability, license_filter):
    filtered_data = df[(df['price'] >= price_range[0]) & (df['price'] <= price_range[1])]
    
    if room_types:
        filtered_data = filtered_data[filtered_data['room_type'].isin(room_types)]
        
    if neighbourhoods:
        filtered_data = filtered_data[filtered_data['neighbourhood'].isin(neighbourhoods)]
        
    filtered_data = filtered_data[(filtered_data['availability_365'] >= min_availability) & (filtered_data['availability_365'] <= max_availability)]
    
    if license_filter:
        filtered_data = filtered_data[filtered_data['license'].notnull()]
    
    return filtered_data

# Paths for data
listings_path = 'C:/Users/ACER/Desktop/Milind-dashboard/data/listings.csv'
neighbourhoods_path = 'C:/Users/ACER/Desktop/Milind-dashboard/data/neighbourhoods.csv'

# Load data
df_listings = pd.read_csv(listings_path)
df_neighbourhoods = pd.read_csv(neighbourhoods_path)

# Merge data
df = pd.merge(df_listings, df_neighbourhoods, on=['neighbourhood_group', 'neighbourhood'], how='left')

# Sidebar for user inputs
st.sidebar.header('Please Provide Your Preferences')

# Price range slider
price_range = st.sidebar.slider(
    'Select your price range (in euros):', 
    min_value=0, 
    max_value=1000, 
    value=(50, 500),  # Default Range
    step=10  # Increase by 10 Euros
)

# Minimum and maximum nights slider
min_nights = st.sidebar.slider('Minimum Number of Nights:', 0, 365, 1)
max_nights = st.sidebar.slider('Maximum Number of Nights:', 1, 365, 7)

# Room type preference
room_types = st.sidebar.multiselect(
    'Preferred Room Type:', 
    options=df['room_type'].unique(), 
    default=df['room_type'].unique()  # Select all by default
)

# Neighbourhood preference
neighbourhoods = st.sidebar.multiselect(
    'Preferred Neighbourhood:', 
    options=df['neighbourhood'].unique(), 
    default=df['neighbourhood'].unique()  # Select all by default
)

# Additional filters
availability = st.sidebar.slider('Minimum Availability (days/year):', 0, 365, 0)
license_filter = st.sidebar.checkbox('Show only licensed properties')

# Call the function to filter data
filtered_df = filter_data(
    df, 
    price_range, 
    min_nights, 
    max_nights, 
    room_types, 
    neighbourhoods, 
    0,  # min_availability
    1000,  # max_availability
    0.0,  # min_reviews
    1000,  # max_reviews
    pd.to_datetime('2023-01-01'),  # checkin_date
    availability, 
    license_filter
)

# Analysis Section
st.title("Paris Property Listings Data Dashboard")

# 1. Map Visualization of Properties
st.subheader('Map of Properties:')
fig_map = go.Figure()

# Color map for room types
color_map = {
    'Entire home/apt': '#1f77b4',
    'Private room': '#ff7f0e',
    'Shared room': '#2ca02c'
}

# Add scatter plot on map
fig_map.add_trace(go.Scattermapbox(
    lat=filtered_df['latitude'],
    lon=filtered_df['longitude'],
    mode='markers',
    marker=dict(
        size=10,
        color=[color_map.get(rt, '#dcdcdc') for rt in filtered_df['room_type']],
        opacity=0.8
    ),
    text=filtered_df.apply(lambda row: 
        f"Name: {row['name']}<br>"
        f"Price: €{row['price']:.2f}<br>"
        f"Room Type: {row['room_type']}<br>"
        f"Neighbourhood: {row['neighbourhood']}<br>"
        f"Minimum Nights: {row['minimum_nights']}<br>"
        f"Availability: {row['availability_365']} days/year<br>"
        f"License: {row['license'] if pd.notna(row['license']) else 'Not Available'}",
        axis=1),
    hoverinfo='text'
))

fig_map.update_layout(
    mapbox=dict(
        style="open-street-map",
        center=dict(lat=filtered_df['latitude'].mean(), lon=filtered_df['longitude'].mean()),
        zoom=12
    ),
    margin=dict(t=0, b=0, l=0, r=0),
    title='Property Locations'
)

st.plotly_chart(fig_map, use_container_width=True)

# 2. Summary Statistics
st.subheader('Summary Statistics')
st.write(filtered_df.describe())

# 3. Distribution of Prices
st.subheader('Price Distribution')
fig_price_dist = px.histogram(filtered_df, x='price', nbins=30, title='Distribution of Property Prices', labels={'price': 'Price (in euros)'})
st.plotly_chart(fig_price_dist, use_container_width=True)

# 4. Average Price by Room Type
st.subheader('Average Price by Room Type')
avg_price_by_room = filtered_df.groupby('room_type')['price'].mean().reset_index()
fig_avg_price = px.bar(avg_price_by_room, x='room_type', y='price', title='Average Price by Room Type', labels={'room_type': 'Room Type', 'price': 'Average Price (in euros)'}, color='room_type')
st.plotly_chart(fig_avg_price, use_container_width=True)

# 5. Price Heatmap by Neighbourhood
st.subheader('Price Heatmap by Neighbourhood')
fig_price_heatmap = px.density_mapbox(filtered_df, lat='latitude', lon='longitude', z='price', radius=10, center=dict(lat=filtered_df['latitude'].mean(), lon=filtered_df['longitude'].mean()), zoom=12, title='Price Heatmap by Neighbourhood', mapbox_style="open-street-map")
st.plotly_chart(fig_price_heatmap, use_container_width=True)

# 6. Top 10 Neighbourhoods by Number of Listings
st.subheader('Top 10 Neighbourhoods by Number of Listings')
top_neighbourhoods = filtered_df['neighbourhood'].value_counts().head(10).reset_index()
top_neighbourhoods.columns = ['Neighbourhood', 'Number of Listings']
fig_top_neigh = px.bar(top_neighbourhoods, x='Neighbourhood', y='Number of Listings', title='Top 10 Neighbourhoods by Number of Listings', labels={'Number of Listings': 'Number of Listings'})
st.plotly_chart(fig_top_neigh, use_container_width=True)

# 7. Availability Distribution
st.subheader('Availability Distribution')
fig_avail_dist = px.histogram(filtered_df, x='availability_365', nbins=30, title='Distribution of Property Availability', labels={'availability_365': 'Availability (days/year)'})
st.plotly_chart(fig_avail_dist, use_container_width=True)

# 8. Price vs Availability Scatter Plot
st.subheader('Price vs Availability Scatter Plot')
fig_price_vs_avail = px.scatter(filtered_df, x='availability_365', y='price', color='room_type', title='Price vs Availability', labels={'availability_365': 'Availability (days/year)', 'price': 'Price (in euros)'})
st.plotly_chart(fig_price_vs_avail, use_container_width=True)

# 9. Price Distribution by Neighbourhood
st.subheader('Price Distribution by Neighbourhood')
fig_price_by_neigh = px.box(filtered_df, x='neighbourhood', y='price', title='Price Distribution by Neighbourhood', labels={'neighbourhood': 'Neighbourhood', 'price': 'Price (in euros)'})
st.plotly_chart(fig_price_by_neigh, use_container_width=True)

# 10. Availability vs Minimum Nights Scatter Plot
st.subheader('Availability vs Minimum Nights Scatter Plot')
fig_avail_vs_min_nights = px.scatter(filtered_df, x='minimum_nights', y='availability_365', color='room_type', title='Availability vs Minimum Nights', labels={'minimum_nights': 'Minimum Nights', 'availability_365': 'Availability (days/year)'})
st.plotly_chart(fig_avail_vs_min_nights, use_container_width=True)


# 13. Cheap to Costly Neighbourhoods
st.subheader('Neighbourhoods from Cheapest to Most Expensive')
avg_price_by_neigh = filtered_df.groupby('neighbourhood')['price'].mean().sort_values().reset_index()
fig_avg_price_by_neigh = px.bar(avg_price_by_neigh, x='neighbourhood', y='price', title='Neighbourhoods from Cheapest to Most Expensive', labels={'neighbourhood': 'Neighbourhood', 'price': 'Average Price (in euros)'})
st.plotly_chart(fig_avg_price_by_neigh, use_container_width=True)
