import geopandas as gpd
import pandas as pd
from shapely.geometry import Point, shape
import polars as pl
import matplotlib.pyplot as plt
from shapely.wkt import loads
from shapely.ops import nearest_points
from scipy.spatial import cKDTree
import numpy as np

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

def find_nearest_bulk(points_gdf, polygons_gdf):
    # Extract point coordinates and ensure they are finite
    point_coords = np.array(list(zip(points_gdf.geometry.x, points_gdf.geometry.y)))
    point_coords = point_coords[np.isfinite(point_coords).all(axis=1)]  # Filter out invalid values

    # Extract polygon centroid coordinates
    polygon_coords = np.array(list(zip(polygons_gdf.geometry.centroid.x, polygons_gdf.geometry.centroid.y)))

    # Build KDTree for points
    tree = cKDTree(point_coords)

    # Query nearest points for each polygon centroid
    distances, indices = tree.query(polygon_coords)
    return indices

def build_file():
    raw_path = "./raw_files"
    raw_data_path = f"{raw_path}/Illinois_prcp_risks_round.json"
    geojson_path = f"{raw_path}/tl_2023_17_bg_no_lake.json"
    # geojson_path = f"{raw_path}/IL_BNDY_County_Py.json"
    prcp_threshold = build_threshold_rgba(prcp_domain_mm, prcp_colors)
    boundary_feature_id = "COUNTY_NAM"
    boundary_feature_id = "GEOID"

    df_pts = pd.read_csv(f"{raw_path}/Illinois_prcp_risks_round.csv")
    df_pts["geometry"] = gpd.points_from_xy(df_pts["longitude"], df_pts["latitude"])

    boundary_gdf = gpd.read_file(geojson_path)
    boundary_gdf.rename(columns={boundary_feature_id: 'UNITID'}, inplace=True)

    df_pts_gdf = gpd.GeoDataFrame(df_pts, geometry="geometry", crs="EPSG:4326")  # Assuming WGS84
    df_pts_gdf = df_pts_gdf.to_crs(boundary_gdf.crs)
    original_crs = boundary_gdf.crs

    projected_crs = "EPSG:3857"
    df_pts_gdf = df_pts_gdf.to_crs(projected_crs)
    boundary_gdf = boundary_gdf.to_crs(projected_crs)

    time_stamp_keys = sorted([col for col in df_pts.columns if col.isdigit()])

    data_accumulator = []

    for time_stamp in time_stamp_keys:
    # for time_stamp in ["1980"]:

        df_pts_t = df_pts_gdf[["latitude", "longitude", "geometry", time_stamp]]

        joined = gpd.sjoin(df_pts_t, boundary_gdf, how="inner", predicate="within")

        missing_polygons = boundary_gdf[~boundary_gdf['UNITID'].isin(joined['UNITID'])]

        if not missing_polygons.empty:
            # Find nearest points in bulk
            nearest_indices = find_nearest_bulk(df_pts_t, missing_polygons)

            # Extract nearest point data
            nearest_points = df_pts_t.iloc[nearest_indices].reset_index(drop=True)
            nearest_points['UNITID'] = missing_polygons['UNITID'].values

            # Concatenate the new rows to the joined DataFrame
            joined = pd.concat([joined, nearest_points], ignore_index=True)

        # joined = joined.to_crs(original_crs)
        # boundary_gdf = boundary_gdf.to_crs(original_crs)

        grouped = joined.groupby('UNITID')[time_stamp].mean().reset_index()

        grouped.rename(columns={time_stamp: 'value'}, inplace=True)
        grouped['color'] = grouped['value'].apply(lambda x: get_color_for_value(prcp_threshold, x))

        grouped = grouped.merge(boundary_gdf[['UNITID', 'geometry']], on='UNITID', how='left')
        #######################################################################################
        #######################################################################################
        #######################################################################################

        grouped['time_stamp'] = time_stamp
        grouped['geometry'] = grouped['geometry'].apply(lambda geom: geom.wkt if geom is not None else None)
        
        data_accumulator.append(grouped[['UNITID', 'geometry', 'value', 'time_stamp']])

    accumulated_df = gpd.pd.concat(data_accumulator, ignore_index=True)

    pivot_df = accumulated_df.pivot_table(
            index=['UNITID', 'geometry'], 
            columns='time_stamp', 
            values='value', 
            aggfunc='first',
        ).reset_index()

    pivot_df.columns.name = None

    pivot_gdf = gpd.GeoDataFrame(
        pivot_df, 
        geometry=gpd.GeoSeries.from_wkt(pivot_df['geometry']), 
        crs=projected_crs
    )

    pivot_gdf = pivot_gdf.to_crs(original_crs)

    # pivot_gdf.to_parquet(f'./preprocessing/rebuild_climate_agg/all_no_null.parquet', compression='snappy')
    pivot_gdf.to_file('./preprocessing/rebuild_climate_agg/all_no_null.geojson', driver='GeoJSON')

    # memory_usage = grouped.memory_usage(deep=True).sum()
    # memory_in_mb = memory_usage / (1024 ** 2)
    # # print(memory_in_mb)

