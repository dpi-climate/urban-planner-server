from consts import SOCIO_VARIABLES, STATIONS_FILE, CLIMATE_VARIABLES, CLIMATE_TIME_STAMPS, SOCIO_SPATIAL_LEVELS, RISK_FILE, CLIMATE_SPATIAL_LEVELS, processed_climate_files_dir, processed_bound_files_dir, socio_vars, processed_socio_dir, click_boundary_file, boundaries_list
import pickle
import os
from collections import defaultdict
import pandas as pd
import re
import numpy as np
import struct
import json
import geopandas as gpd
import ast
import pyarrow.parquet as pq
import pyarrow as pa
import io
import dask_geopandas as dg
from shapely import ops
import polars as pl

class Structure(object):
    def __init__(self) -> None:
        self.__boundary_layers = {}
        self.__climate_layers = {}
        self.__risk_df = None
        
        self.__stations = None
        
        self.__socio_df = None
        self.__socio_gdf = None
        self.__socio_layers = {}
        # self.__socio_list = []
        self.__climate_geojson = None

    ########################  LOAD FUNCTIONS #################################################
    
    
    def load_csv_file(self, var_name, year, s_agg):
        # filep = "C:/Users/carolvfs/Documents/GitHub/urban-planner-server/preprocessing/rebuild_climate_agg/all_no_null.parquet"
        # df = gpd.read_parquet(filep)
        # df_filtered = df[["UNITID", year, "geometry"]].copy()
        # df_filtered = df_filtered.rename(columns={year: "value"})
        # # df_filtered["geometry"] = df_filtered["geometry"]#.apply(lambda geom: geom.wkt if geom is not None else None)#.astype(str)
        # df_filtered["geometry"] = df_filtered["geometry"].apply(
        #     lambda g: g.wkt if g is not None else None
        # )


        # # buffer = df_filtered.to_json()
        # null_geometries = df_filtered["geometry"].isnull().sum()
        # print(f"Number of null geometries: {null_geometries}")

        # df_filtered = pd.DataFrame(df_filtered)
        
        # buffer = io.BytesIO()
        # # df_filtered.to_parquet(buffer, compression=None, engine='pyarrow', version="1.0")
        # df_filtered.to_feather(buffer, compression="uncompressed")

    
        # buffer.seek(0)

        # return buffer#.read()
    
        csv_file = f"{processed_climate_files_dir}/{s_agg}_{var_name}.csv"
        # csv_file = f"{processed_climate_files_dir}/ct_prcp.csv"
        # df = pd.read_csv(csv_file)
        # df = pl.read_csv(csv_file)
        df = pl.read_csv(csv_file, columns=["UNITID", "geometry", year])

        buffer_list = []

        # Number of rows (features) in the DataFrame
        # num_features = len(df)
        num_features = df.height
        buffer_list.append(struct.pack("<I", num_features))  # Pack the number of features

        # Iterate over each row to encode its data
        # for _, row in df.iterrows():
        for row in df.iter_rows(named=True):
            # UNITID as UTF-8 bytes
            geo_id = str(row["UNITID"])  # Ensure UNITID is a string
            geo_id_bytes = geo_id.encode("utf-8")
            geo_id_len = len(geo_id_bytes)
            buffer_list.append(struct.pack("<I", geo_id_len))  # Length of UNITID
            buffer_list.append(geo_id_bytes)                  # Actual UNITID bytes

            # Value (year column) as float32
            avg_val = 30.0 #float(row[year])  # Ensure it's a float
            buffer_list.append(struct.pack("<f", avg_val))

            # Placeholder for color (example: [255, 0, 0, 255])
            color = ast.literal_eval(row[year])
            buffer_list.append(struct.pack("<BBBB", *color))

            # Geometry as JSON string
            geometry_dict = json.loads(row["geometry"])  # Assuming 'geometry' column contains JSON strings
            geom_str = json.dumps(geometry_dict)
            geom_bytes = geom_str.encode("utf-8")
            geom_len = len(geom_bytes)
            buffer_list.append(struct.pack("<I", geom_len))  # Length of geometry
            buffer_list.append(geom_bytes)                  # Actual geometry bytes

        # Combine all parts into a single byte string
        final_data = b"".join(buffer_list)

        return final_data
    
    def __load_climate_spatial_level(self, file_group, prefix=''):
        data_dict = defaultdict(dict)
        
        for filename in file_group:
            if filename.endswith('.pickle'):
                try:
                    name_year = filename[:-7]
                    parts = name_year.split('_')
                    
                    if prefix:
                        if len(parts) != 3:
                            print(f"Unexpected filename format with prefix: {filename}")
                            continue
                        _, name, year = parts
                    else:
                        if len(parts) != 2:
                            print(f"Unexpected filename format without prefix: {filename}")
                            continue
                        name, year = parts
                    
                    file_path = os.path.join(processed_climate_files_dir, filename)
                    with open(file_path, 'rb') as f:
                        data = pickle.load(f)
                    
                    data_dict[name][year] = data

                except Exception as e:
                    print(f"Failed to load {filename}: {e}")
        
        return data_dict
    
    def __load_social_spatial_level(self, file_group):
        data_dict = defaultdict(dict)
        
        for filename in file_group:
            if filename.endswith('.pickle'):
                try:
                    group_name = filename[:-7]
                    name = group_name.split('_', 1)[1]
                    
                    file_path = os.path.join(processed_socio_dir, filename)

                    with open(file_path, 'rb') as f:
                        data = pickle.load(f)

                    data_dict[name] = data

                except Exception as e:
                    print(f"Failed to load {filename}: {e}")
        
        return data_dict
    
    def load_boundary_layers(self):
        boundaries = {}

        for b in boundaries_list:
            id = b.get("id")

            if id == "None":
                continue

            print(f"Processing boundary {id}")
            
            file_path = os.path.join(processed_bound_files_dir, f"bound_{id}.pickle")
            
            with open(file_path, 'rb') as f:
                data = pickle.load(f)

            boundaries[id] = data

        self.__boundary_layers = boundaries
        
    def load_climate_layers(self):

        filep = "C:/Users/carolvfs/Documents/GitHub/urban-planner-server/preprocessing/rebuild_climate_agg/all_no_null.geojson"
        # self.__climate_geojson = gpd.read_file(filep)

         
        # all_files = [f for f in os.listdir(processed_climate_files_dir) if f.endswith('.pickle')]
        spatial_level_ids = [sp.get("id") for sp in CLIMATE_SPATIAL_LEVELS]
        
        all_files = [
            f for f in os.listdir(processed_climate_files_dir)
            if f.endswith('.pickle') and any(f.startswith(prefix + '_') for prefix in spatial_level_ids)
        ]

        groups = defaultdict(list)
        
        for filename in all_files:
            group_name_time = filename[:-7]
            parts = group_name_time.split('_')
            prefix = parts[0]
            
            groups[prefix].append(filename)
        
        all_data = {}
        
        for prefix, file_group in groups.items():
            print(f"Processing group with prefix '{prefix}' containing {len(file_group)} files.")
            group_data = self.__load_climate_spatial_level(file_group, prefix)
            all_data[prefix] = group_data
        
        self.__climate_layers = all_data
    
    def load_risk_df(self):
        df = pd.read_feather(RISK_FILE)
        self.__risk_df = df

        if 'latitude' in self.__risk_df.columns and 'longitude' in self.__risk_df.columns:
            self.__risk_df['latitude'] = self.__risk_df['latitude'].astype(float)
            self.__risk_df['longitude'] = self.__risk_df['longitude'].astype(float)
    
    def load_socio_df(self):
        level_list = [sp.get("id") for sp in SOCIO_SPATIAL_LEVELS]
        my_dict = {}

        for level in level_list:
            feather_file = f"./{processed_socio_dir}/{level}_socio.feather"
            df = pd.read_feather(feather_file)
            my_dict[level] = df
        
        self.__socio_df = my_dict
    
    def load_socio_layers(self):
        spatial_level_ids = [sp.get("id") for sp in SOCIO_SPATIAL_LEVELS]
        
        all_files = [
            f for f in os.listdir(processed_socio_dir)
            if f.endswith('.pickle') and any(f.startswith(prefix + '_') for prefix in spatial_level_ids)
        ]

        groups = defaultdict(list)
        
        for filename in all_files:
            group_name_time = filename[:-7]
            parts = group_name_time.split('_')
            prefix = parts[0]
            
            groups[prefix].append(filename)
        
        all_data = {}
        
        for prefix, file_group in groups.items():
            print(f"Processing group with prefix '{prefix}' containing {len(file_group)} files.")
            group_data = self.__load_social_spatial_level(file_group)
            all_data[prefix] = group_data
    
        self.__socio_layers = all_data

    def load_socio_gdf(self): # to do 
        pass
        # socio_list = [
        #     {"id": "ct", "name": "Census Tract"}, 
        #     {"id": "bg", "name": "Block Level"}
        # ]

        # boundaries = {}

        # for b in boundaries_list:
        #     print(f"Processing boundary {b.get("id")}")
        #     id = b.get("id")
        #     boundaries[b.get("id")] = None
            
        #     file_path = os.path.join(processed_bound_files_dir, f"bound_{id}.pickle")
        #     with open(file_path, 'rb') as f:
        #         data = pickle.load(f)

        #     boundaries[id] = data

        # boundaries_list.insert(0, {"id": "None", "name": "No Boundaries"})
        
        # self.__boundaries_list = boundaries_list
        # self.__boundary_layers = boundaries
   
    def load_stations_layer(self):
        with open(STATIONS_FILE, 'r', encoding='utf-8') as f:
            self.__stations = json.load(f)
    
    ########################  GET FUNCTIONS ################################################

    def get_boundary(self, boundary_id): # maybe preprocess this
        print(f"[Structure - get_boundary] {boundary_id}")

        data = self.__boundary_layers[boundary_id]

        features = data["features"]
        num_features = len(features)

        # Pack the number of features (4 bytes)
        buffer_list = [struct.pack("<I", num_features)]

        # For each feature, pack the fields
        for feature in features:
            unit_id = feature["UNITID"]
            geometry_dict = feature["geometry"]

            unit_id_bytes = unit_id.encode("utf-8")
            unit_id_len = len(unit_id_bytes)
            buffer_list.append(struct.pack("<I", unit_id_len))  # length of UNITID
            buffer_list.append(unit_id_bytes)                   # actual UNITID bytes

            # iv) geometry as JSON string
            geom_str = json.dumps(geometry_dict)
            geom_bytes = geom_str.encode("utf-8")
            geom_len = len(geom_bytes)
            buffer_list.append(struct.pack("<I", geom_len))
            buffer_list.append(geom_bytes)

        # Wrap up
        final_data = b"".join(buffer_list)

        return final_data

    def get_boundaries_list(self):
        return boundaries_list
    
    def get_click_boundary(self):
        print("[Structure - get_click_boundary] Sending click boundary")
        gdf = gpd.read_file(click_boundary_file)
        return gdf
    
    def get_climate_point_layer(self, name, year, s_agg): # maybe preprocess this
        """
        Return binary data for points.
        """
        print("[Structure - get_points] ", name, year, s_agg)
        try:
            data = self.__climate_layers[s_agg][name][year]
        
        except KeyError:
            print(f"No data found for name: {name}, year: {year}, s_agg: {s_agg}")
            return None

        if not data:
            print(f"Data for {name}-{year}-{s_agg} is empty.")
            return None

        if s_agg == "pt":
            length = data["length"]
            positions = data["positions"]
            colors = data["colors"]
            ids = data["ids"]
            values = data["values"]

            header = struct.pack("<I", length)
            
            pos_fmt = f"<{len(positions)}f"
            pos_bin = struct.pack(pos_fmt, *positions)
            
            col_fmt = f"<{len(colors)}B"
            col_bin = struct.pack(col_fmt, *colors)

            ids_fmt = f"<{len(ids)}I"
            ids_bin = struct.pack(ids_fmt, *ids)

            buffer_values = [struct.pack("<I", len(values))]

            for val in values:
                if val is None:
                    # 0 indicates None
                    buffer_values.append(struct.pack("<B", 0))
                else:
                    # 1 indicates a valid float
                    buffer_values.append(struct.pack("<B", 1))
                    buffer_values.append(struct.pack("<f", val))

            values_bin = b"".join(buffer_values)
            final_data = header + pos_bin + col_bin + ids_bin + values_bin
            size_in_bytes = len(final_data)
            # print(f"Size of the binary data: {size_in_bytes} bytes")
            print(f"Size of the binary data (points): {size_in_bytes  / (1024 ** 2):.2f} MB")

            return final_data
        
        else:
            # Unknown s_agg
            print(f"Unhandled s_agg='{s_agg}' - returning None.")
            return None

    def get_climate_polygon_layer(self, name, year, s_agg):
        print("[Structure - get_polygons] ", name, year, s_agg)
        try:
            data = self.__climate_layers[s_agg][name][year]
        
        except KeyError:
            print(f"No data found for name: {name}, year: {year}, s_agg: {s_agg}")
            return None

        if not data:
            print(f"Data for {name}-{year}-{s_agg} is empty.")
            return None
        
        features = data["features"]
        num_features = len(features)

        # Pack the number of features (4 bytes)
        buffer_list = [struct.pack("<I", num_features)]

        # For each feature, pack the fields
        for feature in features:
            geo_id = feature["UNITID"]
            avg_val = feature["value"]
            color = feature["color"]  # [r,g,b,a]
            geometry_dict = feature["geometry"]

            # UNITID as UTF-8 bytes
            geo_id_bytes = geo_id.encode("utf-8")
            geo_id_len = len(geo_id_bytes)
            buffer_list.append(struct.pack("<I", geo_id_len))  # length of UNITID
            buffer_list.append(geo_id_bytes)                    # actual UNITID bytes

            # Value (float32)
            buffer_list.append(struct.pack("<f", avg_val))

            # Color (4 bytes)
            buffer_list.append(struct.pack("<BBBB", *color))

            # Geometry as JSON string
            geom_str = json.dumps(geometry_dict)  # e.g. {"type":"Polygon","coordinates":[...]}
            geom_bytes = geom_str.encode("utf-8")
            geom_len = len(geom_bytes)
            buffer_list.append(struct.pack("<I", geom_len))
            buffer_list.append(geom_bytes)

        # Wrap up
        final_data = b"".join(buffer_list)
        return final_data

    def get_climate_spatial_levels(self):
        return CLIMATE_SPATIAL_LEVELS
    
    def get_climate_variables(self):
        # climate_variables_without_domain_colors = [
        #     {key: value for key, value in variable.items() if key not in ["domain", "colors"]}
        #     for variable in CLIMATE_VARIABLES
        # ]

        # return climate_variables_without_domain_colors

        converted_data = CLIMATE_VARIABLES.copy()

        for entry in converted_data:
            for key in ["domain", "colors"]:
                if key in entry and isinstance(entry[key], np.ndarray):
                    entry[key] = entry[key].tolist()
        return converted_data

    @staticmethod
    def __haversine_distance(lat1, lon1, lat2, lon2):
        """
        Calculate the great-circle distance between two points on the Earth surface.
        
        Parameters:
            lat1, lon1: Latitude and Longitude of point 1 in decimal degrees
            lat2, lon2: Latitude and Longitude of point 2 in decimal degrees
            
        Returns:
            Distance in meters
        """
        # Earth radius in meters
        R = 6371000  
        
        # Convert decimal degrees to radians
        lat1_rad, lon1_rad = np.radians(lat1), np.radians(lon1)
        lat2_rad, lon2_rad = np.radians(lat2), np.radians(lon2)
        
        # Haversine formula
        dlat = lat2_rad - lat1_rad
        dlon = lon2_rad - lon1_rad
        a = np.sin(dlat / 2.0)**2 + np.cos(lat1_rad) * np.cos(lat2_rad) * np.sin(dlon / 2.0)**2
        c = 2 * np.arcsin(np.sqrt(a))
        distance = R * c
        return distance

    def get_risk_data(self, identifier):
            """
            Retrieve risk data by index or by the nearest point to given lat/lon.
            
            Parameters:
                identifier: int (index) or tuple (lat, lon)
            
            Returns:
                List of risk data dictionaries.
            """
            formatted_data = []
            properties_of_interest = [
                'risk_2yr (', 'risk_5yr (', 'risk_10yr',
                'risk_25yr', 'risk_50yr', 'risk_100yr',
                'risk_200yr', 'risk_500yr'
            ]
            digit_pattern = re.compile(r'\d+')  # Compile the regex once
            
            if isinstance(identifier, int):  # If identifier is an index
                if identifier in self.__risk_df.index:
                    extracted_row = self.__risk_df.loc[identifier, properties_of_interest]
                    formatted_data = [
                        {"year": digit_pattern.search(column).group(), "value": value}
                        for column, value in extracted_row.items()
                    ]
                else:
                    print(f"Index {identifier} does not exist in the DataFrame.")
            
            elif isinstance(identifier, tuple) and len(identifier) == 2:  # If identifier is a lat/lon pair
                lat, lon = identifier
                
                if 'latitude' in self.__risk_df.columns and 'longitude' in self.__risk_df.columns:
                    # Extract all latitudes and longitudes
                    latitudes = self.__risk_df['latitude'].values
                    longitudes = self.__risk_df['longitude'].values
                    
                    # Calculate distances using the Haversine formula
                    distances = self.__haversine_distance(lat, lon, latitudes, longitudes)
                    
                    # Find the index of the nearest point
                    nearest_index = self.__risk_df.index[np.argmin(distances)]
                    
                    extracted_row = self.__risk_df.loc[nearest_index, properties_of_interest]
                    formatted_data = [
                        {"year": digit_pattern.search(column).group(), "value": value}
                        for column, value in extracted_row.items()
                    ]
                else:
                    print("Latitude and longitude columns are not available in the DataFrame.")
            
            else:
                print("Invalid identifier. Must be an integer index or a tuple (lat, lon).")
            
            return formatted_data

    def get_socio_data(self, id, level):
        df = self.__socio_df[level]
        df = df[df["GEOID"] == id]

        result = [
            {"name": description, "value": int(df[var].iloc[0]) if not df.empty else None}
            for var_dict in socio_vars
            for var, description in var_dict.items()
        ]
        
        return result
    
    def get_socio_variables(self): # to do
        converted_data = SOCIO_VARIABLES.copy()

        for entry in converted_data:
            for key in ["domain", "colors"]:
                if key in entry and isinstance(entry[key], np.ndarray):
                    entry[key] = entry[key].tolist()
        return converted_data
    
    def get_socio_layer(self, name, s_agg):
        print("[Structure - get_socio_layer] ", name, s_agg)
        try:
            print(self.__socio_layers.keys())
            print(self.__socio_layers[s_agg].keys())
            data = self.__socio_layers[s_agg][name]
        
        except KeyError:
            print(f"No data found for name: {name}, s_agg: {s_agg}")
            return None

        if not data:
            print(f"Data for {name} {s_agg} is empty.")
            return None
        
        features = data["features"]
        num_features = len(features)

        # Pack the number of features (4 bytes)
        buffer_list = [struct.pack("<I", num_features)]

        # For each feature, pack the fields
        for feature in features:
            geo_id = feature["UNITID"]
            avg_val = feature["value"]
            color = feature["color"]  # [r,g,b,a]
            geometry_dict = feature["geometry"]

            # UNITID as UTF-8 bytes
            geo_id_bytes = geo_id.encode("utf-8")
            geo_id_len = len(geo_id_bytes)
            buffer_list.append(struct.pack("<I", geo_id_len))  # length of UNITID
            buffer_list.append(geo_id_bytes)                    # actual UNITID bytes

            # Value (float32)
            buffer_list.append(struct.pack("<f", avg_val))

            # Color (4 bytes)
            buffer_list.append(struct.pack("<BBBB", *color))

            # Geometry as JSON string
            geom_str = json.dumps(geometry_dict)  # e.g. {"type":"Polygon","coordinates":[...]}
            geom_bytes = geom_str.encode("utf-8")
            geom_len = len(geom_bytes)
            buffer_list.append(struct.pack("<I", geom_len))
            buffer_list.append(geom_bytes)

        # Wrap up
        final_data = b"".join(buffer_list)
        return final_data
    
    def get_stations(self):
        return self.__stations
    
    def get_climate_time_stamp_list(self):
        return CLIMATE_TIME_STAMPS
    