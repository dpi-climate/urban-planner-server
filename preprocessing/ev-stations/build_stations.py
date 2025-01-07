import pandas as pd
import geopandas as gpd
import pickle
import csv
import json
from consts import raw_files_dir, ev_files_dir

def stations_to_pickle():
    csv_file = f'./{raw_files_dir}/alt_fuel_stations_Aug_26_2024.csv'
    pickle_file = f'./{ev_files_dir}/alt_fuel_stations_geodf.pkl'

    # Read CSV into a DataFrame
    df = pd.read_csv(csv_file)

    # Create geometry from longitude and latitude
    geometry = gpd.points_from_xy(df['Longitude'], df['Latitude'])

    # Create a GeoDataFrame
    gdf = gpd.GeoDataFrame(df, geometry=geometry)

    # Now pickle this GeoDataFrame
    with open(pickle_file, 'wb') as p:
        pickle.dump(gdf, p)

    print(f"Pickle file with geometry created: {pickle_file}")

def stations_to_geojson():
    
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
