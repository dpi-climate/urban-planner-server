import geopandas as gpd
import pandas as pd

# Function to convert GeoJSON to Feather with optional latitude and longitude
def geojson_to_feather(
    geojson_file: str,
    feather_file: str,
    include_geometry: bool = False,
    include_lat_lon: bool = False,
    selected_columns: list = None
):
    """
    Converts a GeoJSON file to Feather format with optional geometry and latitude/longitude.

    Parameters:
        geojson_file (str): Path to the input GeoJSON file.
        feather_file (str): Path to the output Feather file.
        include_geometry (bool): Whether to include geometry as WKT in the output.
        include_lat_lon (bool): Whether to include latitude and longitude as separate columns.
        selected_columns (list): List of columns to include in the output. If None, all columns are included.
    """
    try:
        # Load the GeoJSON file
        gdf = gpd.read_file(geojson_file)

        # Initialize flags for geometry and lat/lon
        geometry_included = include_geometry
        lat_lon_included = include_lat_lon

        # Handle geometry inclusion
        if include_geometry:
            # Convert geometry to WKT
            gdf['geometry'] = gdf['geometry'].apply(lambda geom: geom.wkt if geom else None)
        else:
            # Drop geometry column if not needed
            gdf = gdf.drop(columns=['geometry'])

        # Handle latitude and longitude extraction
        if include_lat_lon:
            if 'geometry' not in gdf.columns:
                # Reload GeoJSON to access geometry
                gdf = gpd.read_file(geojson_file)
            
            # Check if geometries are points
            if gdf.geometry.type.unique().tolist() == ['Point']:
                gdf['longitude'] = gdf.geometry.x
                gdf['latitude'] = gdf.geometry.y
            else:
                # For non-point geometries, compute centroid
                gdf['centroid'] = gdf.geometry.centroid
                gdf['longitude'] = gdf.centroid.x
                gdf['latitude'] = gdf.centroid.y
                gdf = gdf.drop(columns=['centroid'])

            # Optionally drop the geometry column if not included
            if not include_geometry:
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


# Example usage
if __name__ == "__main__":
    main_path = "./files"
    geojson_file = f"{main_path}/Illinois_prcp_risks_round.json"
    feather_file = f"{main_path}/Illinois_prcp_risks_round.feather"

    selected_columns = [
        'risk_2yr (', 'risk_5yr (', 'risk_10yr',
        'risk_25yr', 'risk_50yr', 'risk_100yr',
        'risk_200yr', 'risk_500yr', 'latitude', 'longitude'
    ]

    # Convert GeoJSON to Feather with latitude and longitude
    geojson_to_feather(
        geojson_file,
        feather_file,
        include_geometry=False,
        include_lat_lon=True,  # Set to True to include latitude and longitude
        selected_columns=selected_columns
    )
