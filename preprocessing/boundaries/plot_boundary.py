import pickle
import geopandas as gpd
import matplotlib.pyplot as plt
from shapely.geometry import shape

def plot_pickle_file(file_path, prop_key):
    # Load the Pickle file
    with open(file_path, 'rb') as f:
        data = pickle.load(f)
    # print(data)

    features = data["features"]
    geometries = [shape(feature["geometry"]) for feature in features]
    properties = [feature["unitid"] for feature in features]

    gdf = gpd.GeoDataFrame(properties, geometry=geometries)

    # Plot the GeoDataFrame
    gdf.plot(figsize=(10, 10), edgecolor='black', cmap='viridis')
    plt.title("GEOID Map")
    plt.xlabel("Longitude")
    plt.ylabel("Latitude")
    plt.show()

if __name__ == "__main__":
    # pickle_path = "./processed_files/cb_2018_17_tract_500k.pickle"
    pickle_path = "./processed_files/ct.pickle"
    pickle_prop_key = "unit"
    plot_pickle_file(pickle_path, pickle_prop_key)
