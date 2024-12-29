from consts import binary_data_dir, stations_file
import pickle
import os
from collections import defaultdict
import pandas as pd
import re
import numpy as np
import struct
import json
class Structure(object):
    def __init__(self) -> None:
        self.__binary = {}
        self.__risk_df = None
        self.__stations = None
    
    def load_points(self, file_group, prefix=''):
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
                    
                    file_path = os.path.join(binary_data_dir, filename)
                    with open(file_path, 'rb') as f:
                        data = pickle.load(f)
                    
                    data_dict[name][year] = data

                except Exception as e:
                    print(f"Failed to load {filename}: {e}")
        
        return data_dict
    
    def load_binary(self):
        all_files = [f for f in os.listdir(binary_data_dir) if f.endswith('.pickle')]
        groups = defaultdict(list)
        
        for filename in all_files:
            name_year = filename[:-7]
            parts = name_year.split('_')
            
            if len(parts) == 3:
                prefix = parts[0]
            elif len(parts) == 2:
                prefix = ''
            else:
                print(f"Unexpected filename format: {filename}")
                continue
            
            groups[prefix].append(filename)
        
        all_data = {}
        for prefix, file_group in groups.items():
            print(f"Processing group with prefix '{prefix}' containing {len(file_group)} files.")
            group_data = self.load_points(file_group, prefix)
            all_data[prefix] = group_data
        
        self.__binary = all_data
        print(all_data.keys())
        # return all_data
    
    def load_stations(self):
        with open(stations_file, 'r', encoding='utf-8') as f:
            self.__stations = json.load(f)
    
    def load_points_old(self):
        data_dict = defaultdict(dict)  # Nested dictionary: data_dict[name][year] = data
        
        for filename in os.listdir(binary_data_dir):
            if filename.endswith('.pickle'):
                try:
                    name, year_ext = filename.split('_')
                    year = year_ext.split('.')[0]
                    file_path = os.path.join(binary_data_dir, filename)
                    
                    with open(file_path, 'rb') as f:
                        data = pickle.load(f)
                    
                    data_dict[name][year] = data

                except Exception as e:
                    print(f"Failed to load {filename}: {e}")
        self.__binary = data_dict

    def load_risk(self):
        feather_file = "./files/Illinois_prcp_risks_round.feather"
        df = pd.read_feather(feather_file)
        self.__risk_df = df

        if 'latitude' in self.__risk_df.columns and 'longitude' in self.__risk_df.columns:
            self.__risk_df['latitude'] = self.__risk_df['latitude'].astype(float)
            self.__risk_df['longitude'] = self.__risk_df['longitude'].astype(float)
    
    def get_points(self, name, year, s_agg):
        """
        Return binary data for both points (s_agg == "") and polygons (s_agg == "ct").
        """
        print("[Structure - get_points] ", name, year, s_agg)
        try:
            data = self.__binary[s_agg][name][year]
        except KeyError:
            print(f"No data found for name: {name}, year: {year}, s_agg: {s_agg}")
            return None

        if not data:
            print(f"Data for {name}-{year}-{s_agg} is empty.")
            return None

        # ---------------------------
        # CASE 1: Points (s_agg == "")
        # ---------------------------
        if s_agg == "":
            # Expect fields: {"length": int, "positions": [...], "colors": [...]}
            length = data["length"]
            positions = data["positions"]
            colors = data["colors"]
            # ids = data["ids"]
            # values = data["values"]

            header = struct.pack("<I", length)  # 4 bytes (little-endian)
            
            pos_fmt = f"<{len(positions)}f"
            pos_bin = struct.pack(pos_fmt, *positions)
            
            col_fmt = f"<{len(colors)}B"
            col_bin = struct.pack(col_fmt, *colors)

            # ids_fmt = f"<{len(ids)}f"
            # ids_bin = struct.pack(ids_fmt, *ids)

            # values_fmt = f"<{len(values)}f"
            # values_bin = struct.pack(values_fmt, *values)

            final_data = header + pos_bin + col_bin #+ ids_bin + values_bin

            return final_data

        # ---------------------------
        # CASE 2: Polygons (s_agg == "ct")
        # ---------------------------
        elif s_agg == "ct":
            # data format: { "tracts": [ { "GEOID": str, "average_value": float,
            #                             "color": [r,g,b,a],
            #                             "geometry": {...} }, ... ] }

            tracts = data["tracts"]
            num_tracts = len(tracts)

            # 1) pack the number of tracts (4 bytes)
            buffer_list = [struct.pack("<I", num_tracts)]

            # 2) for each tract, pack the fields
            for tract in tracts:
                geo_id = tract["GEOID"]
                avg_val = tract["average_value"]
                color = tract["color"]  # [r,g,b,a]
                geometry_dict = tract["geometry"]

                # i) GEOID as UTF-8 bytes
                geo_id_bytes = geo_id.encode("utf-8")
                geo_id_len = len(geo_id_bytes)
                buffer_list.append(struct.pack("<I", geo_id_len))  # length of GEOID
                buffer_list.append(geo_id_bytes)                    # actual GEOID bytes

                # ii) average_value (float32)
                buffer_list.append(struct.pack("<f", avg_val))

                # iii) color (4 bytes)
                # color is likely [int, int, int, int], each 0-255
                buffer_list.append(struct.pack("<BBBB", *color))

                # iv) geometry as JSON string
                geom_str = json.dumps(geometry_dict)  # e.g. {"type":"Polygon","coordinates":[...]}
                geom_bytes = geom_str.encode("utf-8")
                geom_len = len(geom_bytes)
                buffer_list.append(struct.pack("<I", geom_len))
                buffer_list.append(geom_bytes)

            # Combine everything
            final_data = b"".join(buffer_list)
            return final_data

        else:
            # Unknown s_agg
            print(f"Unhandled s_agg='{s_agg}' - returning None.")
            return None

    @staticmethod
    def haversine_distance(lat1, lon1, lat2, lon2):
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
                    distances = self.haversine_distance(lat, lon, latitudes, longitudes)
                    
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

    def get_stations(self):
        return self.__stations
    
if __name__ == "__main__":
    structure = Structure()
    structure.load_points()
    structure.get_points()