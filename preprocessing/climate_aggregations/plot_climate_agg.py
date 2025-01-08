import pickle
import geopandas as gpd
import matplotlib.pyplot as plt
from shapely.geometry import shape

import geopandas as gpd

def plot_geojson(gdf, agg_key):

    # Plot the data
    fig, ax = plt.subplots(figsize=(10, 10))
    gdf.plot(ax=ax, column=agg_key, cmap='coolwarm', legend=True)

    # Add title and axis labels
    ax.set_title("Title", fontsize=15)
    ax.set_xlabel("Longitude")
    ax.set_ylabel("Latitude")

    plt.show()


def plot_pickle(file_path, prop_key, agg_key):

    # Load the Pickle file
    with open(file_path, 'rb') as f:
        data = pickle.load(f)

    # Convert the data back to a GeoDataFrame
    records = data[prop_key]
    geometries = [shape(record['geometry']) for record in records]
    values = [record[agg_key] for record in records]

    gdf = gpd.GeoDataFrame({agg_key: values}, geometry=geometries)

    plot_geojson(gdf, agg_key)

if __name__ == "__main__":
    pickle_file_path = "./processed_files/ct_prcp_1980.pickle"
    pickle_prop_key = "features"
    pickle_agg_key = "value"

    plot_pickle(pickle_file_path, pickle_prop_key, pickle_agg_key)

    ##############################################################

    # geojson_file_path = "./processed_files/ct_tmin_1980.geojson"
    # geojson_agg_key = "value"

    # gdf = gpd.read_file(geojson_file_path, geojson_agg_key)
    # plot_geojson(gdf, geojson_agg_key)

