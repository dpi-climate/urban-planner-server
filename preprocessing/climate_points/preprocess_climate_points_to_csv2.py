import sys
import os
import json
import pickle
import csv

# If you have a consts.py, it might look something like this:
from consts import (
    min_temp_domain,  # e.g., [ -20, -10, 0, 10, 20, 30 ]
    min_temp_colors,  # e.g., [ (0,0,255), (0,128,255), (0,255,255), (128,255,128), (255,255,0), (255,128,0) ]
    max_temp_domain,  
    max_temp_colors,  
    prcp_domain_mm,   
    prcp_colors       
)

# # For demonstration, you could define them inline here (if not importing from consts):
# min_temp_domain   = [-20, -10, 0, 10, 20, 30]
# min_temp_colors   = [(0, 0, 255), (0, 128, 255), (0, 255, 255), (128, 255, 128), (255, 255, 0), (255, 128, 0)]
# max_temp_domain   = [0, 10, 20, 30, 40]
# max_temp_colors   = [(0, 128, 255), (0, 255, 255), (128, 255, 128), (255, 255, 0), (255, 128, 0)]
# prcp_domain_mm    = [5, 10, 20, 50, 100]
# prcp_colors       = [(85, 255, 255), (0, 170, 255), (0, 85, 170), (0, 0, 255), (85, 0, 170)]


def build_threshold_rgba(a, C):
    """
    Given two lists:
      a = list of threshold values
      C = list of color triplets (R, G, B)
    Returns a list of dictionaries, each with "value" and "color".
    Example output:
      [
        {"value": 5,  "color": (85, 255, 255, 255)},
        {"value": 10, "color": (0, 170, 255, 255)},
        ...
      ]
    """
    output = []
    for value, color in zip(a, C):
        rgba_color = (int(color[0]), int(color[1]), int(color[2]), 255)
        output.append({"value": value, "color": rgba_color})
    return output


def get_color_for_value(var_threshold, value):
    """
    Given a value and a list of thresholds, return the corresponding RGBA color.
    If the value is non-numeric or 0, return a fully transparent color (0,0,0,0).
    If the value is below or equal to the first threshold, return the first color.
    If the value is above the last threshold, return the last color.
    Otherwise, return the color for the first threshold that is >= value.
    """
    if not isinstance(value, (int, float)) or value == 0:
        # Fully transparent
        return (0, 0, 0, 0)
    
    for threshold in var_threshold:
        if value <= threshold["value"]:
            return threshold["color"]
    # If value exceeds all var_threshold, return the last color
    return var_threshold[-1]["color"]


