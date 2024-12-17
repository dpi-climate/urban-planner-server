from flask_cors import CORS
from flask import Flask, request, send_from_directory, jsonify
import argparse
import json

from structure import Structure

app = Flask(__name__)
CORS(app)

app.debug  = True


structure = Structure()
# structure.startServer()


@app.route("/geojson_data", methods=("GET",))
def handle_geojson_data():
    var_name = request.args["var_name"]
    print(var_name, 1)
    gjson = structure.get_geojson_data(var_name)
    print(var_name, 2)

    return jsonify(gjson)

@app.route("/point_feature", methods=("GET",))
def handle_point_feature():
    pt_feature = structure.get_point_feature("tmin")
    return jsonify(pt_feature)

def main():
    # global workdir

    # parser = argparse.ArgumentParser(description='e-JUST')

    # parser.add_argument('-d', '--data', nargs='?', type=str, required=False, default=None, help='Path to data folder.')

    # args = parser.parse_args()
    # workdir = args.data

    # if workdir == None:
    #     print("Error: --data not specified.")
    #     exit(1)

    structure.load_geojson()
    app.run()

if __name__ == '__main__':
    main()