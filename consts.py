import numpy as np


###########################################################
processed_files_dir = "./processed_files"

boundaries_list = [
    {"id": "None", "name": "No Boundaries"},
    {"id": "co", "name": "County"},
    {"id": "ct", "name": "Census Tract"},
    {"id": "bg", "name": "Block Group"}
]

CLIMATE_SPATIAL_LEVELS = [
    { "name": "Points", "id": "pt" },
    { "name": "County", "id": "co" },
    { "name": "Census Tract", "id": "ct"},
    { "name": "Block Group", "id": "bg"},
]

RISK_FILE = f"./{processed_files_dir}/risk/Illinois_prcp_risks_round.feather"

SOCIO_SPATIAL_LEVELS = [
    { "name": "Census Tract", "id": "ct"},
    # { "name": "Block Group", "id": "bg"},
]

STATIONS_FILE = f"{processed_files_dir}/ev-stations/alt_fuel_stations.geojson"

###########################################################

# CLIMATE_TIME_STAMPS = [str(y) for y in range(1980, 2023+1)]
CLIMATE_TIME_STAMPS = [str(y) for y in range(1980, 1982+1)]

raw_files_dir = "./raw_files"
click_boundary_file = f"{raw_files_dir}/IL_BNDY_State_Py.json"

processed_climate_files_dir = f"{processed_files_dir}/climate"
processed_ev_files_dir = f"{processed_files_dir}/ev-stations"
processed_bound_files_dir = f"{processed_files_dir}/boundaries"
processed_risk_dir = f"{processed_files_dir}/risk"
processed_socio_dir = f"{processed_files_dir}/socio"

files_path = "./files"


socio_vars = [
    {"B01003_001E": "Population"},
    {"P9_002N": "Hispanic or Latino"},
    {"P9_003N": "Not Hispanic or Latino"},
    {"P9_005N": "White"},
    {"P9_006N": "Black or African American"},
    {"P9_007N": "American Indian and Alaska Native"},
    {"P9_008N": "Asian"},
    {"P9_009N": "Native Hawaiian and Other Pacific Islander "},
    {"P9_010N": "Some Other Race"},
]

files = [
            {"var_name": "tmin", "path": f"{files_path}/Yearly_tmin_round.json"},
            {"var_name": "tmax", "path": f"{files_path}/Yearly_tmax_round.json"},
            {"var_name": "prcp", "path": f"{files_path}/Yearly_prcp_round.json"},
        ]

binary_data_dir = f"{files_path}/binary_data"

variables = ["tmin", "tmax", "prcp"]

# Build variables domains and colors
min_temp_start, min_temp_end, min_temp_n = -35, 0, 14
min_temp_domain = [round(min_temp_start + (min_temp_end - min_temp_start) * i / (min_temp_n - 1), 1) for i in range(min_temp_n)]

max_temp_start, max_temp_end, max_temp_n = 10, 50, 14
max_temp_domain = [round(max_temp_start + (max_temp_end - max_temp_start) * i / (max_temp_n - 1), 1) for i in range(max_temp_n)]

prcp_domain_inches = [0, 0.01, 0.1, 0.25, 0.5, 1, 1.5, 2, 3, 4, 6, 8, 10]
prcp_domain_mm = [round(value * 25.4, 2) for value in prcp_domain_inches]

min_temp_colors = np.array([
    [145, 0, 63],
    [206, 18, 86],
    [231, 41, 138],
    [223, 101, 176],
    [255, 115, 223],
    [255, 190, 232],
    [255, 255, 255],
    [218, 218, 235],
    [188, 189, 220],
    [158, 154, 200],
    [117, 107, 177],
    [84, 39, 143],
    [13, 0, 125],
    [13, 61, 156],
    [0, 102, 194],
    [41, 158, 255],
    [74, 199, 255],
    [115, 215, 255],
    [173, 255, 255]
])

max_temp_colors = np.array([
    [48, 207, 194],
    [0, 153, 150],
    [18, 87, 87],
    [6, 109, 44],
    [49, 163, 84],
    [116, 196, 118],
    [161, 217, 155],
    [211, 255, 190],
    [255, 255, 179],
    [255, 237, 160],
    [254, 209, 118],
    [254, 174, 42],
    [253, 141, 60],
    [252, 78, 42],
    [227, 26, 28],
    [177, 0, 38],
    [128, 0, 38],
    [89, 0, 66],
    [40, 0, 40]
])

