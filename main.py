import pandas as pd
import folium
from folium.plugins import HeatMap

# Load processed city-level crime data with coordinates
crime_data = pd.read_csv("Crime_By_City_With_Coordinates.csv")

# Load full crime dataset to calculate last 1-year crimes
full_crime_data = pd.read_csv("US_Crime_DataSet.csv", usecols=["City", "State", "Year"])

# Keep only last 1 year of data
latest_year = full_crime_data["Year"].max()
crime_last_year = full_crime_data[full_crime_data["Year"] == latest_year]

# Count crimes in last 1 year per city
last_year_counts = crime_last_year.groupby(["City", "State"]).size().reset_index(name="Crimes Last Year")

# Merge last year crimes with total crimes dataset
crime_data = crime_data.merge(last_year_counts, on=["City", "State"], how="left")
crime_data["Crimes Last Year"].fillna(0, inplace=True)  # Fill missing values with 0

# Define Safety Score (1 to 10) based on crime counts
def assign_safety_quality(total_crimes):
    if total_crimes < 100:
        return 10  # Very Safe
    elif total_crimes < 500:
        return 9
    elif total_crimes < 1000:
        return 8
    elif total_crimes < 3000:
        return 7
    elif total_crimes < 5000:
        return 6
    elif total_crimes < 8000:
        return 5
    elif total_crimes < 12000:
        return 4
    elif total_crimes < 18000:
        return 3
    elif total_crimes < 25000:
        return 2
    else:
        return 1  # Most Dangerous

# Apply Safety Score
crime_data["Safety Quality"] = crime_data["Crime Count"].apply(assign_safety_quality)

# Create a base map centered in the U.S.
m = folium.Map(location=[39.8283, -98.5795], zoom_start=5, tiles="cartodbpositron")

# Prepare heatmap data (Latitude, Longitude, Crime Count)
heat_data = [
    [row["Latitude"], row["Longitude"], row["Crime Count"] / 100]  # Normalize intensity
    for index, row in crime_data.iterrows()
]

# Add Heatmap Layer with better radius & intensity
HeatMap(heat_data, radius=20, blur=15, max_zoom=10).add_to(m)

# Add Circle Markers with improved popups
for index, row in crime_data.iterrows():
    folium.CircleMarker(
        location=[row["Latitude"], row["Longitude"]],
        radius=row["Crime Count"] / 500,  # Adjust size based on crime count
        color="red" if row["Safety Quality"] <= 3 else "orange" if row["Safety Quality"] <= 6 else "green",
        fill=True,
        fill_color="red" if row["Safety Quality"] <= 3 else "orange" if row["Safety Quality"] <= 6 else "green",
        fill_opacity=0.6,
        popup=folium.Popup(
            f"<b>City:</b> {row['City']}, {row['State']}<br>"
            f"<b>Total Crimes:</b> {row['Crime Count']}<br>"
            f"<b>Crimes Last Year:</b> {int(row['Crimes Last Year'])}<br>"
            f"<b>Safety Quality:</b> {row['Safety Quality']} (1 = Worst, 10 = Best)",
            max_width=250,
        ),
    ).add_to(m)

# Save the map
m.save("city_crime_heatmap.html")

print("✅ Enhanced city-level crime heatmap generated! Open 'city_crime_heatmap.html' in your browser.")
