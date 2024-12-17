import json

from consts import files_path

class Structure(object):
    def __init__(self) -> None:
        self.__geojson_dict = {}
        self.__geojson_features = {}

    def load_geojson(self):
        # main_path = "C:/Users/carol/Documents/GitHub/urban-planner/public"
        files = [
            {"var_name" : "tmin", "path": f"{files_path}/Yearly_tmin_round.json"},
            {"var_name" : "tmax", "path": f"{files_path}/Yearly_tmax_round.json"},
            {"var_name" : "prcp", "path": f"{files_path}/Yearly_prcp_round.json"},
            ]

        for file in files:
            # Open and load the GeoJSON file
            with open(file["path"], 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            self.__geojson_dict[file["var_name"]] = data
            self.__geojson_features = data.get("features", [])

        print("All set!")

    def get_geojson_data(self, var_name):
        geojson_data = self.__geojson_dict[var_name]
        return geojson_data
    
    def get_geojson_features(self, var_name):
        return self.__geojson_features[var_name]
    
    def get_point_feature(self, var_name):
        # Let's say you want the first feature
        desired_feature = self.__geojson_features[10000]
        data = [{"category": prop, "value": value} for prop, value in desired_feature["properties"].items()]
        return data

        # criteria_property = "id"
        # desired_value = "feature_12345"

        # desired_feature = None

        # for feature in self.__geojson_features:
        #     # Check the feature's properties
        #     if feature.get("properties", {}).get(criteria_property) == desired_value:
        #         desired_feature = feature
        #         break
                