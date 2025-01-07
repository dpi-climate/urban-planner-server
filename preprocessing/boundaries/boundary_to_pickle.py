import json
import pickle
import geopandas as gpd
from shapely.geometry import mapping

def backup_geojson_to_pickle(input_geojson_path, output_pickle_path):
    """
    Convert a GeoJSON file to a pickle format retaining only the GEOID property.
    
    Args:
        input_geojson_path (str): Path to the input GeoJSON file.
        output_pickle_path (str): Path to the output pickle file.
    """
    try:
        # Load the GeoJSON file
        with open(input_geojson_path, 'r') as geojson_file:
            geojson_data = json.load(geojson_file)
        
        # Process features to keep only the GEOID property
        processed_features = [
            {
                "type": feature["type"],
                "geometry": feature["geometry"],
                "properties": {"GEOID": feature["properties"]["GEOID"]},
            }
            for feature in geojson_data.get("features", [])
        ]
        
        # Create the processed GeoJSON structure
        processed_geojson = {
            "type": geojson_data["type"],
            "features": processed_features,
        }
        
        # Save the processed GeoJSON as a pickle file
        with open(output_pickle_path, 'wb') as pickle_file:
            pickle.dump(processed_geojson, pickle_file)
        
        print(f"GeoJSON data successfully converted to pickle format: {output_pickle_path}")
    except KeyError as e:
        print(f"KeyError: {e}. Ensure all features have the 'GEOID' property.")
    except Exception as e:
        print(f"An error occurred: {e}")

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
    

if __name__ == "__main__":
    raw_path = "./raw_files"
    processed_path = "./processed_files/boundaries"

    # ##########################################################
    
    # input_geojson = f"{raw_path}/tl_2023_17_tract_no_lake.json"
    # output_pickle = f"{processed_path}/bound_ct.pickle"

    # feature_id = "GEOID"
    
    # working(input_geojson, output_pickle, feature_id)

    # ##########################################################

    # input_geojson = f"{raw_path}/tl_2023_17_bg_no_lake.json"
    # output_pickle = f"{processed_path}/bound_bg.pickle"

    # feature_id = "GEOID"

    # working(input_geojson, output_pickle, feature_id)

    ##########################################################

    input_geojson = f"{raw_path}/IL_BNDY_County_Py.json"
    output_pickle = f"{processed_path}/bound_co.pickle"

    feature_id = "COUNTY_NAM"

    working(input_geojson, output_pickle, feature_id)


