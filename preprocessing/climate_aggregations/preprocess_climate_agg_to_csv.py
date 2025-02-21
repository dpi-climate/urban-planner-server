import os
import geopandas as gpd
from shapely.ops import nearest_points
from shapely.geometry import mapping
import pandas as pd
import time
from consts import min_temp_domain, min_temp_colors, max_temp_domain, max_temp_colors, prcp_domain_mm, prcp_colors
import json

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

def process_climate_agg_files_old(raw_file_path, boundary_json_file_path, boundary_feature_id, final_path, prefix, extension, var_id, var_threshold):

    # Read input files
    points_gdf = gpd.read_file(raw_file_path)
    boundary_gdf = gpd.read_file(boundary_json_file_path)
    boundary_gdf.rename(columns={boundary_feature_id: 'UNITID'}, inplace=True)

    # Ensure both GeoDataFrames use the same CRS
    if points_gdf.crs != boundary_gdf.crs:
        points_gdf = points_gdf.to_crs(boundary_gdf.crs)

    # Identify time stamp columns assuming they are numeric strings
    sample_properties = points_gdf.iloc[0].drop(labels='geometry').to_dict()
    time_stamp_keys = sorted([key for key in sample_properties.keys() if key.isdigit()])

    print(f"Processing variable '{var_id}' for time stamps: {', '.join(time_stamp_keys)}")

    # List to accumulate CSV data for each time stamp
    csv_data_accumulator = []

    for time_stamp in time_stamp_keys:
        # Select the value column for the current time stamp
        if time_stamp not in points_gdf.columns:
            print(f"Time stamp '{time_stamp}' not found in {raw_file_path}. Skipping this time stamp.")
            continue

        df_time_stamp = points_gdf[['geometry', time_stamp]].copy()
        df_time_stamp = df_time_stamp.dropna(subset=[time_stamp])

        try:
            joined = gpd.sjoin(df_time_stamp, boundary_gdf, how='inner', predicate='within')
        except Exception as e:
            print(f"Error during spatial join for {var_id} {time_stamp}: {e}")
            continue

        # Group by UNITID and compute the mean value
        grouped = joined.groupby('UNITID')[time_stamp].mean().reset_index()
        grouped.rename(columns={time_stamp: 'value'}, inplace=True)

        # Assign colors based on average values
        grouped['color'] = grouped['value'].apply(lambda x: get_color_for_value(var_threshold, x))

        # Merge with boundary to retrieve geometries
        grouped = grouped.merge(boundary_gdf[['UNITID', 'geometry']], on='UNITID', how='left')

        # Add a column for the current time stamp so that we can distinguish records
        grouped['time_stamp'] = time_stamp

        # Convert geometry to WKT for CSV compatibility
        grouped['geometry'] = grouped['geometry'].apply(lambda geom: geom.wkt if geom is not None else None)

        # Collect the processed data
        csv_data_accumulator.append(grouped)

    # After processing all time stamps, concatenate all data into a single DataFrame
    if csv_data_accumulator:
        final_csv_df = gpd.pd.concat(csv_data_accumulator, ignore_index=True)

        # Filter columns to only UNITID, geometry, color, time_stamp
        final_csv_df = final_csv_df[['UNITID', 'geometry', 'color', 'time_stamp']]

        # Construct a single filename for output CSV
        filename = f"{prefix}_{var_id}.csv"
        output_path = os.path.join(final_path, filename)

        try:
            # Save the combined DataFrame to CSV
            final_csv_df.to_csv(output_path, index=False)
            print(f"Saved combined CSV data for {var_id} to {output_path}")
        except IOError as e:
            print(f"Failed to save CSV data to {output_path}: {e}")
    else:
        print("No data was processed for any time stamps.")


