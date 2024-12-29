from consts import binary_data_dir
import pickle
import os
from collections import defaultdict
import pandas as pd
import re
from geopy.distance import geodesic
import numpy as np
from scipy.spatial.distance import cdist

class Structure(object):
    def __init__(self) -> None:
        self.__binary = {}
        self.__risk_df = None
    
    
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
        try:
            return self.__binary[s_agg][name][year]
        except KeyError:
            print(f"No data found for name: {name} and year: {year}")
            return None

    def get_polygon_layer(self, name, year):
        try:
            return self.__binary[name][year]
        except KeyError:
            print(f"No data found for name: {name} and year: {year}")
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

  
if __name__ == "__main__":
    structure = Structure()
    structure.load_points()
    structure.get_points()