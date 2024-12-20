import json
from consts import files_path, thresholds, binary_data_dir, variables
import pickle
import os
from collections import defaultdict
import pandas as pd

class Structure(object):
    def __init__(self) -> None:
        self.__geojson_dict = {}
        self.__binary = {}
        self.__risk_df = None
    
    def load_data(self):
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
        # return data_dict

    def load_risk(self):
        feather_file = "./files/Illinois_prcp_risks_round.feather"
        df = pd.read_feather(feather_file)
        self.__risk_df = df
    
    # Accessing data
    def get_data(self, name, year):
        try:
            return self.__binary[name][year]
        except KeyError:
            print(f"No data found for name: {name} and year: {year}")
            return None
    
    def build_risk_chart_data(self, index):
        properties_of_interest = ['risk_2yr (', 'risk_5yr (', 'risk_10yr', 'risk_25yr', 'risk_50yr', 'risk_100yr', 'risk_200yr', 'risk_500yr']

        if index in self.__risk_df.index:
            # Extract the properties for the specified index
            extracted_row = self.__risk_df.loc[index, properties_of_interest]
            print(f"Extracted properties for index {index}:")
            print(extracted_row)


        else:
            print(f"Index {index} does not exist in the DataFrame.")
    
    def get_geojson_data(self, var_name):
        return self.__geojson_binary[var_name]
        # geojson_data = self.__geojson_dict[var_name]
        # return geojson_data
  
if __name__ == "__main__":
    structure = Structure()
    structure.load_data()
    structure.get_data()