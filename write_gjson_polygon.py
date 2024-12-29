import numpy as np
import json
import geopandas as gpd
from shapely.geometry import Point
from consts import files_path, binary_data_dir
import pickle
import os
from collections import defaultdict

def build_threshold_rgba(a, C):
    # Bins normalized between 0 and 1
    norm = [(float(i) - min(a)) / (max(a) - min(a)) for i in a]

    # Generate the desired output format
    output = []

    for value, color in zip(a, C):
        rgba_color = (int(color[0]), int(color[1]), int(color[2]), 255)
        output.append({"value": value, "color": rgba_color})

    return output

def get_color_for_value(var_threshold, value):
    """
    Given a value and a list of thresholds, return the corresponding color.
    If the value is non-numeric, return a fully transparent color.
    If the value is below the first threshold, return the first color.
    If the value is above the last threshold, return the last color.
    """
    if not isinstance(value, (int, float)) or value == 0:
        # Fully transparent
        return (0, 0, 0, 0)

    for threshold in var_threshold:
        if value <= threshold["value"]:
            return threshold["color"]
    # If value exceeds all var_threshold, return the last color
    return var_threshold[-1]["color"]

def process_files_geojson(files, tracts_gdf, feature_id):
    """
    Process each variable file to compute average values by census tract and output as GeoJSON.
    """

    # Directory to save processed GeoJSON files
    os.makedirs(binary_data_dir, exist_ok=True)  # Create the directory if it doesn't exist

    for file in files:
        var_name = file["var_name"]
        file_path = file["path"]

        print(var_name)

        # Open and load the GeoJSON file using geopandas
        try:
            points_gdf = gpd.read_file(file_path)
        except FileNotFoundError:
            print(f"File not found: {file_path}. Skipping {var_name}.")
            continue
        except Exception as e:
            print(f"Error loading {file_path}: {e}. Skipping {var_name}.")
            continue

        # Ensure the GeoDataFrame has a geometry column
        if points_gdf.empty or 'geometry' not in points_gdf:
            print(f"No geometry found in {file_path}. Skipping {var_name}.")
            continue

        # Ensure CRS matches between points and tracts
        if points_gdf.crs != tracts_gdf.crs:
            points_gdf = points_gdf.to_crs(tracts_gdf.crs)

        # Extract all years from the properties
        # Assuming year properties are all keys that are purely digits
        sample_properties = points_gdf.iloc[0].drop(labels='geometry').to_dict()
        years = sorted([key for key in sample_properties.keys() if key.isdigit()])

        if not years:
            print(f"No year properties found in {file_path}. Skipping {var_name}.")
            continue

        print(f"Processing variable '{var_name}' for years: {', '.join(years)}")

        for year in years:
            # Select the value column for the current year
            if year not in points_gdf.columns:
                print(f"Year '{year}' not found in {file_path}. Skipping year.")
                continue

            # Create a GeoDataFrame with only necessary columns
            df_year = points_gdf[['geometry', year]].copy()
            df_year = df_year.dropna(subset=[year])

            # Spatial join with tracts to assign each point to a tract
            try:
                joined = gpd.sjoin(df_year, tracts_gdf, how='inner', predicate='within')
            except Exception as e:
                print(f"Error during spatial join for {var_name} {year}: {e}")
                continue

            # Group by tract and compute average
            grouped = joined.groupby(feature_id)[year].mean().reset_index()
            grouped.rename(columns={year: 'average_value'}, inplace=True)

            # Assign colors based on average values
            grouped['color'] = grouped['average_value'].apply(lambda x: get_color_for_value(file["threshold"], x))

            # Merge with tracts_gdf to get geometries
            grouped = grouped.merge(tracts_gdf[[feature_id, 'geometry']], on=feature_id, how='left')

            # Convert to GeoDataFrame
            geojson_gdf = gpd.GeoDataFrame(grouped, geometry='geometry')

            # Define properties for GeoJSON
            geojson_gdf['color'] = geojson_gdf['color'].apply(lambda c: f"rgba({c[0]}, {c[1]}, {c[2]}, {c[3]})")
            geojson_gdf = geojson_gdf[[feature_id, 'average_value', 'color', 'geometry']]

            # Define the filename
            filename = f"ct_{var_name}_{year}.geojson"
            filepath = os.path.join(binary_data_dir, filename)

            # Save to GeoJSON
            try:
                geojson_gdf.to_file(filepath, driver='GeoJSON')
                print(f"Saved GeoJSON data for {var_name} {year} to {filepath}")
            except IOError as e:
                print(f"Failed to save GeoJSON data to {filepath}: {e}")

# Define thresholds and colors as in your original code
start, end, n = -50, 50, 38
temp_range = [round(start + (end - start) * i / (n - 1), 1) for i in range(n)]