def process_climate_agg_files_with_colors(raw_file_path, boundary_json_file_path, boundary_feature_id, final_path, prefix, extension, var_id, var_threshold):

    # Read input files
    points_gdf = gpd.read_file(raw_file_path)
    boundary_gdf = gpd.read_file(boundary_json_file_path)
    boundary_gdf.rename(columns={boundary_feature_id: 'UNITID'}, inplace=True)

    # Ensure both GeoDataFrames use the same CRS
    if points_gdf.crs != boundary_gdf.crs:
        points_gdf = points_gdf.to_crs(boundary_gdf.crs)

    # Identify time stamp columns assuming they are numeric strings
    sample_properties = points_gdf.iloc[0].drop(labels='geometry').to_dict()
    time_stamp_keys = sorted([key for key in sample_properties.keys() if key.isdigit()])

    print(f"Processing variable '{var_id}' for time stamps: {', '.join(time_stamp_keys)}")

    # List to accumulate data for each time stamp
    csv_data_accumulator = []

    for time_stamp in time_stamp_keys:
        # Select the value column for the current time stamp
        if time_stamp not in points_gdf.columns:
            print(f"Time stamp '{time_stamp}' not found in {raw_file_path}. Skipping this time stamp.")
            continue

        df_time_stamp = points_gdf[['geometry', time_stamp]].copy()
        df_time_stamp = df_time_stamp.dropna(subset=[time_stamp])

        try:
            joined = gpd.sjoin(df_time_stamp, boundary_gdf, how='inner', predicate='within')
        except Exception as e:
            print(f"Error during spatial join for {var_id} {time_stamp}: {e}")
            continue

        # Group by UNITID and compute the mean value
        grouped = joined.groupby('UNITID')[time_stamp].mean().reset_index()
        grouped.rename(columns={time_stamp: 'value'}, inplace=True)

        # Assign colors based on average values
        grouped['color'] = grouped['value'].apply(lambda x: get_color_for_value(var_threshold, x))

        # Merge with boundary to retrieve geometries
        grouped = grouped.merge(boundary_gdf[['UNITID', 'geometry']], on='UNITID', how='left')

        # Add a column for the current time stamp
        grouped['time_stamp'] = time_stamp

        # Convert geometry to WKT for CSV compatibility
        grouped['geometry'] = grouped['geometry'].apply(lambda geom: geom.wkt if geom is not None else None)

        # Append relevant columns to the accumulator
        csv_data_accumulator.append(grouped[['UNITID', 'geometry', 'color', 'time_stamp']])

    # After processing all time stamps, check if there is any data collected
    if not csv_data_accumulator:
        print("No data was processed for any time stamps.")
        return

    # Concatenate all accumulated data into a single DataFrame
    accumulated_df = gpd.pd.concat(csv_data_accumulator, ignore_index=True)

    # Pivot the DataFrame so each time_stamp becomes a separate column of colors
    pivot_df = accumulated_df.pivot_table(
        index=['UNITID', 'geometry'], 
        columns='time_stamp', 
        values='color', 
        aggfunc='first'
    ).reset_index()

    # After pivot, 'time_stamp' values become column headers.
    # The columns will be a MultiIndex if there are multiple value fields; 
    # but here we only pivoted on 'color', so columns should be flat except for the new time_stamp columns.
    # If necessary, flatten the columns (not strictly needed in this case):
    pivot_df.columns.name = None  # remove the aggregation axis name

    # Construct a single filename for output CSV
    filename = f"{prefix}_{var_id}.csv"
    output_path = os.path.join(final_path, filename)

    try:
        # Save the pivoted DataFrame to CSV
        pivot_df.to_csv(output_path, index=False)
        print(f"Saved combined CSV data for {var_id} to {output_path}")
    except IOError as e:
        print(f"Failed to save CSV data to {output_path}: {e}")

