import json
import pickle
import geopandas as gpd
from shapely.geometry import mapping

def working(input_geojson_path, output_pickle_path, src_feature_id):
    gdf = gpd.read_file(input_geojson_path)
    gdf.rename(columns={src_feature_id: 'UNITID'}, inplace=True)

    gdf['geometry'] = gdf['geometry'].apply(lambda geom: mapping(geom))

    binary_data = {
        "features": gdf[['UNITID', 'geometry']].to_dict(orient='records')
    }

    try:
        with open(output_pickle_path, 'wb') as pf:
            pickle.dump(binary_data, pf)
        print(f"Saved binary data for {output_pickle_path}")
    
    except IOError as e:
        print(f"Failed to save binary data to {output_pickle_path}: {e}")
    

def build_census_tract_boundary():
    input_geojson = f"{raw_path}/tl_2023_17_tract_no_lake.json"
    output_pickle = f"{processed_path}/bound_ct.pickle"

    feature_id = "GEOID"
    
    working(input_geojson, output_pickle, feature_id)

def build_block_groups_boundary():
    input_geojson = f"{raw_path}/tl_2023_17_bg_no_lake.json"
    output_pickle = f"{processed_path}/bound_bg.pickle"

    feature_id = "GEOID"

    working(input_geojson, output_pickle, feature_id)

def build_county_boundary():
    input_geojson = f"{raw_path}/IL_BNDY_County_Py.json"
    output_pickle = f"{processed_path}/bound_co.pickle"

    feature_id = "COUNTY_NAM"

    working(input_geojson, output_pickle, feature_id)

if __name__ == "__main__":
    raw_path = "./raw_files"
    processed_path = "./processed_files/boundaries"

    # ##########################################################
    build_census_tract_boundary()
    build_block_groups_boundary()
    build_county_boundary()





