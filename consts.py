import numpy as np

files_path = "./files"

files = [
            {"var_name": "tmin", "path": f"{files_path}/Yearly_tmin_round.json"},
            {"var_name": "tmax", "path": f"{files_path}/Yearly_tmax_round.json"},
            {"var_name": "prcp", "path": f"{files_path}/Yearly_prcp_round.json"},
        ]

binary_data_dir = f"{files_path}/binary_data"

variables = ["tmin", "tmax", "prcp"]

years = [str(y) for y in range(1980, 2023+1)]



# Build variables domains and colors
start, end, n = -50, 50, 38
temp_range = [round(start + (end - start) * i / (n - 1), 1) for i in range(n)]

prcp_range_inches = [0, 0.01, 0.1, 0.25, 0.5, 1, 1.5, 2, 3, 4, 6, 8, 10, 15, 20, 30]
prcp_range_mm = [round(value * 25.4, 2) for value in prcp_range_inches]

temp_colors = np.array([
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
    [173, 255, 255],
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

prcp_colors = np.array([[255,255,255],
              [199,233,192],
              [161,217,155],
              [116,196,118],
              [49,163,83],
              [0,109,44],
              [255,250,138],
              [255,204,79],
              [254,141,60],
              [252,78,42],
              [214,26,28],
              [173,0,38],
              [112,0,38],
              [59,0,48],
              [76,0,115],
              [255,219,255]])

variables_domains = {
    "tmin": temp_range, 
    "tmax": temp_range, 
    "prcp": prcp_range_mm
}

variables_colors = {
    "tmin": temp_colors, 
    "tmax": temp_colors, 
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