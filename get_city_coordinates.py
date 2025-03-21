import pandas as pd

# Load city-level crime data
crime_data = pd.read_csv("Crime_By_City.csv")

# Load U.S. city coordinates dataset (from uscities.csv)
city_coords = pd.read_csv("uscities.csv", usecols=["city", "state_name", "lat", "lng"])

# Standardize column names to match
city_coords.rename(columns={"city": "City", "state_name": "State", "lat": "Latitude", "lng": "Longitude"}, inplace=True)

# Merge crime data with coordinates (left join to keep only matched cities)
crime_data = crime_data.merge(city_coords, on=["City", "State"], how="left")

# Drop rows where coordinates are missing
crime_data = crime_data.dropna(subset=["Latitude", "Longitude"])

# Save updated dataset with coordinates
crime_data.to_csv("Crime_By_City_With_Coordinates.csv", index=False)

print("✅ City crime data merged with coordinates and saved as 'Crime_By_City_With_Coordinates.csv'")
