import os
import geopandas as gpd
import pickle
from shapely.ops import nearest_points
from shapely.geometry import mapping
import pandas as pd
import time
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

def find_nearest(point, points):
    """
    Find the nearest point from a collection of points to the given point.
    """
    nearest_geom = nearest_points(point, points.unary_union)[1]
    return points.loc[points['geometry'] == nearest_geom].iloc[0]

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

def process_climate_agg_files_combined_shapefile(raw_file_path, boundary_json_file_path, boundary_feature_id, final_path, 
                                                 prefix, var_id, var_threshold):

    # Load point and boundary data
    points_gdf = gpd.read_file(raw_file_path)
    boundary_gdf = gpd.read_file(boundary_json_file_path)
    boundary_gdf.rename(columns={boundary_feature_id: 'UNITID'}, inplace=True)

    # Ensure CRS compatibility
    if points_gdf.crs != boundary_gdf.crs:
        points_gdf = points_gdf.to_crs(boundary_gdf.crs)

    # Identify timestamp keys from the points GeoDataFrame
    sample_properties = points_gdf.iloc[0].drop(labels='geometry').to_dict()
    time_stamp_keys = sorted([key for key in sample_properties.keys() if key.isdigit()])
    print(f"Processing variable '{var_id}' for time stamps: {', '.join(time_stamp_keys)}")

    # Initialize the base GeoDataFrame with boundary geometries and UNITID
    combined_gdf = boundary_gdf[['UNITID', 'geometry']].copy()

    # Iterate over each timestamp and compute aggregated values
    for time_stamp in time_stamp_keys:
        if time_stamp not in points_gdf.columns:
            print(f"Time stamp '{time_stamp}' not found in {raw_file_path}. Skipping this timestamp.")
            continue

        # Filter out rows with NaN values for the current timestamp
        df_time_stamp = points_gdf[['geometry', time_stamp]].dropna(subset=[time_stamp]).copy()

        try:
            # Spatial join between timestamp-specific points and boundaries
            joined = gpd.sjoin(df_time_stamp, boundary_gdf, how='inner', predicate='within')
        except Exception as e:
            print(f"Error during spatial join for {var_id} {time_stamp}: {e}")
            continue

        # Group by boundary UNITID and calculate mean for the timestamp
        grouped = joined.groupby('UNITID')[time_stamp].mean().reset_index()
        # Use a shorter column name because shapefile field names are limited to 10 characters
        # value_col = f"val_{time_stamp}"
        value_col = time_stamp
        # color_col = f"col_{time_stamp}"

        # grouped.rename(columns={time_stamp: value_col}, inplace=True)

        # # Assign colors based on average values for the current timestamp
        # grouped[color_col] = grouped[value_col].apply(
        #     lambda x: get_color_for_value(var_threshold, x)
        # )

        # # Convert RGBA tuples to string format if needed 
        # grouped[color_col] = grouped[color_col].apply(
        #     lambda c: f"rgba({c[0]}, {c[1]}, {c[2]}, {c[3]})" if isinstance(c, (list, tuple)) else c
        # )

        # Merge the results for the current timestamp into the combined GeoDataFrame
        # combined_gdf = combined_gdf.merge(grouped[['UNITID', value_col, color_col]],
        #                                   on='UNITID', how='left')

        combined_gdf = combined_gdf.merge(grouped[['UNITID', value_col]],
                                          on='UNITID', how='left')

    # Create a GeoDataFrame from combined_gdf (if not already one)
    combined_shapefile_gdf = gpd.GeoDataFrame(combined_gdf, geometry='geometry')

    # Define the output file path for a Shapefile
    output_filename = f"{prefix}_{var_id}.shp"
    output_path = os.path.join(final_path, output_filename)

    # Save the combined GeoDataFrame to a Shapefile
    try:
        combined_shapefile_gdf.to_file(output_path, driver='ESRI Shapefile')
        print(f"Saved combined Shapefile data for {var_id} to {output_path}")
    except Exception as e:
        print(f"Failed to save combined Shapefile data to {output_path}: {e}")


def process_tmin(pa, pr, feature_id):
    tmin_id = "tmin"
    tmin_raw_data_path = f"{raw_path}/Illinois_tmin_round.json"
    tmin_threshold = build_threshold_rgba(min_temp_domain, min_temp_colors)

    start = time.time()

    process_climate_agg_files_combined_shapefile(
        tmin_raw_data_path, 
        pa,
        feature_id,
        processed_path,
        pr,
        tmin_id,
        tmin_threshold
    )

    end = time.time()
    elapsed_time = end - start

    print(f"Elapsed time for tmin: {elapsed_time:.2f} seconds")

def process_tmax(pa, pr, feature_id):
    tmax_id = "tmax"
    tmax_raw_data_path = f"{raw_path}/Illinois_tmax_round.json"
    tmax_threshold = build_threshold_rgba(max_temp_domain, max_temp_colors)

    start = time.time()

    process_climate_agg_files_combined_shapefile(
        tmax_raw_data_path, 
        pa,
        feature_id,
        processed_path,
        pr,
        tmax_id,
        tmax_threshold
    )

    end = time.time()
    elapsed_time = end - start

    print(f"Elapsed time for tmax: {elapsed_time:.2f} seconds")

def process_prcp(pa, pr, feature_id):
    prcp_id = "prcp"
    prcp_raw_data_path = f"{raw_path}/Illinois_prcp_risks_round.json"
    prcp_threshold = build_threshold_rgba(prcp_domain_mm, prcp_colors)

    start = time.time()

    process_climate_agg_files_combined_shapefile(
        prcp_raw_data_path, 
        pa,
        feature_id,
        processed_path,
        pr,
        prcp_id,
        prcp_threshold
    )

    end = time.time()
    elapsed_time = end - start

    print(f"Elapsed time for tmin: {elapsed_time:.2f} seconds")


def build_ct_layers():
    geojson_path = f"{raw_path}/tl_2023_17_tract_no_lake.json"
    final_prefix = "ct"
    feature_id = "GEOID"

    process_prcp(geojson_path, final_prefix, feature_id)
    process_tmin(geojson_path, final_prefix, feature_id)
    process_tmax(geojson_path, final_prefix, feature_id)

def build_bg_layers():
    geojson_path = f"{raw_path}/tl_2023_17_bg_no_lake.json"
    feature_id = "GEOID"
    final_prefix = "bg"

    # process_prcp(geojson_path, final_prefix, feature_id)
    # process_tmin(geojson_path, final_prefix, feature_id)
    process_tmax(geojson_path, final_prefix, feature_id)

def build_co_layers():
    geojson_path = f"{raw_path}/IL_BNDY_County_Py.json"
    final_prefix = "co"
    feature_id = "COUNTY_NAM"

    process_prcp(geojson_path, final_prefix, feature_id)
    process_tmin(geojson_path, final_prefix, feature_id)
    process_tmax(geojson_path, final_prefix, feature_id)



if __name__ == "__main__":
    raw_path = "./raw_files"
    processed_path = "./processed_files/climate"

    # Census Tract
    # build_ct_layers()
    
    # Block Level
    build_bg_layers()

    # County
    # build_co_layers()



