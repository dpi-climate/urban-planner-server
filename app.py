from flask_cors import CORS
from flask import Flask, request, send_from_directory, jsonify, send_file, Response

from structure import Structure
from flask_compress import Compress

app = Flask(__name__)
CORS(app)
Compress(app)

app.debug  = True

structure = Structure()

@app.route("/boundary", methods=("GET", "POST"))
def handle_boundary():
    if(request.method == "GET"):
        b = structure.get_boundaries_list()
        return jsonify(b)
    else:
        b_id = request.json["b_id"]
        b = structure.get_boundary(b_id)

        return Response(b, mimetype="application/octet-stream")

@app.route("/click_boundary", methods=("GET",))
def handle_click_boundary():
    gdf = structure.get_click_boundary()
    return Response(gdf.to_json(), mimetype='application/json')

@app.route("/climate_layer", methods=("GET",))
def handle_climate_layer():
    
    # s_agg = "" if "s_agg" not in request.args else request.args["s_agg"]
    s_agg = request.args["s_agg"]
    var_name = request.args["var_name"]
    year = request.args["year"]
    
    print(var_name, year, s_agg)

    if s_agg == "pt":
        buffer = structure.get_climate_point_layer(var_name, year, s_agg)
        final = Response(buffer, mimetype="application/octet-stream")
    else:
        buffer = structure.load_csv_file(var_name, year, s_agg)# structure.get_climate_polygon_layer(var_name, year, s_agg)
        final = Response(buffer, mimetype="application/octet-stream")
        # # final = Response(
        # #     buffer,
        # #     mimetype="application/octet-stream",
        # #     headers={"Content-Disposition": "attachment; filename=data.parquet"}
        # #     # headers={"Content-Disposition": "attachment; filename=data.pkl"}
        # # )
        # # final = Response(buffer, content_type='application/json')#buffer
        # final = send_file(
        #     buffer,
        #     as_attachment=False,
        #     # as_attachment=True,
        #     download_name="data.feather",
        #     mimetype="application/octet-stream"
        #     # download_name="data.parquet",
        #     # mimetype="application/parquet"
        # )
        # # final = Response(
        # #     buffer,
        # #     mimetype='application/geo+json',
        # #     headers={'Content-Disposition': 'attachment;filename=data.geojson'}
        # # )
    
    if buffer is None:
        return jsonify({"error": "No data found"}), 404

    # Return the raw bytes with an octet-stream mimetype
    # return Response(buffer, mimetype="application/octet-stream")
    return final


@app.route("/socio_layer", methods=("GET",))
def handle_socio_layer():

    s_agg = request.args["s_agg"]

    if s_agg == "pt":
        s_agg = "co"
    
    elif s_agg == "bg":
        s_agg = "ct"
        
    var_name = request.args["var_name"]

    print(var_name, s_agg)

    binary = structure.get_socio_layer(var_name, s_agg)

    if binary is None:
        return jsonify({"error": "No data found"}), 404

    # Return the raw bytes with an octet-stream mimetype
    return Response(binary, mimetype="application/octet-stream")

@app.route("/socio_vars", methods=("GET",))
def handle_socio_vars():
    socio_vars = structure.get_socio_variables()
    return jsonify(socio_vars)

@app.route("/climate_vars", methods=("GET",))
def handle_climate_vars():
    climate_vars = structure.get_climate_variables()
    return jsonify(climate_vars)

@app.route("/risk_data", methods=("GET",))
def handle_point_feature():

    coords = (float(request.args["lat"]), float(request.args["lon"]))

    risk_data = structure.get_risk_data(coords)
    
    return jsonify(risk_data)

@app.route("/stations", methods=("GET",))
def handle_stations():
    stations = structure.get_stations()    
    return jsonify(stations)

@app.route("/socio", methods=("POST",))
def handle_socio():
    id = request.json["id"]
    level = request.json["level"]
    obj = structure.get_socio_data(id, level)

    return jsonify(obj)

@app.route("/climate_sp_lvls", methods=("GET",))
def handle_climate_sp_lvls():
    climate_sp_lvls = structure.get_climate_spatial_levels()
    return jsonify(climate_sp_lvls)

@app.route("/climate_time_stamp_list", methods=("GET",))
def handle_climate_time_stamp_list():
    climate_tstamp_list = structure.get_climate_time_stamp_list()
    return climate_tstamp_list


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
    structure.load_boundary_layers()
    structure.load_climate_layers()
    structure.load_risk_df()
    structure.load_socio_layers()
    # structure.load_socio_df()
    structure.load_stations_layer()

    # structure.load_csv_file()


    
    print("Go!")
    app.run(debug=False)
    print()

if __name__ == '__main__':
    main()