def process_climate_agg_files(raw_file_path, boundary_json_file_path, boundary_feature_id, final_path, prefix, extension, var_id, var_threshold):
    print(f"\n Processing {var_id}")

    # Read input files
    points_gdf = gpd.read_file(raw_file_path)
    boundary_gdf = gpd.read_file(boundary_json_file_path)
    boundary_gdf.rename(columns={boundary_feature_id: 'UNITID'}, inplace=True)

    # Ensure both GeoDataFrames use the same CRS
    if points_gdf.crs != boundary_gdf.crs:
        points_gdf = points_gdf.to_crs(boundary_gdf.crs)

    # Identify time stamp columns assuming they are numeric strings
    sample_properties = points_gdf.iloc[0].drop(labels='geometry').to_dict()
    time_stamp_keys = sorted([key for key in sample_properties.keys() if key.isdigit()])

    print(f"Processing variable '{var_id}' for time stamps: {', '.join(time_stamp_keys)}")

    # List to accumulate data for each time stamp
    csv_data_accumulator = []

    for time_stamp in time_stamp_keys:
        # Select the value column for the current time stamp
        if time_stamp not in points_gdf.columns:
            print(f"Time stamp '{time_stamp}' not found in {raw_file_path}. Skipping this time stamp.")
            continue

        df_time_stamp = points_gdf[['geometry', time_stamp]].copy()
        df_time_stamp = df_time_stamp.dropna(subset=[time_stamp])

        try:
            joined = gpd.sjoin(df_time_stamp, boundary_gdf, how='inner', predicate='within')
        except Exception as e:
            print(f"Error during spatial join for {var_id} {time_stamp}: {e}")
            continue

        # Group by UNITID and compute the mean value for the current time_stamp
        grouped = joined.groupby('UNITID')[time_stamp].mean().round(1).reset_index()
        grouped.rename(columns={time_stamp: 'value'}, inplace=True)

        # grouped['value'] = grouped['value'].apply(lambda x: get_color_for_value(var_threshold, x))

        # Merge with boundary to retrieve geometries
        grouped = grouped.merge(boundary_gdf[['UNITID', 'geometry']], on='UNITID', how='left')

        # Add a column for the current time stamp
        grouped['time_stamp'] = time_stamp

        # Convert geometry to WKT for CSV compatibility
        # grouped['geometry'] = grouped['geometry'].apply(lambda geom: geom.wkt if geom is not None else None)
        # Convert geometry to a GeoJSON dictionary, then serialize to JSON string
        grouped['geometry'] = grouped['geometry'].apply(
            lambda geom: json.dumps(mapping(geom)) if geom is not None else None
        )

        # Keep only relevant columns and accumulate data
        csv_data_accumulator.append(grouped[['UNITID', 'geometry', 'value', 'time_stamp']])

    # After processing all time stamps, check if there is any data collected
    if not csv_data_accumulator:
        print("No data was processed for any time stamps.")
        return

    # Concatenate all accumulated data into a single DataFrame
    accumulated_df = gpd.pd.concat(csv_data_accumulator, ignore_index=True)

    # Pivot the DataFrame so each time_stamp becomes a separate column of values
    pivot_df = accumulated_df.pivot_table(
        index=['UNITID', 'geometry'], 
        columns='time_stamp', 
        values='value', 
        aggfunc='first'
    ).reset_index()

    # Remove the columns axis name to flatten column headers if necessary
    pivot_df.columns.name = None

    # Construct a single filename for output CSV
    filename = f"{prefix}_{var_id}.csv"
    output_path = os.path.join(final_path, filename)

    try:
        # Save the pivoted DataFrame to CSV
        pivot_df.to_csv(output_path, index=False)
        print(f"Saved combined CSV data for {var_id} to {output_path}")
    except IOError as e:
        print(f"Failed to save CSV data to {output_path}: {e}")

