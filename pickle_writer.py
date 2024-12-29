import numpy as np
import json
from consts import files_path, binary_data_dir
import pickle
import os
from collections import defaultdict
import geopandas as gpd



class PickleWriter(object):
    def __init__(self) -> None:
        self.__original_files = []
        self.__bbox_gpd = None
        self.__feature_id = None

    def __get_color_for_value(self, var_threshold, value):
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

    def __process_points(self):
        for file in self.__original_files:
            var_name = file["var_name"]
            file_path = file["path"]

            # Open and load the GeoJSON file
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
            except FileNotFoundError:
                print(f"File not found: {file_path}. Skipping {var_name}.")
                continue
            except json.JSONDecodeError as e:
                print(f"Invalid JSON in {file_path}: {e}. Skipping {var_name}.")
                continue

            features = data.get("features", [])
            if not features:
                print(f"No features found in {file_path}. Skipping {var_name}.")
                continue
            
            features = data.get("features", [])
            if not features:
                print(f"No features found in {file_path}. Skipping {var_name}.")
                continue

            # Extract all years from the properties of the first feature
            sample_feature = features[0]
            properties = sample_feature.get("properties", {})

            years = sorted([key for key in properties.keys() if key.isdigit()])

            if not years:
                print(f"No year properties found in {file_path}. Skipping {var_name}.")
                continue

            print(f"Processing variable '{var_name}' for years: {', '.join(years)}")

            for year in years:
                positions = []
                colors = []
                values = []  # New list to store values
                ids = []  # List to store IDs
                processed_features = 0
                point_id = 0  # Initialize ID counter

                for feature in features:
                    coord = feature.get("geometry", {}).get("coordinates", [])
                    if not coord or len(coord) < 2:
                        print(f"Invalid coordinates in feature: {feature}. Skipping feature.")
                        continue

                    properties = feature.get("properties", {})

                    # Retrieve the value for the current year
                    raw_value = properties.get(year)

                    # Convert raw_value to float, handle errors
                    if raw_value is None:
                        value = None  # Will be handled as transparent
                    else:
                        try:
                            value = float(raw_value)
                        except (ValueError, TypeError):
                            print(f"Warning: Unable to convert value '{raw_value}' to float for feature with properties {properties}")
                            value = None  # Will be handled as transparent

                    # Get the color based on the value and thresholds
                    try:
                        r, g, b, a = self.__get_color_for_value(file["threshold"], value)
                    except ValueError as e:
                        print(f"Error converting color for value {value}: {e}")
                        r, g, b, a = (0, 0, 0, 0)  # Fully transparent as fallback

                    # Append data
                    positions.extend([coord[0], coord[1]])
                    colors.extend([r, g, b, a])
                    values.append(value)  # Store the value
                    ids.append(point_id)  # Add the current point ID
                    point_id += 1  # Increment ID counter
                    processed_features += 1

                # Prepare the binary data
                binary_data = {
                    "length": processed_features,
                    "positions": positions,
                    "colors": colors,
                    "values": values,
                    "ids": ids
                }

                # Define the filename
                filename = f"{var_name}_{year}.pickle"
                filepath = os.path.join(binary_data_dir, filename)

                # Save the binary data using pickle
                try:
                    with open(filepath, 'wb') as pf:
                        pickle.dump(binary_data, pf)
                    print(f"Saved binary data for {var_name} {year} to {filepath}")
                except IOError as e:
                    print(f"Failed to save binary data to {filepath}: {e}")
    
    def __process_polygons(self):
        for file in self.__original_files:
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
            if points_gdf.crs != self.__bbox_gpd.crs:
                points_gdf = points_gdf.to_crs(self.__bbox_gpd.crs)

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
                    joined = gpd.sjoin(df_year, self.__bbox_gpd, how='inner', predicate='within')
                except Exception as e:
                    print(f"Error during spatial join for {var_name} {year}: {e}")
                    continue

                # Group by tract and compute average
                grouped = joined.groupby(self.__feature_id)[year].mean().reset_index()
                grouped.rename(columns={year: 'average_value'}, inplace=True)

                # Assign colors based on average values
                grouped['color'] = grouped['average_value'].apply(lambda x: self.__get_color_for_value(file["threshold"], x))

                # Merge with bbox_gpd to get geometries
                grouped = grouped.merge(self.__bbox_gpd[[self.__feature_id, 'geometry']], on=self.__feature_id, how='left')

                # Convert to GeoDataFrame
                geojson_gdf = gpd.GeoDataFrame(grouped, geometry='geometry')

                # Define properties for GeoJSON
                geojson_gdf['color'] = geojson_gdf['color'].apply(lambda c: f"rgba({c[0]}, {c[1]}, {c[2]}, {c[3]})")
                geojson_gdf = geojson_gdf[[self.__feature_id, 'average_value', 'color', 'geometry']]

                # Define the filename
                filename = f"ct_{var_name}_{year}.geojson"
                filepath = os.path.join(binary_data_dir, filename)

                # Save to GeoJSON
                try:
                    geojson_gdf.to_file(filepath, driver='GeoJSON')
                    print(f"Saved GeoJSON data for {var_name} {year} to {filepath}")
                except IOError as e:
                    print(f"Failed to save GeoJSON data to {filepath}: {e}")
    
    def process_file(self):

        if self.__bbox_gpd != None and self.__feature_id != None:
            self.__process_polygons()

        else:
            self.__process_points()

    def reset_obj(self):
        self.__original_files = []
        self.__bbox_gpd = None
        self.__feature_id = None

    def start_obj(self, files, bbox_gpd, feature_id):
        self.__original_files = files
        self.__bbox_gpd = bbox_gpd
        self.__feature_id = feature_id