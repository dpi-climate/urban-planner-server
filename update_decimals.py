import json
import math


# main_path = "C:/Users/carol/Documents/GitHub/urban-planner/public"

# input_geojson_path = f"{main_path}/Yearly_tmin.json"
# output_geojson_path = f"{main_path}/Yearly_tmin_round.json"

main_path = "C:/Users/carol/Box/carolina/work/Projects/CLEETS/Visualization/urban-planner-files"

input_geojson_path = f"{main_path}/Illinois_prcp_risks.json"
output_geojson_path = f"{main_path}/Illinois_prcp_risks_round.json"


with open(input_geojson_path, "r", encoding="utf-8") as f:
    data = json.load(f)

if "features" in data:
    for feature in data["features"]:
        props = feature.get("properties", {})
        for k, v in props.items():
            if v is not None and isinstance(v, (int, float)):
                props[k] = round(v, 2)

with open(output_geojson_path, "w", encoding="utf-8") as f:
    # Using separators to minimize output size (no extra spaces)
    json.dump(data, f, separators=(',',':'))
