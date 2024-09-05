#This dashboard is made from the cleaned dataset Paris_housing_index_cleaned.csv
#Suggested modifications - Extract the postal code/zip code from the latitude and longitude data to enable users to easily filter properties for specific arrondissements.
#Suggested visualizations - Bar chart for avg rent/sale prices per arrondissements

import streamlit as st
import pandas as pd
import plotly.express as px

# Load data
@st.cache_data
def load_data():
    df = pd.read_csv('task-2a-data-analysis/Cleaned_datasets/Paris_housing_index_cleaned.csv')
    df = df.drop(columns=['id'], errors='ignore')  
    return df

df = load_data()

# Title and description
st.title("Housing Affordability in Paris")
st.write("""
This dashboard allows you to analyze housing affordability in Paris based on various factors such as room type, person capacity, cleanliness rating, and more.
""")

# Sidebar for filtering
st.sidebar.header("Filter Options")

# Filter by room type
room_type = st.sidebar.multiselect(
    "Select Room Type",
    options=df["room_type"].unique(),
    default=df["room_type"].unique()
)

host_status = st.sidebar.radio(
    "Select Host Status",
    options=["All"] + list(df["host_status"].unique()),
    index=0
)

# Filter by room sharing
room_sharing = st.sidebar.radio(
    "Select Room Sharing",
    options=["All"] + list(df["room_sharing"].unique()),
    index=0
)

# Filter by room private
room_private = st.sidebar.radio(
    "Select Room Private",
    options=["All"] + list(df["room_private"].unique()),
    index=0
)

# Filter by person capacity
person_capacity = st.sidebar.slider(
    "Select Person Capacity",
    min_value=int(df["person_capacity"].min()),
    max_value=int(df["person_capacity"].max()),
    value=(int(df["person_capacity"].min()), int(df["person_capacity"].max()))
)

# Filter by budget range
price_range = st.sidebar.slider(
    "Select Budget Range (Price in Euros)",
    min_value=int(df["price"].min()),
    max_value=int(df["price"].max()),
    value=(int(df["price"].min()), int(df["price"].max()))
)

# Apply filters
filtered_df = df[
    (df["room_type"].isin(room_type)) &
    (df["person_capacity"] >= person_capacity[0]) &
    (df["person_capacity"] <= person_capacity[1]) &
    (df["price"] >= price_range[0]) &
    (df["price"] <= price_range[1])
]
     
if host_status != "All":
    filtered_df = filtered_df[filtered_df["host_status"] == host_status]

if room_sharing != "All":
    filtered_df = filtered_df[filtered_df["room_sharing"] == room_sharing]

if room_private != "All":
    filtered_df = filtered_df[filtered_df["room_private"] == room_private]

# Number of properties
st.subheader(f"Number of Available Properties: {filtered_df.shape[0]}")

# KPIs
col1, col2, col3 = st.columns(3)
with col1:
    avg_price = filtered_df["price"].mean()
    st.metric(label="Average Price", value=f"€{avg_price:.2f}")

with col2:
    avg_cleanliness = filtered_df["cleanliness_rating"].mean()
    st.metric(label="Average Cleanliness Rating", value=f"{avg_cleanliness:.2f}")

with col3:
    avg_satisfaction = filtered_df["guest_satisfaction_rating"].mean()
    st.metric(label="Average Satisfaction Rating", value=f"{avg_satisfaction:.2f}")

# Map of listings
st.header("Map of Listings")
map_fig = px.scatter_mapbox(
    filtered_df,
    lat="latitude",
    lon="longitude",
    color="room_type",
    size="person_capacity",
    hover_name="room_type",
    hover_data=["price", "cleanliness_rating", "guest_satisfaction_rating"],
    zoom=10,
    height=600,
    title="Map of Listings"
)
map_fig.update_layout(mapbox_style="open-street-map")
st.plotly_chart(map_fig)

# Top 5 properties based on customer ratings
st.subheader("Top 5 Properties Based on Customer Ratings")
top_5_properties = filtered_df.nlargest(5, 'guest_satisfaction_rating').reset_index(drop=True)
st.dataframe(top_5_properties)


# Scatter plot
st.subheader("Price vs. Other Factors")
factor = st.selectbox(
    "Select Factor to Compare with Price",
    options=["cleanliness_rating", "guest_satisfaction_rating", "bedrooms", "dist_city", "dist_metro", "attr_index", "attr_index_norm", "rest_index", "rest_index_norm"]
)
price_scatter = px.scatter(filtered_df, x=factor, y="price", title=f"Price vs. {factor}")
st.plotly_chart(price_scatter)


