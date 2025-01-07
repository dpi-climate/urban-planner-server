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

def process_climate_agg_files(raw_file_path, boundary_json_file_path, boundary_feature_id, final_path, prefix, extension, var_id, var_threshold):
    points_gdf = gpd.read_file(raw_file_path)
    boundary_gdf = gpd.read_file(boundary_json_file_path)
    boundary_gdf.rename(columns={boundary_feature_id: 'UNITID'}, inplace=True)

    if points_gdf.crs != boundary_gdf.crs:
        points_gdf = points_gdf.to_crs(boundary_gdf.crs)

    sample_properties = points_gdf.iloc[0].drop(labels='geometry').to_dict()
    time_stamp_keys = sorted([key for key in sample_properties.keys() if key.isdigit()])

    print(f"Processing variable '{var_id}' for time stamps: {', '.join(time_stamp_keys)}")

    for time_stamp in time_stamp_keys:
        # Select the value column for the current time stamp
        if time_stamp not in points_gdf.columns:
            print(f"Time stamp '{time_stamp}' not found in {raw_file_path}. Skipping year.")
            continue

        df_time_stamp = points_gdf[['geometry', time_stamp]].copy()
        df_time_stamp = df_time_stamp.dropna(subset=[time_stamp])

        try:
            # joined = gpd.sjoin(df_time_stamp, boundary_gdf[['UNITID', 'geometry']], how='inner', predicate='within')
            joined = gpd.sjoin(df_time_stamp, boundary_gdf, how='inner', predicate='within')

        except Exception as e:
            print(f"Error during spatial join for {var_id} {time_stamp}: {e}")
            continue

        grouped = joined.groupby('UNITID')[time_stamp].mean().reset_index()
        grouped.rename(columns={time_stamp: 'value'}, inplace=True)

        # Assign colors based on average values
        grouped['color'] = grouped['value'].apply(lambda x: get_color_for_value(var_threshold, x))

        # Merge with boundary_gdf to get geometries
        grouped = grouped.merge(boundary_gdf[['UNITID', 'geometry']], on='UNITID', how='left')

        filename = f"{prefix}_{var_id}_{time_stamp}.{extension}"
        output_path = os.path.join(final_path, filename)
        
        if extension == "geojson":
            # Convert to GeoDataFrame
            geojson_gdf = gpd.GeoDataFrame(grouped, geometry='geometry')

            # Define properties for GeoJSON
            geojson_gdf['color'] = geojson_gdf['color'].apply(lambda c: f"rgba({c[0]}, {c[1]}, {c[2]}, {c[3]})")
            geojson_gdf = geojson_gdf[['UNITID', 'value', 'color', 'geometry']]           

            # Save to GeoJSON
            try:
                geojson_gdf.to_file(output_path, driver='GeoJSON')
                print(f"Saved GeoJSON data for {var_id} {time_stamp} to {output_path}")
            
            except IOError as e:
                print(f"Failed to save GeoJSON data to {output_path}: {e}")
        
        elif extension == "pickle":
            # Convert geometries to GeoJSON-like dicts
            grouped['geometry'] = grouped['geometry'].apply(lambda geom: mapping(geom))

            # Prepare the binary data
            binary_data = {
                "features": grouped[['UNITID', 'value', 'color', 'geometry']].to_dict(orient='records')
            }

            # # Define the filename
            # output_name = f"ct_{var_id}_{time_stamp}.pickle"
            # output_path = os.path.join(final_path, output_name)

            # Save the binary data using pickle
            try:
                with open(output_path, 'wb') as pf:
                    pickle.dump(binary_data, pf)
                print(f"Saved binary data for {var_id} {time_stamp} to {output_path}")
            
            except IOError as e:
                print(f"Failed to save binary data to {output_path}: {e}")


def process_tmin(pa, pr):
    tmin_id = "tmin"
    tmin_raw_data_path = f"{raw_path}/Illinois_tmin_round.json"
    tmin_threshold = build_threshold_rgba(min_temp_domain, min_temp_colors)

    start = time.time()

    process_climate_agg_files(
        tmin_raw_data_path, 
        pa,
        feature_id,
        processed_path,
        pr,
        final_extension,
        tmin_id,
        tmin_threshold
    )

    end = time.time()
    elapsed_time = end - start

    print(f"Elapsed time for tmin: {elapsed_time:.2f} seconds")

def process_tmax(pa, pr):
    tmax_id = "tmax"
    tmax_raw_data_path = f"{raw_path}/Illinois_tmax_round.json"
    tmax_threshold = build_threshold_rgba(max_temp_domain, max_temp_colors)

    start = time.time()

    process_climate_agg_files(
        tmax_raw_data_path, 
        pa,
        feature_id,
        processed_path,
        pr,
        final_extension,
        tmax_id,
        tmax_threshold
    )

    end = time.time()
    elapsed_time = end - start

    print(f"Elapsed time for tmax: {elapsed_time:.2f} seconds")

def process_prcp(pa, pr):
    prcp_id = "prcp"
    prcp_raw_data_path = f"{raw_path}/Illinois_prcp_risks_round.json"
    prcp_threshold = build_threshold_rgba(prcp_domain_mm, prcp_colors)

    start = time.time()

    process_climate_agg_files(
        prcp_raw_data_path, 
        pa,
        feature_id,
        processed_path,
        pr,
        final_extension,
        prcp_id,
        prcp_threshold
    )

    end = time.time()
    elapsed_time = end - start

    print(f"Elapsed time for tmin: {elapsed_time:.2f} seconds")

if __name__ == "__main__":
    raw_path = "./raw_files"
    processed_path = "./processed_files/climate"
    final_extension = "pickle"

    # #######################################################
    # County
    geojson_path = f"{raw_path}/IL_BNDY_County_Py.json"
    final_prefix = "co"
    feature_id = "COUNTY_NAM"

    process_prcp(geojson_path, final_prefix)
    process_tmin(geojson_path, final_prefix)
    process_tmax(geojson_path, final_prefix)


    # # #######################################################

    # # Census Tract
    # geojson_path = f"{raw_path}/tl_2023_17_tract.json"
    # final_prefix = "ct"
    # feature_id = "GEOID"

    # process_prcp(geojson_path, final_prefix)
    # process_tmin(geojson_path, final_prefix)
    # process_tmax(geojson_path, final_prefix)

    # # #######################################################
    # # Block Level

    # geojson_path = f"{raw_path}/tl_2023_17_bg.json"
    # feature_id = "GEOID"
    # final_prefix = "bg"

    # process_prcp(geojson_path, final_prefix)
    # process_tmin(geojson_path, final_prefix)
    # process_tmax(geojson_path, final_prefix)

