import pandas as pd
import geopandas as gpd
from shapely.geometry import mapping
import pickle
from consts import raw_files_dir, processed_socio_dir, socio_domain, socio_colors
from shapely.geometry.base import BaseGeometry
import matplotlib.pyplot as plt
from shapely.geometry import shape

def plot_pickle(file_path, prop_key, agg_key):

    # Load the Pickle file
    with open(file_path, 'rb') as f:
        data = pickle.load(f)

    # Convert the data back to a GeoDataFrame
    records = data[prop_key]
    geometries = [shape(record['geometry']) for record in records]
    values = [record[agg_key] for record in records]

    gdf = gpd.GeoDataFrame({agg_key: values}, geometry=geometries)

    fig, ax = plt.subplots(figsize=(10, 10))
    gdf.plot(ax=ax, column=agg_key, cmap='coolwarm', legend=True)

    # Add title and axis labels
    ax.set_title("Title", fontsize=15)
    ax.set_xlabel("Longitude")
    ax.set_ylabel("Latitude")

    plt.show()

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
    if value is None:
        return (255, 255, 255)  # White color
    
    if not isinstance(value, (int, float)):
        # Fully transparent
        return (0, 0, 0, 0)

    for threshold in var_threshold:
        if value <= threshold["value"]:
            return threshold["color"]
    # If value exceeds all var_threshold, return the last color
    return var_threshold[-1]["color"]

def save_file(data, file_name):
    def safe_mapping(geom):
        # Check if geom is a valid shapely geometry
        if isinstance(geom, BaseGeometry) and geom.is_valid:
            return mapping(geom)
        # If not valid, return None or some placeholder
        return None
    
    if 'geometry' in data.columns:
        # Create a copy to avoid SettingWithCopyWarning
        data = data.copy()
        
        data['geometry'] = data['geometry'].apply(safe_mapping)
    
    binary_data = {
        "features": data[['UNITID', 'value', 'color', 'geometry']].to_dict(orient='records')
    }

    output_path = f"{processed_socio_dir}/{file_name}.pickle"

    try:
        with open(output_path, 'wb') as pf:
            pickle.dump(binary_data, pf)
        print(f"Saved binary data for {file_name} to {output_path}")
    except IOError as e:
        print(f"Failed to save binary data to {output_path}: {e}")

def build_pickle(csv_file, raw_gdf, prefix, geo_feature_id, csv_feature_id, threshold):
    
    df = pd.read_csv(
        csv_file,
        delimiter=',',
        encoding='utf-8',
    )

    df.rename(columns={csv_feature_id: geo_feature_id}, inplace=True)
    raw_gdf[geo_feature_id] = raw_gdf[geo_feature_id].astype(str)
    df[geo_feature_id] = df[geo_feature_id].astype(str)

    merged_df = raw_gdf.merge(df, on=geo_feature_id, how="left")

    filtered_df = merged_df[
        [geo_feature_id, "geometry", "RPL_THEME1", "RPL_THEME2", "RPL_THEME3", "RPL_THEME4", "RPL_THEMES"]
    ].copy()

    filtered_df.rename(columns={geo_feature_id: "UNITID"}, inplace=True)

    for col in filtered_df.columns[2:]:
        final_df = filtered_df[["UNITID", "geometry", col]].copy()
        final_df.rename(columns={col: "value"}, inplace=True)

        final_gdf = gpd.GeoDataFrame(final_df, geometry='geometry')
        
        final_gdf.loc[:, 'value'] = final_gdf['value'].apply(
            lambda x: None if pd.notnull(x) and x < 0 else x
        )

        # Assign colors based on the value, where None results in white
        final_gdf.loc[:, "color"] = final_gdf['value'].apply(lambda x: get_color_for_value(threshold, x))

        save_file(final_gdf, f"{prefix}_{col}")


def preprocess_co(geo_file):
    raw_gdf = gpd.read_file(geo_file)

    raw_gdf["CO_FIPS"] = raw_gdf["CO_FIPS"].astype(str)
    raw_gdf["CO_FIPS"] = "17" + raw_gdf["CO_FIPS"]

    return


if __name__ == "__main__":

    socio_threshold = build_threshold_rgba(socio_domain, socio_colors)

    ct_geojson = f"{raw_files_dir}/tl_2023_17_tract_no_lake.json"
    svi_ct_csv_file = f"{raw_files_dir}/sociodemographic/svi/svi_illinois_ct.csv"
    ct_feature_id = "GEOID"
    svi_feature_id = "FIPS"

    ct_gdf = gpd.read_file(ct_geojson)


    build_pickle(svi_ct_csv_file, ct_gdf, "ct", ct_feature_id, svi_feature_id, socio_threshold)

    co_geojson = f"{raw_files_dir}/IL_BNDY_County_Py.json"
    svi_co_csv_file = f"{raw_files_dir}/sociodemographic/svi/svi_illinois_co.csv"
    co_feature_id = "CO_FIPS"
    svi_feature_id = "FIPS"

    co_gdf = gpd.read_file(co_geojson)

    co_gdf["CO_FIPS"] = co_gdf["CO_FIPS"].astype(str)
    co_gdf["CO_FIPS"] = co_gdf["CO_FIPS"].str.zfill(3)

    co_gdf["CO_FIPS"] = "17" + co_gdf["CO_FIPS"]


    build_pickle(svi_co_csv_file, co_gdf, "co", co_feature_id, svi_feature_id, socio_threshold)

    # plot_pickle(
    #     f"C:/Users/carolvfs/Documents/GitHub/urban-planner-server/processed_files/socio/co_RPL_THEME1.pickle",
    #     "features",
    #     "value"
    # )