min_temp_colors = np.array([
    [145, 0, 63],
    [206, 18, 86],
    [231, 41, 138],
    [223, 101, 176],
    [255, 115, 223],
    [255, 190, 232],
    [255, 255, 255],
    [218, 218, 235],
    [188, 189, 220],
    [158, 154, 200],
    [117, 107, 177],
    [84, 39, 143],
    [13, 0, 125],
    [13, 61, 156],
    [0, 102, 194],
    [41, 158, 255],
    [74, 199, 255],
    [115, 215, 255],
    [173, 255, 255],
    # [48, 207, 194],
    # [0, 153, 150],
    # [18, 87, 87],
    # [6, 109, 44],
    # [49, 163, 84],
    # [116, 196, 118],
    # [161, 217, 155],
    # [211, 255, 190],
    # [255, 255, 179],
    # [255, 237, 160],
    # [254, 209, 118],
    # [254, 174, 42],
    # [253, 141, 60],
    # [252, 78, 42],
    # [227, 26, 28],
    # [177, 0, 38],
    # [128, 0, 38],
    # [89, 0, 66],
    # [40, 0, 40]
])

max_temp_colors = np.array([
    # [145, 0, 63],
    # [206, 18, 86],
    # [231, 41, 138],
    # [223, 101, 176],
    # [255, 115, 223],
    # [255, 190, 232],
    # [255, 255, 255],
    # [218, 218, 235],
    # [188, 189, 220],
    # [158, 154, 200],
    # [117, 107, 177],
    # [84, 39, 143],
    # [13, 0, 125],
    # [13, 61, 156],
    # [0, 102, 194],
    # [41, 158, 255],
    # [74, 199, 255],
    # [115, 215, 255],
    # [173, 255, 255],
    [48, 207, 194],
    [0, 153, 150],
    [18, 87, 87],
    [6, 109, 44],
    [49, 163, 84],
    [116, 196, 118],
    [161, 217, 155],
    [211, 255, 190],
    [255, 255, 179],
    [255, 237, 160],
    [254, 209, 118],
    [254, 174, 42],
    [253, 141, 60],
    [252, 78, 42],
    [227, 26, 28],
    [177, 0, 38],
    [128, 0, 38],
    [89, 0, 66],
    [40, 0, 40]
])

# prcp_range_inches = [0, 0.01, 0.1, 0.25, 0.5, 1, 1.5, 2, 3, 4, 6, 8, 10, 15, 20, 30]
prcp_range_inches = [0, 0.01, 0.1, 0.25, 0.5, 1, 1.5, 2, 3, 4, 6, 8, 10]
prcp_range_mm = [round(value * 25.4, 2) for value in prcp_range_inches]

prcp_colors = np.array([
    [255, 255, 255],
    [199, 233, 192],
    [161, 217, 155],
    [116, 196, 118],
    [49, 163, 83],
    [0, 109, 44],
    [255, 250, 138],
    [255, 204, 79],
    [254, 141, 60],
    [252, 78, 42],
    [214, 26, 28],
    [173, 0, 38],
    [112, 0, 38],
    # [59, 0, 48],
    # [76, 0, 115],
    # [255, 219, 255]
])

min_temp_threshold = build_threshold_rgba(temp_range, min_temp_colors)
max_temp_threshold = build_threshold_rgba(temp_range, max_temp_colors)
prcp_threshold = build_threshold_rgba(prcp_range_mm, prcp_colors)

# List of files
geojson_files = [
    {"var_name": "tmin", "path": f"{files_path}/Illinois_tmin_round.json", "threshold": min_temp_threshold},
    {"var_name": "tmax", "path": f"{files_path}/Illinois_tmax_round.json", "threshold": max_temp_threshold},
    {"var_name": "prcp", "path": f"{files_path}/Illinois_prcp_risks_round.json", "threshold": prcp_threshold},
]

# Load Census Tracts GeoJSON
tracts_geojson_path = f"{files_path}/cb_2018_17_tract_500k.geojson"  # Update the path accordingly
try:
    tracts_gdf = gpd.read_file(tracts_geojson_path)
except FileNotFoundError:
    print(f"Census tract file not found: {tracts_geojson_path}. Exiting.")
    exit(1)
except Exception as e:
    print(f"Error loading census tracts GeoJSON: {e}. Exiting.")
    exit(1)

# Ensure there is a unique identifier for each tract
# Replace 'GEOID' with the actual property name in your GeoJSON
# if 'GEOID' not in tracts_gdf.columns:
#     print("Error: 'GEOID' field not found in census tracts GeoJSON. Please update the code with the correct field name.")
#     exit(1)
feat_id = 'GEOID'

# Process the files and output GeoJSON
process_files_geojson(geojson_files, tracts_gdf, feat_id)