prcp_colors = np.array([
    [255,255,255], # ≤ 0.00
    [199,233,192], # 0.01 - 0.25
    [161,217,155], # 0.26 - 2.54
    [116,196,118], # 2.55 - 6.35
    [49,163,83],   # 6.36 - 12.70
    [0,109,44],    # 12.71 - 25.40
    [255,250,138], # 25.41 - 38.10
    [255,204,79],  # 38.11 - 50.80
    [254,141,60],  # 50.81 - 76.20
    [252,78,42],   # 76.21 - 101.60
    [214,26,28],   # 101.61 - 152.40
    [173,0,38],    # 152.41 - 203.20
    [112,0,38],    # 203.21 - 254.00
    # [59,0,48],
    # [76,0,115],
    # [255,219,255]
])

variables_domains = {
    "tmin": min_temp_domain, 
    "tmax": max_temp_domain, 
    "prcp": prcp_domain_mm
}

variables_colors = {
    "tmin": min_temp_colors, 
    "tmax": max_temp_colors, 
    "prcp": prcp_colors
}

thresholds = {
    "tmin": [
            { "value": -30   , "color": "#FFFFFF"},
            { "value": -28, "color": "#E0F3DB"},
            { "value":  -26, "color": "#C2E699"},
            { "value": -24, "color": "#78C679"},
            { "value": -22, "color": "#31A354"},
            { "value": -20, "color": "#006837"},
            { "value": -18, "color": "#FFEDA0"},
            { "value": -16, "color": "#FED976"},
            { "value": -14, "color": "#FEB24C"},
            { "value": -12, "color": "#FD8D3C"},
            { "value": -10, "color": "#FC4E2A"},
            { "value": -8, "color": "#E31A1C"},
            { "value": -6, "color": "#BD0026"},
            { "value": -4, "color": "#800026"},
            { "value": -2, "color": "#54278F"},
            { "value": 0, "color": "#756BB1"},
            { "value": 2, "color": "#9E9AC8"},
            { "value": 4, "color": "#CBC9E2"},
            { "value": 6, "color": "#DADAEB"},
            { "value": 8, "color": "#F2F0F7"},
    ],
    "tmax": [
        { "value": 0 , "color": "#FFFFFF"},
        { "value": 14, "color": "#E0F3DB"},
        { "value": 16, "color": "#C2E699"},
        { "value": 18, "color": "#78C679"},
        { "value": 20, "color": "#31A354"},
        { "value": 22, "color": "#006837"},
        { "value": 24, "color": "#FFEDA0"},
        { "value": 26, "color": "#FED976"},
        { "value": 28, "color": "#FEB24C"},
        { "value": 30, "color": "#FD8D3C"},
        { "value": 32, "color": "#FC4E2A"},
        { "value": 34, "color": "#E31A1C"},
        { "value": 36, "color": "#BD0026"},
        { "value": 38, "color": "#800026"},
        { "value": 40, "color": "#54278F"},
        { "value": 42, "color": "#756BB1"},
        { "value": 44, "color": "#9E9AC8"},
        { "value": 46, "color": "#CBC9E2"},
        { "value": 48, "color": "#DADAEB"},
        { "value": 50, "color": "#F2F0F7"},
        ],
    "prcp": [
                    {"value": 0.0, "color": "#FFFFFF"},
            {"value": 12.7, "color": "#E0F3DB"},
            {"value": 25.4, "color": "#C2E699"},
            {"value": 38.1, "color": "#78C679"},
            {"value": 50.8, "color": "#31A354"},
            {"value": 63.5, "color": "#006837"},
            {"value": 76.2, "color": "#FFEDA0"},
            {"value": 88.9, "color": "#FED976"},
            {"value": 101.6, "color": "#FEB24C"},
            {"value": 114.3, "color": "#FD8D3C"},
            {"value": 127.0, "color": "#FC4E2A"},
            {"value": 139.7, "color": "#E31A1C"},
            {"value": 152.4, "color": "#BD0026"},
            {"value": 165.1, "color": "#800026"},
            {"value": 177.8, "color": "#54278F"},
            {"value": 190.5, "color": "#756BB1"},
            {"value": 203.2, "color": "#9E9AC8"},
            {"value": 215.9, "color": "#CBC9E2"},
            {"value": 228.6, "color": "#DADAEB"},
            {"value": 241.3, "color": "#F2F0F7"},
    ]
}

CLIMATE_VARIABLES = [
    {
        "name": "Min Temperature",
        "id": "tmin",
        "domain": min_temp_domain,
        "colors": min_temp_colors
    },
    {
        "name": "Max Temperature",
        "id": "tmax",
        "domain": max_temp_domain,
        "colors": max_temp_colors
    },
    {
        "name": "Annual Daily Max Precipitation",
        "id": "prcp",
        "domain": prcp_domain_mm,
        "colors": prcp_colors
    }
]

CLIMATE_YEARS = [str(y) for y in range(1980, 2023+1)]
