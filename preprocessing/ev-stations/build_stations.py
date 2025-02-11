import pandas as pd
import geopandas as gpd
import pickle
import csv
import json
from consts import raw_files_dir, processed_files_dir

def stations_to_pickle():
    csv_file = f'{raw_files_dir}/alt_fuel_stations_Aug_26_2024.csv'
    pickle_file = f'{processed_files_dir}/ev-stations/alt_fuel_stations_geodf.pkl'

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

def stations_to_geojson_one_file(station_type):
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
                    "Station Name": station_name,
                    "Type": station_type
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

import json
import csv

def stations_to_geojson(csv_file, station_type):
    features = []

    # Read the CSV file
    with open(csv_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
    
        for row in reader:
            lat = float(row['Latitude'])
            lon = float(row['Longitude'])
            station_name = row['Station Name']
            
            # Create a GeoJSON feature and add the type property
            feature = {
                "type": "Feature",
                "geometry": {
                    "type": "Point",
                    "coordinates": [lon, lat]
                },
                "properties": {
                    "Station Name": station_name,
                    "Type": station_type
                }
            }
            features.append(feature)

    return features


if __name__ == "__main__":
    # # csv_file = f'{raw_files_dir}/alt_fuel_stations_Aug_26_2024.csv'
    # # geojson_file = f'{processed_files_dir}/ev-stations/alt_fuel_stations.geojson'

    # # Biodiesel
    # csv_file = f'{raw_files_dir}/biodiesel_Feb_11_2025.csv'
    # geojson_file = f'{processed_files_dir}/ev-stations/biodiesel_Feb_11_2025.geojson'

    # stations_to_geojson("biodiesel")

    # # Electric
    # csv_file = f'{raw_files_dir}/electric_Feb_11_2025.csv'
    # geojson_file = f'{processed_files_dir}/ev-stations/electric_Feb_11_2025.geojson'

    # stations_to_geojson("electric")

    # # Ethanol
    # csv_file = f'{raw_files_dir}/ethanol_Feb_11_2025.csv'
    # geojson_file = f'{processed_files_dir}/ev-stations/ethanol_Feb_11_2025.geojson'

    # stations_to_geojson("ethanol")

    # # Liquefied Natural Gas
    # csv_file = f'{raw_files_dir}/liquefied_natural_gas_Feb_11_2025.csv'
    # geojson_file = f'{processed_files_dir}/ev-stations/liquefied_natural_gas_Feb_11_2025.geojson'

    # stations_to_geojson("lng")

    # # Liquefied Petroleum Gas
    # csv_file = f'{raw_files_dir}/liquefied_petroleum_gas_Feb_11_2025.csv'
    # geojson_file = f'{processed_files_dir}/ev-stations/liquefied_petroleum_gas_Feb_11_2025.geojson'

    # stations_to_geojson("lpg")

    # # Compressed Natural Gas
    # csv_file = f'{raw_files_dir}/compressed_natural_gas_Feb_11_2025.csv'
    # geojson_file = f'{processed_files_dir}/ev-stations/compressed_natural_gas_Feb_11_2025.geojson'

    # stations_to_geojson("cng")

    ####################################################################################################

    # Merge
    station_types = {
        'biodiesel': 'biodiesel_Feb_11_2025.csv',
        'electric': 'electric_Feb_11_2025.csv',
        'ethanol': 'ethanol_Feb_11_2025.csv',
        'lng': 'liquefied_natural_gas_Feb_11_2025.csv',
        'lpg': 'liquefied_petroleum_gas_Feb_11_2025.csv',
        'cng': 'compressed_natural_gas_Feb_11_2025.csv'
    }

    all_features = []

    # Generate features for each station type
    for station_type, filename in station_types.items():
        csv_file = f'{raw_files_dir}/{filename}'
        features = stations_to_geojson(csv_file, station_type)
        all_features.extend(features)

    # Create a final GeoJSON FeatureCollection
    merged_geojson = {
        "type": "FeatureCollection",
        "features": all_features
    }

    # Write the merged GeoJSON to a file
    output_file = f'{processed_files_dir}/ev-stations/merged_stations_Feb_11_2025.geojson'
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(merged_geojson, f, ensure_ascii=False, indent=2)

    print(f"Merged GeoJSON file has been created: {output_file}")