def json_to_csv_with_timestamps(raw_file_path, csv_file_path):
    """
    ORIGINAL VERSION (stores numeric values).
    Loads JSON data, extracts lat/lon and numeric values for each timestamp,
    then writes the results to CSV.
    """
    with open(raw_file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    features = data.get("features", [])
    if not features:
        print("No features found in the JSON data.")
        return

    # Identify sorted timestamp keys from the first feature's properties
    sample_feature = features[0]
    properties = sample_feature.get("properties", {})
    timestamp_keys = sorted([key for key in properties.keys() if key.isdigit()])

    # Prepare header: lat, lon, followed by each timestamp
    header = ["lat", "lon"] + timestamp_keys

    with open(csv_file_path, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(header)

        for feature in features:
            coord = feature.get("geometry", {}).get("coordinates", [])
            if not coord or len(coord) < 2:
                continue

            lon, lat = coord[0], coord[1]
            row = [lat, lon]

            properties = feature.get("properties", {})
            for ts in timestamp_keys:
                raw_value = properties.get(ts)
                try:
                    value = float(raw_value) if raw_value is not None else ""
                except (ValueError, TypeError):
                    value = ""
                row.append(value)

            writer.writerow(row)

    print(f"Data successfully written to {csv_file_path}")


def json_to_csv_with_timestamps_colors(raw_file_path, csv_file_path, threshold):
    """
    NEW VERSION (stores RGBA colors).
    Loads JSON data, extracts lat/lon and uses get_color_for_value(...) to map
    each timestamp value to an RGBA color, then writes it to CSV.
    """
    with open(raw_file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    features = data.get("features", [])
    if not features:
        print("No features found in the JSON data.")
        return

    # Identify sorted timestamp keys from the first feature's properties
    sample_feature = features[0]
    properties = sample_feature.get("properties", {})
    timestamp_keys = sorted([key for key in properties.keys() if key.isdigit()])

    # Prepare header: lat, lon, followed by each timestamp
    header = ["lat", "lon"] + timestamp_keys

    with open(csv_file_path, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(header)

        for feature in features:
            coord = feature.get("geometry", {}).get("coordinates", [])
            if not coord or len(coord) < 2:
                # Skip features with invalid coords
                continue

            lon, lat = coord[0], coord[1]
            row = [lat, lon]

            properties = feature.get("properties", {})
            for ts in timestamp_keys:
                raw_value = properties.get(ts)
                try:
                    value = float(raw_value) if raw_value is not None else None
                except (ValueError, TypeError):
                    value = None

                # Map the numeric value to an RGBA color
                color_tuple = get_color_for_value(threshold, value)

                # Store the color as "R,G,B,A" string
                color_str = f"{color_tuple[0]},{color_tuple[1]},{color_tuple[2]},{color_tuple[3]}"
                row.append(color_str)

            writer.writerow(row)

    print(f"Color data successfully written to {csv_file_path}")


def build_prcp(raw_path, processed_path):
    """
    Create precipitation thresholds and store color-coded CSV.
    """
    prcp_id = "prcp"
    raw_prcp_path = f"{raw_path}/Illinois_prcp_risks_round.json"

    # Build the threshold
    prcp_threshold = build_threshold_rgba(prcp_domain_mm, prcp_colors)

    # Optionally, if you still want the numeric CSV:
    # json_to_csv_with_timestamps(raw_prcp_path, f"{processed_path}/pt_prcp_values.csv")

    # Then build the color-coded CSV:
    json_to_csv_with_timestamps_colors(
        raw_prcp_path,
        f"{processed_path}/pt_prcp_colors.csv",
        prcp_threshold
    )

    # If you had some extra processing, e.g., process_climate_points_files(...), you could do that here:
    # process_climate_points_files(
    #     raw_prcp_path,
    #     processed_path,
    #     prcp_id,
    #     prcp_threshold,
    #     True,
    #     True
    # )


def build_tmin(raw_path, processed_path):
    """
    Create minimum temperature thresholds and store color-coded CSV.
    """
    min_temp_id = "tmin"
    raw_min_temp_path = f"{raw_path}/Illinois_tmin_round.json"

    # Build the threshold
    min_temp_threshold = build_threshold_rgba(min_temp_domain, min_temp_colors)

    # Optionally, if you still want numeric CSV:
    # json_to_csv_with_timestamps(raw_min_temp_path, f"{processed_path}/pt_tmin_values.csv")

    # Then build the color-coded CSV:
    json_to_csv_with_timestamps_colors(
        raw_min_temp_path,
        f"{processed_path}/pt_tmin_colors.csv",
        min_temp_threshold
    )


def build_tmax(raw_path, processed_path):
    """
    Create maximum temperature thresholds and store color-coded CSV.
    """
    max_temp_id = "tmax"
    raw_max_temp_path = f"{raw_path}/Illinois_tmax_round.json"

    # Build the threshold
    max_temp_threshold = build_threshold_rgba(max_temp_domain, max_temp_colors)

    # Optionally, if you still want numeric CSV:
    # json_to_csv_with_timestamps(raw_max_temp_path, f"{processed_path}/pt_tmax_values.csv")

    # Then build the color-coded CSV:
    json_to_csv_with_timestamps_colors(
        raw_max_temp_path,
        f"{processed_path}/pt_tmax_colors.csv",
        max_temp_threshold
    )


if __name__ == "__main__":
    # Adjust these paths as needed
    raw_path = "./raw_files"
    processed_path = "./processed_files/climate"

    # Build color-coded CSVs for precipitation, Tmin, Tmax
    build_prcp(raw_path, processed_path)
    build_tmin(raw_path, processed_path)
    build_tmax(raw_path, processed_path)
