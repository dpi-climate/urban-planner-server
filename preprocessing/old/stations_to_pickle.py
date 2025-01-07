import pandas as pd
import geopandas as gpd
from shapely.geometry import Point
import pickle

csv_file = './files/alt_fuel_stations_Aug_26_2024.csv'
pickle_file = './files/alt_fuel_stations_geodf.pkl'

# Read CSV into a DataFrame
df = pd.read_csv(csv_file)

# Create geometry from longitude and latitude
geometry = gpd.points_from_xy(df['Longitude'], df['Latitude'])

# Create a GeoDataFrame
gdf = gpd.GeoDataFrame(df, geometry=geometry)

# Now pickle this GeoDataFrame
with open(pickle_file, 'wb') as p:
    pickle.dump(gdf, p)

print(f"Pickle file with geometry created: {pickle_file}")