def read_gpd_parquet():
    # gdf = gpd.read_parquet('./preprocessing/rebuild_climate_agg/all_no_null.parquet')

    # gdf.plot(column='1980', cmap='viridis', legend=True, figsize=(10, 6))

    # # Add a title and labels
    # plt.title('Spatial Plot of Values')
    # plt.xlabel('Longitude')
    # plt.ylabel('Latitude')
    # plt.show()

    from shapely.geometry import box
    gdf = gpd.read_parquet('./preprocessing/rebuild_climate_agg/all_no_null.parquet')
    print(gdf)

    # bounding_box = [
    #     -88.3407821883814, 41.188423415530345, 
    #     -87.2932174068868, 42.40323025365792
    # ]

    bounding_box = [
        -87.79598408816868, 41.710310484530844, 
        -87.59510940377477, 42.08835044731295
    ]

    if bounding_box:

        filtered_gdf = gdf.cx[bounding_box[0]:bounding_box[2], bounding_box[1]:bounding_box[3]]

        # Plot the filtered data
        filtered_gdf.plot(column='1980', cmap='viridis', legend=True, figsize=(10, 6))
    
    else:
        gdf.plot(column='1980', cmap='viridis', legend=True, figsize=(10, 6))

    # Add a title and labels
    plt.title('Filtered Spatial Plot of Values')
    plt.xlabel('Longitude')
    plt.ylabel('Latitude')
    plt.show()

    # gdf.plot(column='1980', cmap='viridis', legend=True, figsize=(10, 6))

    # # Add a title and labels
    # plt.title('Spatial Plot of Values')
    # plt.xlabel('Longitude')
    # plt.ylabel('Latitude')
    # plt.show()

def read_parquet():
    
    df = pl.read_parquet('./preprocessing/rebuild_climate_agg/all_no_null.parquet')

    # Ensure your DataFrame has geometry and value columns
    # prop_key = "1980"  # The column with values
    prop_key = "1982"  # The column with values
    geometry_key = "geometry"  # The column with geometries
    agg_key = "value"  # Name for aggregated values in GeoDataFrame

    # (min_lon, min_lat, max_lon, max_lat)
    bounding_box = (-88.3407821883814, 41.188423415530345, -87.2932174068868, 42.40323025365792)

    # Convert to list for iteration
    records = df.to_dicts()

    # Extract geometries and values
    geometries = [loads(record[geometry_key]) for record in records]
    values = [record[prop_key] for record in records]

    for geom in geometries[:5]:  # Print bounds of the first 5 geometries
        print(geom.bounds)


    filtered_geometries = []
    filtered_values = []

    for geom, value in zip(geometries, values):
        if geom.bounds[0] >= bounding_box[0] and geom.bounds[2] <= bounding_box[2] and \
        geom.bounds[1] >= bounding_box[1] and geom.bounds[3] <= bounding_box[3]:
            filtered_geometries.append(geom)
            filtered_values.append(value)

    # Create GeoDataFrame
    # gdf = gpd.GeoDataFrame({agg_key: values}, geometry=geometries)
    gdf = gpd.GeoDataFrame({agg_key: filtered_values}, geometry=filtered_geometries)

    # Plot the data
    fig, ax = plt.subplots(figsize=(10, 10))
    gdf.plot(ax=ax, column=agg_key, cmap='coolwarm', legend=True)

    # Add title and axis labels
    ax.set_title("Title", fontsize=15)
    ax.set_xlabel("Longitude")
    ax.set_ylabel("Latitude")

    plt.show()

build_file()
# read_gpd_parquet()

