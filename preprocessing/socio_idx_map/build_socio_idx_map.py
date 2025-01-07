# Sociodemographic data
# Percent of population that is African American by County/Census Tract/Block
# Percent of population that is Hispanic by County/Census Tract/Block
# Hispanic population by race
# Percent of Population Living in Poverty by County/Census Tract/Block

# https://dph.illinois.gov/data-statistics/vital-statistics/illinois-population-data/population-race-ethnicity.html

import pandas as pd
import geopandas as gpd
from shapely.geometry import mapping
import pickle
from consts import raw_files_dir, processed_socio_dir, socio_vars


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


def save_file(data, file_name):
    data['geometry'] = data['geometry'].apply(lambda geom: mapping(geom))
    
    # Prepare the binary data
    binary_data = {
        "features": data.to_dict(orient='records')
    }

    output_path = f"{processed_socio_dir}/{file_name}.pickle"

    try:
        with open(output_path, 'wb') as pf:
            pickle.dump(binary_data, pf)
        print(f"Saved binary data for {file_name} to {output_path}")
    
    except IOError as e:
        print(f"Failed to save binary data to {output_path}: {e}")

def merge(raw_gdf, df, on_key):
    merged_gdf = raw_gdf.merge(df, on=on_key, how="left")
    return merged_gdf
    
def build_ct_pop_map(raw_gdf):

    ct_population_file = f"{raw_files_dir}/sociodemographic/ct_total_population/ACSDT5Y2023.B01003-Data.csv"
    ct_pop_df = pd.read_csv(ct_population_file, skiprows=[1])

    # Remove first part of GEO_ID number
    ct_pop_df["GEO_ID"] = ct_pop_df["GEO_ID"].str.replace("1400000US", "", regex=False)
    
    # Select columns
    ct_pop_df = ct_pop_df[["GEO_ID", "B01003_001E"]]

    # Rename GEO_ID column to GEOID
    ct_pop_df.rename(columns={"GEO_ID": "GEOID"}, inplace=True)

    # Merge
    merged_data = merge(raw_gdf, ct_pop_df, "GEOID")
    
    # Select columns
    merged_data = merged_data[["GEOID", "geometry", "B01003_001E"]]

    # Rename GEOID column
    merged_data.rename(columns={"GEOID": "UNITID"}, inplace=True)
    # print(merged_data)
    
    # Save
    save_file(merged_data, "ct_pop")

def build_ct_race_map(raw_gdf):
    ct_race_file = f"{raw_files_dir}/sociodemographic/ct_race_hispanic_not_hispanic/DECENNIALDHC2020.P9-Data.csv"
    ct_race_df = pd.read_csv(ct_race_file, skiprows=[1])
    
    # Remove first part of GEO_ID number
    ct_race_df["GEO_ID"] = ct_race_df["GEO_ID"].str.replace("1400000US", "", regex=False)
        
    # Rename GEO_ID column to GEOID
    ct_race_df.rename(columns={"GEO_ID": "GEOID"}, inplace=True)
    
    # Merge
    merged_data = merge(raw_gdf, ct_race_df, "GEOID")
    
    # Select columns
    merged_data = merged_data[["GEOID", "geometry", "P9_002N", "P9_003N", "P9_005N", "P9_006N", "P9_007N", "P9_008N", "P9_009N", "P9_010N"]]

    # Rename GEOID column
    merged_data.rename(columns={"GEOID": "UNITID"}, inplace=True)
    # print(merged_data)

    # Save
    save_file(merged_data, "ct_race")


if __name__ == "__main__":
    ct_geojson = f"{raw_files_dir}/tl_2023_17_tract.json"
    ct_gdf = gpd.read_file(ct_geojson)
    
    # build_ct_pop_map(ct_gdf)
    # build_ct_race_map(ct_gdf)

    # Plot pop
    path = f"{processed_socio_dir}/ct_pop.pickle"
    plot_pickle(
        f"{processed_socio_dir}/ct_pop.pickle",
        "features", 
        "B01003_001E"
    )

    # Plot race
    path = f"{processed_socio_dir}/ct_pop.pickle"
    plot_pickle(
        f"{processed_socio_dir}/ct_race.pickle",
        "features", 
        "P9_002N"
    )