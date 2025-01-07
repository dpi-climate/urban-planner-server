import sys
import os
import json
import pickle

from consts import min_temp_domain, min_temp_colors, max_temp_domain, max_temp_colors, prcp_domain_mm, prcp_colors

def build_threshold_rgba(a, C):
    # Bins normalized between 0 and 1
    # norm = [(float(i) - min(a)) / (max(a) - min(a)) for i in a]

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

def process_climate_points_files(raw_file_path, final_path, var_id, var_threshold, process_ids=False, process_values=False):
    with open(raw_file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    features = data.get("features", [])
    sample_feature = features[0]
    properties = sample_feature.get("properties", {})

    time_stamp_keys = sorted([key for key in properties.keys() if key.isdigit()])

    print(f"Processing variable '{var_id}' for years: {', '.join(time_stamp_keys)}")

    for time_stamp in time_stamp_keys:
        positions = []
        colors = []
        values = []
        ids = []
        processed_features = 0
        id_counter = 0

        final_data = {}

        for feature in features:
            
            # Process positions
            coord = feature.get("geometry", {}).get("coordinates", [])

            if not coord or len(coord) < 2:
                print(f"Invalid coordinates in feature: {feature}. Skipping feature.")
                continue
            
            positions.extend([coord[0], coord[1]])
            
            properties = feature.get("properties", {})
            raw_value = properties.get(time_stamp)

            if raw_value is None:
                value = None  # Will be handled as transparent
            
            else:
                try:
                    value = float(raw_value)
                except (ValueError, TypeError):
                    print(f"Warning: Unable to convert value '{raw_value}' to float for feature with properties {properties}")
                    value = None  # Will be handled as transparent

            # Process colors
            try:
                r, g, b, a = get_color_for_value(var_threshold, value)

            except ValueError as e:
                print(f"Error converting color for value {value}: {e}")
                r, g, b, a = (0, 0, 0, 0)  # Fully transparent as fallback
            
            colors.extend([r, g, b, a])
            
            # Process values
            if process_values:
                values.append(value)
            
            # Process ids
            if process_ids:
                ids.append(id_counter)
                id_counter += 1
            
            processed_features += 1

        final_data = {
            "length": processed_features,
            "positions": positions,
            "colors": colors,
        }

        if process_values:
            final_data["values"] = values
            
        if process_ids:
           final_data["ids"] = ids

        processed_file_name = f"pt_{var_id}_{time_stamp}.pickle"
        processed_file_path = os.path.join(final_path, processed_file_name)

        try:
            with open(processed_file_path, 'wb') as pf:
                pickle.dump(final_data, pf)
            print(f"Saved binary data for {var_id} {time_stamp} to {processed_file_path}")
        
        except IOError as e:
            print(f"Failed to save binary data to {processed_file_path}: {e}")

if __name__ == "__main__":

    raw_path = "./raw_files"
    processed_path = "./processed_files/climate"

    ######################################################
    # Process tmin

    min_temp_id = "tmin"
    raw_min_temp_path = f"{raw_path}/Illinois_tmin_round.json"
    min_temp_threshold = build_threshold_rgba(min_temp_domain, min_temp_colors)

    process_climate_points_files(
        raw_min_temp_path,
        processed_path,
        min_temp_id,
        min_temp_threshold,
        True,
        True
    )

    ######################################################
    # Process tmax
    
    max_temp_id = "tmax"
    raw_max_temp_path = f"{raw_path}/Illinois_tmax_round.json"
    max_temp_threshold = build_threshold_rgba(max_temp_domain, max_temp_colors)

    process_climate_points_files(
        raw_max_temp_path,
        processed_path,
        max_temp_id,
        max_temp_threshold,
        True,
        True
    )

    ######################################################
    # Process prcp
    
    prcp_id = "prcp"
    raw_prcp_path = f"{raw_path}/Illinois_prcp_risks_round.json"
    prcp_threshold = build_threshold_rgba(prcp_domain_mm, prcp_colors)

    process_climate_points_files(
        raw_prcp_path,
        processed_path,
        prcp_id,
        prcp_threshold,
        True,
        True
    )


   



