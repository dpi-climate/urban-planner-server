import csv
import json

# Input CSV file and desired output GeoJSON file
csv_file = './files/alt_fuel_stations_Aug_26_2024.csv'
geojson_file = './files/alt_fuel_stations.geojson'

# Prepare a list to hold all GeoJSON features
features = []

# Read the CSV file
with open(csv_file, 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    
    for row in reader:
        # Extract latitude, longitude, and station name from each row
        lat = float(row['Latitude'])
        lon = float(row['Longitude'])
        station_name = row['Station Name']
        
        # Create a GeoJSON feature for each row
        feature = {
            "type": "Feature",
            "geometry": {
                "type": "Point",
                "coordinates": [lon, lat]  # GeoJSON expects [longitude, latitude]
            },
            "properties": {
                "Station Name": station_name
            }
        }
        features.append(feature)

# Create a FeatureCollection
feature_collection = {
    "type": "FeatureCollection",
    "features": features
}

# Write out the GeoJSON file
with open(geojson_file, 'w', encoding='utf-8') as f:
    json.dump(feature_collection, f, ensure_ascii=False, indent=2)

print(f"GeoJSON file has been created: {geojson_file}")
