import json

from consts import files_path, thresholds
import json

class Structure(object):
    def __init__(self) -> None:
        self.__geojson_dict = {}
        self.__geojson_binary = {}
        self.__geojson_features = {}
    
    def hex_to_rgba(self, hex_color, alpha=255):
        """
        Convert a hexadecimal color string to an RGBA tuple.
        """
        hex_color = hex_color.lstrip('#')
        if len(hex_color) != 6:
            raise ValueError(f"Invalid hex color: {hex_color}")
        r = int(hex_color[0:2], 16)
        g = int(hex_color[2:4], 16)
        b = int(hex_color[4:6], 16)
        
        return (r, g, b, alpha)

    def get_color_for_value(self, value, var_name):
        """
        Given a value and a list of thresholds, return the corresponding color.
        If the value is non-numeric, return a fully transparent color.
        If the value is below the first threshold, return the first color.
        If the value is above the last threshold, return the last color.
        """
        if not isinstance(value, (int, float)) or value == 0:
            # Fully transparent
            return (0, 0, 0, 0)
        
        for threshold in thresholds[var_name]:
            if value <= threshold["value"]:
                return self.hex_to_rgba(threshold["color"])
        # If value exceeds all thresholds, return the last color
        return self.hex_to_rgba(thresholds[var_name][-1]["color"])
    
    def process_files(self):
        files = [
            {"var_name": "tmin", "path": f"{files_path}/Yearly_tmin_round.json"},
            {"var_name": "tmax", "path": f"{files_path}/Yearly_tmax_round.json"},
            {"var_name": "prcp", "path": f"{files_path}/Yearly_prcp_round.json"},
        ]

        for file in files:
            # Open and load the GeoJSON file
            with open(file["path"], 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            self.__geojson_dict[file["var_name"]] = data
            # self.__geojson_features = data.get("features", [])
        
            features = data.get("features", [])
            length = len(features)
        
            positions = []
            colors = []
            radii = []
        
            for feature in features:
                coord = feature["geometry"]["coordinates"]  # [lng, lat]
                properties = feature["properties"]
                
                # Retrieve the value from the properties
                # Replace "1980" with the actual property key you want to use
                raw_value = properties.get("1985", 500)  # Default to 500 if "1980" not present
                
                # Ensure the value is a float, handle None or non-numeric values
                if raw_value is None:
                    value = None  # Will be handled as transparent
                else:
                    try:
                        value = float(raw_value)
                    except (ValueError, TypeError):
                        # Handle cases where conversion to float fails
                        print(f"Warning: Unable to convert value '{raw_value}' to float for feature with properties {properties}")
                        value = None  # Will be handled as transparent
                
                # Get the color based on the value and thresholds
                try:
                    r, g, b, a = self.get_color_for_value(value, file["var_name"])
                except ValueError as e:
                    # Handle invalid hex color
                    print(f"Error converting color for value {value}: {e}")
                    r, g, b, a = (0, 0, 0, 0)  # Fully transparent as fallback
                
                # Optionally, determine the radius based on the value or another property
                # Here, using a separate "radius" property if available, else default to 500
                radius = properties.get("radius", 500)  # Replace "radius" with actual key if different
                if radius is None:
                    radius = 500  # Assign default if radius is None
                else:
                    try:
                        radius = float(radius)
                    except (ValueError, TypeError):
                        print(f"Warning: Unable to convert radius '{radius}' to float for feature with properties {properties}")
                        radius = 500  # Assign default value
                
                # Append position
                positions.extend([coord[0], coord[1]])
        
                # Append color (RGBA)
                colors.extend([r, g, b, a])
        
                # Append radius
                radii.append(radius)
        
            # Prepare the binary data
            binary_data = {
                "length": length,
                "positions": positions,
                "colors": colors,
                "radii": radii
            }
        
            # Store the binary data as JSON string
            # self.__geojson_binary[file["var_name"]] = json.dumps(binary_data)
            self.__geojson_binary[file["var_name"]] = binary_data    

    

    

    
    def get_geojson_data(self, var_name):
        return self.__geojson_binary[var_name]
        # geojson_data = self.__geojson_dict[var_name]
        # return geojson_data
    
    def get_geojson_features(self, var_name):

        final_geojson = copy.deepcopy(source_geojson)

        for feature in final_geojson["features"]:
            # Replace the properties with only the 1980 property
            feature["properties"] = {"1980": feature["properties"].get("1980")}
        
        # return self.__geojson_features[var_name]
        return final_geojson
    
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
                