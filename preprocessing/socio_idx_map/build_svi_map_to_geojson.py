import pandas as pd
import geopandas as gpd
from shapely.geometry import mapping
import pickle
from consts import raw_files_dir, processed_socio_dir, socio_domain, socio_colors
from shapely.geometry.base import BaseGeometry
import matplotlib.pyplot as plt
from shapely.geometry import shape


def build_geojson(csv_file, raw_gdf, prefix, geo_feature_id, csv_feature_id, threshold):
    
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

        final_gdf.to_file(f"{processed_socio_dir}/{prefix}_{col.lower()}.geojson", driver="GeoJSON")


if __name__ == "__main__":

    # co_geojson = f"{raw_files_dir}/IL_BNDY_County_Py.json"
    # svi_co_csv_file = "C:/Users/carolvfs/Documents/GitHub/urban-planner-server/raw_files/sociodemographic/svi/svi_illinois_co.csv"
    # co_feature_id = "CO_FIPS"
    # svi_feature_id = "FIPS"
    # co_prefix = "co"

    # co_gdf = gpd.read_file(co_geojson)

    # co_gdf[co_feature_id] = co_gdf[co_feature_id].astype(str)
    # co_gdf[co_feature_id] = co_gdf[co_feature_id].str.zfill(3)

    # co_gdf[co_feature_id] = "17" + co_gdf[co_feature_id]

    # build_geojson(
    #     csv_file=svi_co_csv_file,
    #     raw_gdf=co_gdf,
    #     prefix="co",
    #     geo_feature_id=co_feature_id,
    #     csv_feature_id=svi_feature_id,
    #     threshold=None
    # )

    # COUNTIES
    
    co_gdf = gpd.read_file(f"{raw_files_dir}/tl_2023_17_tract_no_lake.json")

    co_gdf["CO_FIPS"] = co_gdf["CO_FIPS"].astype(str)
    co_gdf["CO_FIPS"] = co_gdf["CO_FIPS"].str.zfill(3)

    co_gdf["CO_FIPS"] = "17" + co_gdf["CO_FIPS"]
    
    build_geojson(
        csv_file="C:/Users/carolvfs/Documents/GitHub/urban-planner-server/raw_files/sociodemographic/svi/svi_illinois_co.csv",
        raw_gdf=co_gdf,
        prefix="co",
        geo_feature_id="CO_FIPS",
        csv_feature_id="FIPS",
        threshold=None
    )

    ###################################################################################################################

    # CENSUS TRACTS 
    
    ct_gdf = gpd.read_file(f"{raw_files_dir}/tl_2023_17_tract_no_lake.json")

    ct_gdf["GEOID"] = ct_gdf["GEOID"].astype(str)
    ct_gdf["GEOID"] = ct_gdf["GEOID"].str.zfill(3)
    
    build_geojson(
        csv_file="C:/Users/carolvfs/Documents/GitHub/urban-planner-server/raw_files/sociodemographic/svi/svi_illinois_ct.csv",
        raw_gdf=ct_gdf,
        prefix="ct",
        geo_feature_id="GEOID",
        csv_feature_id="FIPS",
        threshold=None
    )
    


