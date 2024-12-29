import geopandas as gpd
import pandas as pd

# Function to convert GeoJSON to Feather
def geojson_to_feather(geojson_file: str, feather_file: str, include_geometry: bool = False, selected_columns: list = None):
    """
    Converts a GeoJSON file to Feather format.

    Parameters:
        geojson_file (str): Path to the input GeoJSON file.
        feather_file (str): Path to the output Feather file.
        include_geometry (bool): Whether to include geometry as WKT in the output.
    """
    try:
        # Load the GeoJSON file
        gdf = gpd.read_file(geojson_file)

        if include_geometry:
            # Convert geometry to WKT (if needed)
            gdf['geometry'] = gdf['geometry'].apply(lambda geom: geom.wkt if geom else None)
        else:
            # Drop geometry column if not needed
            gdf = gdf.drop(columns=['geometry'])

        # If selected_columns is provided, keep only those columns
        if selected_columns:
            missing_columns = [col for col in selected_columns if col not in gdf.columns]
            if missing_columns:
                raise ValueError(f"The following columns are missing in the GeoJSON: {missing_columns}")
            gdf = gdf[selected_columns]
        
        # Convert to a Pandas DataFrame
        df = pd.DataFrame(gdf)

        # Save the DataFrame to Feather format
        df.to_feather(feather_file)

        print(f"GeoJSON data successfully saved to Feather: {feather_file}")

    except Exception as e:
        print(f"An error occurred: {e}")


main_path = "./files"
geojson_file = f"{main_path}/Illinois_prcp_risks_round.json"
feather_file = f"{main_path}/Illinois_prcp_risks_round.feather"

selected_columns = ['risk_2yr (', 'risk_5yr (', 'risk_10yr', 'risk_25yr', 'risk_50yr', 'risk_100yr', 'risk_200yr', 'risk_500yr']

# geojson_to_feather(geojson_file, feather_file)
geojson_to_feather(geojson_file, feather_file, include_geometry=False, selected_columns=selected_columns)
