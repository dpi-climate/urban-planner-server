import os
import argparse
from fastapi.staticfiles import StaticFiles

from fastapi import FastAPI, Body,HTTPException
from fastapi.responses import FileResponse, Response, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware

import psycopg2
import asyncpg


from structure import Structure

app = FastAPI(
    debug=os.getenv('FLASK_DEBUG', 'False').lower() in ['true', '1'],
    title="My FastAPI App"
)

CORS_ORIGINS = os.getenv('CORS_ORIGINS', '*').split(',')
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(GZipMiddleware, minimum_size=1000)

structure = Structure()

structure.load_boundary_layers()
structure.load_climate_layers()
structure.load_risk_df()
structure.load_socio_layers()
structure.load_stations_layer()
print("Initialization complete.")


async def get_geojson():
    conn = await asyncpg.connect(
        database="urban_planner_db",
        user="postgres",
        password="123",
        host="localhost",
        port="5432"
    )

    query = """
        SELECT json_build_object(
            'type', 'FeatureCollection',
            'features', json_agg(
                json_build_object(
                    'type', 'Feature',
                    'geometry', ST_AsGeoJSON(geom, 6)::json,  -- Geometry with limited precision
                    'properties', json_build_object(
                        'UNITID', unitid,
                        'value', 1980
                    )
                )
            )
        )
        FROM bg_prcp t;
    """
    geojson = await conn.fetchval(query)
    await conn.close()

    return geojson

@app.get("/test_db")
async def get_shapefile():
    geojson = await get_geojson()
    print("sending!!!")
    return JSONResponse(content=geojson)

# @app.get("/test_db")
# def get_geojson():
#     # Connect to PostgreSQL
#     conn = psycopg2.connect(
#         dbname="urban_planner_db",
#         user="postgres",
#         password="123",
#         host="localhost",
#         port="5432"
#     )

#     cursor = conn.cursor()

#     # Use ST_AsGeoJSON to convert geometries into GeoJSON format
#     cursor.execute("""
#         SELECT json_build_object(
#             'type', 'FeatureCollection',
#             'features', json_agg(ST_AsGeoJSON(t.*)::json)
#         )
#         FROM bg_prcp_combined t;
#     """)

#     geojson = cursor.fetchone()[0]

#     # Close connection
#     cursor.close()
#     conn.close()

#     # return geojson
#     return JSONResponse(content=geojson)


@app.get("/boundary")
def handle_boundary_get():
    b = structure.get_boundaries_list()
    return b

@app.post("/boundary")
def handle_boundary_post(data: dict = Body(...)):
    b_id = data["b_id"]
    b = structure.get_boundary(b_id)
    return Response(content=b, media_type="application/octet-stream")

@app.get("/click_boundary")
def handle_click_boundary():
    gdf = structure.get_click_boundary()
    return Response(content=gdf.to_json(), media_type="application/json")


@app.get("/climate_layer")
def handle_climate_layer(
    s_agg: str,
    var_name: str,
    year: str
):
    """
    Example usage: 
    GET /climate_layer?s_agg=pt&var_name=temperature&year=2020
    """
    print(var_name, year, s_agg)

    # do your logic:
    if s_agg == "pt":
        buffer = structure.get_climate_point_layer(var_name, year, s_agg)
    else:
        buffer = structure.load_csv_file(var_name, year, s_agg)

    if buffer is None:
        raise HTTPException(status_code=404, detail="No data found")

    return Response(content=buffer, media_type="application/octet-stream")


@app.get("/socio_layer")
def handle_socio_layer(s_agg: str, var_name: str):
    if s_agg == "pt":
        s_agg = "co"
    elif s_agg == "bg":
        s_agg = "ct"

    binary_data = structure.get_socio_layer(var_name, s_agg)
    if binary_data is None:
        raise HTTPException(status_code=404, detail="No data found")

    return Response(content=binary_data, media_type="application/octet-stream")


@app.get("/socio_vars")
def handle_socio_vars():
    return structure.get_socio_variables()


@app.get("/climate_vars")
def handle_climate_vars():
    return structure.get_climate_variables()


@app.get("/risk_data")
def handle_point_feature(lat: float, lon: float):
    coords = (lat, lon)
    risk_data = structure.get_risk_data(coords)
    return risk_data


@app.get("/stations")
def handle_stations():
    stations = structure.get_stations()
    return stations


@app.post("/socio")
def handle_socio(data: dict = Body(...)):
    id_ = data["id"]
    level = data["level"]
    obj = structure.get_socio_data(id_, level)
    return obj


@app.get("/climate_sp_lvls")
def handle_climate_sp_lvls():
    return structure.get_climate_spatial_levels()


@app.get("/climate_time_stamp_list")
def handle_climate_time_stamp_list():
    return structure.get_climate_time_stamp_list()


app.mount(
    "/",
    StaticFiles(directory="../urban-planner/dist", html=True),
    name="static"
)

@app.get("/")
def read_index():
    return FileResponse("../urban-planner/dist/index.html")


def start():

    global workdir

    parser = argparse.ArgumentParser(description='e-JUST')

    # parser.add_argument('-d', '--data', nargs='?', type=str, required=False, default=None, help='Path to data folder.')
    parser.add_argument('--cert', type=str, required=False, help='Path to the SSL certificate.')
    parser.add_argument('--key', type=str, required=False, help='Path to the SSL key.')

    args = parser.parse_args()

    import uvicorn

    uvicorn.run(
            "main:app", 
            host="0.0.0.0", 
            port=5000,
            ssl_certfile=args.cert if args.cert else None,
            ssl_keyfile=args.key if args.key else None,
            reload=True  # reload for dev
        )    
if __name__ == '__main__':
    start()