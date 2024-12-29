import numpy as np
import json
from consts import files_path, binary_data_dir
import pickle
import os
from collections import defaultdict


def build_threshold_rgba(a, C):
    # Normalize thresholds to the range [0, 1]
    norm = np.array([(float(i) - min(a)) / (max(a) - min(a)) for i in a])
    return [{"value": n, "color": tuple(color)} for n, color in zip(norm, C)]


def interpolate_color(value, var_threshold):
    """
    Interpolate color for a given value based on the thresholds.
    """
    if not isinstance(value, (int, float)) or np.isnan(value):
        return (0, 0, 0, 0)  # Fully transparent for invalid values

    # Extract values and colors from the thresholds
    thresholds = [t["value"] for t in var_threshold]
    colors = np.array([t["color"] for t in var_threshold])

    # Normalize the value to [0, 1]
    value_normalized = (value - min(thresholds)) / (max(thresholds) - min(thresholds))
    value_normalized = np.clip(value_normalized, 0, 1)

    # Interpolate each color channel (RGBA)
    r = np.interp(value_normalized, thresholds, colors[:, 0])
    g = np.interp(value_normalized, thresholds, colors[:, 1])
    b = np.interp(value_normalized, thresholds, colors[:, 2])
    a = np.interp(value_normalized, thresholds, colors[:, 3]) if colors.shape[1] == 4 else 255

    return int(r), int(g), int(b), int(a)


def get_color_for_value(var_threshold, value):
    """
    Wrapper for interpolate_color.
    """
    return interpolate_color(value, var_threshold)


def process_files(files):
    
    # Directory to save processed pickle files
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
                    r, g, b, a = get_color_for_value(file["threshold"], value, var_name)
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

start, end, n = -50, 50, 38
temp_range = [round(start + (end - start) * i / (n - 1), 1) for i in range(n)]

temp_colors = np.array([[145, 0, 63], [206, 18, 86], [231, 41, 138], [223, 101, 176],
                        [255, 115, 223], [255, 190, 232], [255, 255, 255], [218, 218, 235],
                        [188, 189, 220], [158, 154, 200], [117, 107, 177], [84, 39, 143],
                        [13, 0, 125], [13, 61, 156], [0, 102, 194], [41, 158, 255],
                        [74, 199, 255], [115, 215, 255], [173, 255, 255], [48, 207, 194],
                        [0, 153, 150], [18, 87, 87], [6, 109, 44], [49, 163, 84],
                        [116, 196, 118], [161, 217, 155], [211, 255, 190], [255, 255, 179],
                        [255, 237, 160], [254, 209, 118], [254, 174, 42], [253, 141, 60],
                        [252, 78, 42], [227, 26, 28], [177, 0, 38], [128, 0, 38],
                        [89, 0, 66], [40, 0, 40]])

prcp_range_inches = [0, 0.01, 0.1, 0.25, 0.5, 1, 1.5, 2, 3, 4, 6, 8, 10, 15, 20, 30]
prcp_range_mm = [round(value * 25.4, 2) for value in prcp_range_inches]
prcp_colors = np.array([[255, 255, 255], [199, 233, 192], [161, 217, 155], [116, 196, 118],
                        [49, 163, 83], [0, 109, 44], [255, 250, 138], [255, 204, 79],
                        [254, 141, 60], [252, 78, 42], [214, 26, 28], [173, 0, 38],
                        [112, 0, 38], [59, 0, 48], [76, 0, 115], [255, 219, 255]])

# Build interpolated thresholds
temp_threshold = build_threshold_rgba(temp_range, temp_colors)
prcp_threshold = build_threshold_rgba(prcp_range_mm, prcp_colors)

# List of files
geojson_files = [
    # {"var_name": "tmin", "path": f"{files_path}/Yearly_tmin_round.json", "threshold": temp_threshold},
    {"var_name": "tmax", "path": f"{files_path}/Yearly_tmax_round.json", "threshold": temp_threshold},
    # {"var_name": "prcp", "path": f"{files_path}/Illinois_prcp_risks_round.json", "threshold": prcp_threshold},
]

process_files(geojson_files)
