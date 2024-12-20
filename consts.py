files_path = "./files"

files = [
            {"var_name": "tmin", "path": f"{files_path}/Yearly_tmin_round.json"},
            {"var_name": "tmax", "path": f"{files_path}/Yearly_tmax_round.json"},
            {"var_name": "prcp", "path": f"{files_path}/Yearly_prcp_round.json"},
        ]

binary_data_dir = f"{files_path}/binary_data"

variables = ["tmin", "tmax", "prcp"]

years = [str(y) for y in range(1980, 2023+1)]

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