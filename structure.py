import json
from consts import files_path, thresholds, binary_data_dir, variables
import pickle
import os
from collections import defaultdict

class Structure(object):
    def __init__(self) -> None:
        self.__geojson_dict = {}
        self.__binary = {}
    
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

    # Accessing data
    def get_data(self, name="tmin", year="1980"):
        try:
            return self.__binary[name][year]
        except KeyError:
            print(f"No data found for name: {name} and year: {year}")
            return None
    
    def process_files(self):

        # List of files to process with their variable names
        files = [
            {"var_name": "tmin", "path": f"{files_path}/Yearly_tmin_round.json"},
            {"var_name": "tmax", "path": f"{files_path}/Yearly_tmax_round.json"},
            {"var_name": "prcp", "path": f"{files_path}/Yearly_prcp_round.json"},
        ]

        # Default radius value
        my_radius = 30

        # Directory to save processed pickle files
        # output_dir = os.path.join(files_path, "processed_data")
        os.makedirs(binary_data_dir, exist_ok=True)  # Create the directory if it doesn't exist

        for file in files:
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

            # Store the GeoJSON data internally if needed
            self.__geojson_dict[var_name] = data

            features = data.get("features", [])
            if not features:
                print(f"No features found in {file_path}. Skipping {var_name}.")
                continue

            # Extract all years from the properties of the first feature
            sample_feature = features[0]
            properties = sample_feature.get("properties", {})
            # Assuming year properties are all keys that are purely digits
            years = sorted([key for key in properties.keys() if key.isdigit()])

            if not years:
                print(f"No year properties found in {file_path}. Skipping {var_name}.")
                continue

            print(f"Processing variable '{var_name}' for years: {', '.join(years)}")

            for year in years:
                positions = []
                colors = []
                radii = []
                processed_features = 0

                for feature in features:
                    coord = feature.get("geometry", {}).get("coordinates", [])
                    if not coord or len(coord) < 2:
                        print(f"Invalid coordinates in feature: {feature}. Skipping feature.")
                        continue

                    properties = feature.get("properties", {})

                    # Retrieve the value for the current year
                    # raw_value = properties.get(year, my_radius)  # Default to my_radius if year not present
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
                        r, g, b, a = self.get_color_for_value(value, var_name)
                    except ValueError as e:
                        print(f"Error converting color for value {value}: {e}")
                        r, g, b, a = (0, 0, 0, 0)  # Fully transparent as fallback

                    # Determine the radius
                    # radius = properties.get("radius", my_radius)  # Replace "radius" with actual key if different
                    # if radius is None:
                    #     radius = my_radius
                    # else:
                    #     try:
                    #         radius = float(radius)
                    #     except (ValueError, TypeError):
                    #         print(f"Warning: Unable to convert radius '{radius}' to float for feature with properties {properties}")
                    #         radius = my_radius

                    # Append data
                    positions.extend([coord[0], coord[1]])
                    colors.extend([r, g, b, a])
                    # radii.append(radius)
                    processed_features += 1

                # Prepare the binary data
                binary_data = {
                    "length": processed_features,
                    "positions": positions,
                    "colors": colors,
                    # "radii": radii  # Uncomment if radii are needed
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
    
    def get_geojson_data(self, var_name):
        return self.__geojson_binary[var_name]
        # geojson_data = self.__geojson_dict[var_name]
        # return geojson_data
  
if __name__ == "__main__":
    structure = Structure()
    # structure.process_files()
    structure.load_data()
    structure.get_data()