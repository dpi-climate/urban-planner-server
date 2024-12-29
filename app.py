from flask_cors import CORS
from flask import Flask, request, send_from_directory, jsonify, Response
import argparse
import json

from structure import Structure
from flask_compress import Compress

app = Flask(__name__)
CORS(app)
Compress(app)

app.debug  = True


structure = Structure()
# structure.startServer()


@app.route("/pt_layer_data", methods=("GET",))
def handle_pt_layer_data():
    s_agg = "" if "s_agg" not in request.args else request.args["s_agg"]
    var_name = request.args["var_name"]
    year = request.args["year"]
    print(var_name, year, s_agg)
    binary = structure.get_points(var_name, year, s_agg)

    # return json.dumps(gjson)
    # return jsonify(binary)
    
    if binary is None:
        return jsonify({"error": "No data found"}), 404

    # Return the raw bytes with an octet-stream mimetype
    return Response(binary, mimetype="application/octet-stream")

@app.route("/pol_layer_data", methods=("GET",))
def handle_pol_layer_data():
    s_agg = "" if "s_agg" not in request.args else request.args["s_agg"]
    var_name = request.args["var_name"]
    year = request.args["year"]
    print(var_name, year, s_agg)
    binary = structure.get_points(var_name, year, s_agg)

    if binary is None:
        return jsonify({"error": "No data found"}), 404

    return Response(binary, mimetype="application/octet-stream")

@app.route("/risk_data", methods=("GET",))
def handle_point_feature():

    if "pt_idx" in request.args:
        pt_idx = int(request.args["pt_idx"])
    
    else:
        pt_idx = (float(request.args["lat"]), float(request.args["lon"]))

    risk_data = structure.get_risk_data(pt_idx)
    
    return jsonify(risk_data)


# @app.route("/point_feature", methods=("GET",))
# def handle_point_feature():
#     pt_feature = structure.get_point_feature("tmin")
#     return jsonify(pt_feature)

def main():
    # global workdir

    # parser = argparse.ArgumentParser(description='e-JUST')

    # parser.add_argument('-d', '--data', nargs='?', type=str, required=False, default=None, help='Path to data folder.')

    # args = parser.parse_args()
    # workdir = args.data

    # if workdir == None:
    #     print("Error: --data not specified.")
    #     exit(1)

    # structure.process_files()
    structure.load_binary()
    structure.load_risk()
    print("Go!")
    app.run()
    print()

if __name__ == '__main__':
    main()