def process_climate_agg_files_per_time_stamp(raw_file_path, boundary_json_file_path, boundary_feature_id, final_path, prefix, extension, var_id, var_threshold):
    import os
    import geopandas as gpd
    from shapely.geometry import mapping

    # Read input files
    points_gdf = gpd.read_file(raw_file_path)
    boundary_gdf = gpd.read_file(boundary_json_file_path)
    boundary_gdf.rename(columns={boundary_feature_id: 'UNITID'}, inplace=True)

    # Ensure both GeoDataFrames use the same CRS
    if points_gdf.crs != boundary_gdf.crs:
        points_gdf = points_gdf.to_crs(boundary_gdf.crs)

    # Identify time stamp columns assuming they are numeric strings
    sample_properties = points_gdf.iloc[0].drop(labels='geometry').to_dict()
    time_stamp_keys = sorted([key for key in sample_properties.keys() if key.isdigit()])

    print(f"Processing variable '{var_id}' for time stamps: {', '.join(time_stamp_keys)}")

    for time_stamp in time_stamp_keys:
        # Select the value column for the current time stamp
        if time_stamp not in points_gdf.columns:
            print(f"Time stamp '{time_stamp}' not found in {raw_file_path}. Skipping this time stamp.")
            continue

        df_time_stamp = points_gdf[['geometry', time_stamp]].copy()
        df_time_stamp = df_time_stamp.dropna(subset=[time_stamp])

        try:
            joined = gpd.sjoin(df_time_stamp, boundary_gdf, how='inner', predicate='within')
        except Exception as e:
            print(f"Error during spatial join for {var_id} {time_stamp}: {e}")
            continue

        # Group by UNITID and compute the mean value for the current time_stamp
        grouped = joined.groupby('UNITID')[time_stamp].mean().reset_index()
        grouped.rename(columns={time_stamp: 'value'}, inplace=True)

        # Merge with boundary to retrieve geometries
        grouped = grouped.merge(boundary_gdf[['UNITID', 'geometry']], on='UNITID', how='left')

        # Add a column for the current time stamp
        grouped['time_stamp'] = time_stamp

        # Convert geometry to WKT for CSV compatibility
        grouped['geometry'] = grouped['geometry'].apply(lambda geom: geom.wkt if geom is not None else None)

        # Construct the filename for the current timestamp
        output_filename = f"{prefix}_{var_id}_{time_stamp}.csv"
        output_path = os.path.join(final_path, output_filename)

        try:
            # Save the data for the current time stamp to CSV
            grouped.to_csv(output_path, index=False)
            print(f"Saved data for {var_id} time stamp '{time_stamp}' to {output_path}")
        except IOError as e:
            print(f"Failed to save CSV for {time_stamp} to {output_path}: {e}")

    print("Processing completed.")


def process_tmin(pa, pr, feature_id):
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
    elapsed_time = (end - start)/60

    print(f"Elapsed time for tmin: {elapsed_time:.2f} minute(s)")

def process_tmax(pa, pr, feature_id):
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
    elapsed_time = (end - start)/60

    print(f"Elapsed time for tmax: {elapsed_time:.2f} minute(s)")

def process_prcp(pa, pr, feature_id):
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
    elapsed_time = (end - start)/60

    print(f"Elapsed time for prcp: {elapsed_time:.2f} minute(s)")


def build_ct_layers():
    print("")
    print("Building ct layers")
    geojson_path = f"{raw_path}/tl_2023_17_tract_no_lake.json"
    final_prefix = "ct"
    feature_id = "GEOID"

    process_prcp(geojson_path, final_prefix, feature_id)
    process_tmin(geojson_path, final_prefix, feature_id)
    process_tmax(geojson_path, final_prefix, feature_id)

def build_bg_layers():
    print("")
    print("Building bg layers")
    geojson_path = f"{raw_path}/tl_2023_17_bg_no_lake.json"
    feature_id = "GEOID"
    final_prefix = "bg"

    process_prcp(geojson_path, final_prefix, feature_id)
    process_tmin(geojson_path, final_prefix, feature_id)
    process_tmax(geojson_path, final_prefix, feature_id)

def build_co_layers():
    print("")
    print("Building co layers")
    geojson_path = f"{raw_path}/IL_BNDY_County_Py.json"
    final_prefix = "co"
    feature_id = "COUNTY_NAM"

    process_prcp(geojson_path, final_prefix, feature_id)
    process_tmin(geojson_path, final_prefix, feature_id)
    process_tmax(geojson_path, final_prefix, feature_id)



if __name__ == "__main__":
    raw_path = "./raw_files"
    processed_path = "./processed_files/climate"
    # final_extension = "pickle"
    final_extension = "csv"

    # County
    build_co_layers()
    
    # Census Tract
    build_ct_layers()
    
    # Block Level
    build_bg_layers()




