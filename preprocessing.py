import numpy as np
import json
import geopandas as gpd
from shapely.geometry import Point
from consts import files_path, binary_data_dir, temp_colors, temp_range, prcp_colors, prcp_range_mm
import pickle
import os
from collections import defaultdict

from write_bin_polygon import build_threshold_rgba

def write_pickle_files():
    temp_threshold = build_threshold_rgba(temp_range, temp_colors)
    prcp_threshold = build_threshold_rgba(prcp_range_mm, prcp_colors)

    original_files = [
        {"var_name": "tmin", "path": f"{files_path}/Yearly_tmin_round.json", "threshold": temp_threshold},
        {"var_name": "tmax", "path": f"{files_path}/Yearly_tmax_round.json", "threshold": temp_threshold},
        {"var_name": "prcp", "path": f"{files_path}/Illinois_prcp_risks_round.json", "threshold": prcp_threshold},
    ]

    tracts_geojson_path = f"{files_path}/cb_2018_17_tract_500k.geojson"  # Update the path accordingly


if __name__ == "__main__":

    ######################################################
    # Write Pickle Files 
    write_pickle_files()

   



