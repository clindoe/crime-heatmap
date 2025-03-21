import streamlit as st
import pandas as pd
import folium
from folium.plugins import HeatMap

# Load crime dataset with coordinates
crime_data = pd.read_csv("Crime_By_City_With_Coordinates.csv")

# Load the full dataset for year & crime type filtering
full_crime_data = pd.read_csv("US_Crime_DataSet.csv", usecols=["City", "State", "Year", "Crime Type"])

# Sidebar Filters
st.sidebar.header("Crime Data Filters")
selected_year = st.sidebar.selectbox("Select Year", sorted(full_crime_data["Year"].unique(), reverse=True))
selected_crime_type = st.sidebar.selectbox("Select Crime Type", sorted(full_crime_data["Crime Type"].unique()))

# Filter the dataset based on selections
filtered_crime = full_crime_data[(full_crime_data["Year"] == selected_year) & (full_crime_data["Crime Type"] == selected_crime_type)]

# Count filtered crimes per city
filtered_crime_count = filtered_crime.groupby(["City", "State"]).size().reset_index(name="Crime Count")

# Merge with coordinates
filtered_crime_map = filtered_crime_count.merge(crime_data[["City", "State", "Latitude", "Longitude"]], on=["City", "State"], how="left")

# Drop rows with missing coordinates
filtered_crime_map = filtered_crime_map.dropna(subset=["Latitude", "Longitude"])

# Create a Folium map
m = folium.Map(location=[39.8283, -98.5795], zoom_start=5, tiles="cartodbpositron")

# Prepare heatmap data
heat_data = [
    [row["Latitude"], row["Longitude"], row["Crime Count"] / 100]
    for index, row in filtered_crime_map.iterrows()
]

# Add Heatmap Layer
HeatMap(heat_data, radius=20, blur=15, max_zoom=10).add_to(m)

# Add Circle Markers with popups
for index, row in filtered_crime_map.iterrows():
    folium.CircleMarker(
        location=[row["Latitude"], row["Longitude"]],
        radius=row["Crime Count"] / 500,
        color="red",
        fill=True,
        fill_color="red",
        fill_opacity=0.6,
        popup=folium.Popup(
            f"<b>City:</b> {row['City']}, {row['State']}<br>"
            f"<b>Crime Count:</b> {row['Crime Count']}<br>"
            f"<b>Crime Type:</b> {selected_crime_type}<br>"
            f"<b>Year:</b> {selected_year}",
            max_width=250,
        ),
    ).add_to(m)

# Display the map in Streamlit
st.header(f"Crime Heatmap for {selected_crime_type} in {selected_year}")
st.components.v1.html(m._repr_html_(), height=600)
