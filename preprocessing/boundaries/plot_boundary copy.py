import pickle
import geopandas as gpd
import matplotlib.pyplot as plt
from shapely.geometry import shape

def plot_pickle_file(pickle_file_path):
    """
    Load and plot GeoJSON data stored in a pickle file.
    
    Args:
        pickle_file_path (str): Path to the pickle file.
    """
    try:
        # Load the pickle file
        with open(pickle_file_path, 'rb') as file:
            geojson_data = pickle.load(file)
        
        # Convert GeoJSON data to GeoDataFrame
        features = geojson_data["features"]
        geometries = [shape(feature["geometry"]) for feature in features]
        properties = [feature["properties"] for feature in features]
        
        gdf = gpd.GeoDataFrame(properties, geometry=geometries)
        
        # Plot the GeoDataFrame
        gdf.plot(figsize=(10, 10), edgecolor='black', cmap='viridis')
        plt.title("GEOID Map")
        plt.xlabel("Longitude")
        plt.ylabel("Latitude")
        plt.show()
        
    except Exception as e:
        print(f"An error occurred while plotting: {e}")

if __name__ == "__main__":
    # pickle_path = "./processed_files/cb_2018_17_tract_500k.pickle"
    pickle_path = "./processed_files/ct.pickle"
    plot_pickle_file(pickle_path)
