import os
import psycopg2
from flask import Flask, render_template, request, redirect, url_for, jsonify
import folium
import geopandas as gpd
import wikipedia

os.environ["DB_NAME"] = ""
os.environ["DB_USERNAME"] = ""
os.environ["DB_PASSWORD"] = ""


app = Flask(__name__)


# Carlo's Part
# postgresql database connection as function to clean up the code a bit.
def get_db_connection():
    conn = psycopg2.connect(
        host="localhost",
        database=os.environ["DB_NAME"],
        user=os.environ["DB_USERNAME"],
        password=os.environ["DB_PASSWORD"],
    )
    return conn


# creates map of country
def get_map(gdf, water, forest, building):
    centroid = gdf.to_crs(epsg="4326").unary_union.centroid
    m = folium.Map(
        location=[centroid.y, centroid.x], zoom_start=6, tiles="cartodb positron"
    )

    folium.GeoJson(
        gdf.to_crs(epsg="4326"),
        name="Communities",
        style_function=lambda feature: {"fill": False, "color": "black", "weight": 1},
    ).add_to(m)
    folium.GeoJson(
        water,
        name="Water",
        style_function=lambda feature: {
            "color": "#627fde",
            "stroke": False,
            "fillOpacity": "0.8",
        },
    ).add_to(m)
    folium.GeoJson(
        forest,
        name="Forest",
        show=False,
        style_function=lambda feature: {
            "color": "#228a3b",
            "stroke": False,
            "fillOpacity": "0.8",
        },
    ).add_to(m)
    folium.GeoJson(
        building,
        name="Buildings",
        style_function=lambda feature: {
            "color": "#949494",
            "stroke": False,
            "fillOpacity": "0.8",
        },
    ).add_to(m)

    folium.LayerControl().add_to(m)

    m.get_root().width = "800px"
    m.get_root().height = "600px"
    iframe = m.get_root()._repr_html_()
    return iframe


def get_wiki(country):
    return wikipedia.page(country)


# home directory of website. You're able to select a country.
@app.route("/", methods=["GET", "POST"])
def index():
    countries = refresh()
    if request.method == "POST":
        return get_country()
    return render_template("index.html", countries=countries)


# refresh function: selects all countries
def refresh():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM countries ORDER BY NAME;")
    entries = cur.fetchall()
    cur.close()
    conn.close()
    print(len(entries))
    return entries


# Display of country's details
@app.route("/country", methods=["GET", "POST"])
def get_country():
    selected_country = request.form["country"][1:-1].split(",")
    query_st = (
        "SELECT * FROM planet_osm_polygon WHERE admin_level='8' AND ST_CONTAINS("
        + selected_country[1]
        + ",way) ORDER BY name;"
    )
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(
        "SELECT osm_id, name,ST_UNION(array_agg(way)) AS way_union FROM planet_osm_polygon WHERE admin_level='4' AND ST_CONTAINS("
        + selected_country[1]
        + ",way) AND building IS NULL GROUP BY name, osm_id;"
    )
    adminLevel4 = cur.fetchall()
    cur.close()
    gdf = gpd.GeoDataFrame.from_postgis(
        query_st, conn, geom_col="geom"
    )
    water_gdf = gpd.GeoDataFrame.from_postgis(
        "SELECT ST_Intersection(water.geom,"+selected_country[1]+") FROM water;", conn, geom_col="geom"
    )
    forest_gdf = gpd.GeoDataFrame.from_postgis(
        "SELECT ST_Intersection(forest.geom,"+selected_country[1]+") FROM forest;", conn, geom_col="geom"
    )
    building_gdf = gpd.GeoDataFrame.from_postgis(
        "SELECT ST_Intersection(building.geom,"+selected_country[1]+") FROM building;", conn, geom_col="geom"
    )
    subdiv_gdf = gpd.GeoDataFrame.from_postgis(
        "SELECT *, ST_Area(way)/1000000 AS area, water_area/(ST_Area(way)/1000000)*100 as per_water,forest_area/(ST_Area(way)/1000000)*100 as per_forest,building_area/(ST_Area(way)/1000000)*100 as per_building FROM sudvivision WHERE ST_CONTAINS("+selected_country[1]+",way);",
        conn,
        geom_col="way",
        index_col="osm_id",
    ).to_dict("records")
    conn.close()

    return render_template(
        "country.html",
        country=selected_country,
        iframe=get_map(gdf, water_gdf, forest_gdf, building_gdf),
        wiki=get_wiki(selected_country[0]),
        subdivisions=subdiv_gdf,
        adminLevel4=adminLevel4,
    )


@app.route("/subdivision", methods=["GET", "POST"])
def get_subdiv():
    selected_level = request.form["subdivision"][1:-1].split(",")
    print(selected_level[0:2])
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(
        "SELECT name, ST_Union(way) AS aggregated_way FROM planet_osm_polygon WHERE admin_level='8'  AND ST_CONTAINS( ( SELECT ST_Union(array_agg(way))  FROM planet_osm_polygon  WHERE admin_level='4' AND name="
        + selected_level[1]
        + "),  way ) GROUP BY name ORDER BY name;"
    )
    adminLevel8 = cur.fetchall()
    cur.close()
    gdf = gpd.GeoDataFrame.from_postgis(
        "SELECT * FROM planet_osm_polygon WHERE admin_level='8' AND ST_CONTAINS("+ selected_level[1]+ ",way) ORDER BY name;", conn, geom_col="way"
    )
    water_gdf = gpd.GeoDataFrame.from_postgis(
        "SELECT ST_Intersection(water.geom,"+selected_level[1]+") FROM water;", conn, geom_col="geom"
    )
    forest_gdf = gpd.GeoDataFrame.from_postgis(
        "SELECT ST_Intersection(forest.geom,"+selected_level[1]+") FROM forest;", conn, geom_col="geom"
    )
    building_gdf = gpd.GeoDataFrame.from_postgis(
        "SELECT ST_Intersection(building.geom,"+selected_level[1]+") FROM building;", conn, geom_col="geom"
    )
    community_gdf = gpd.GeoDataFrame.from_postgis(
        "SELECT *, ST_Area(way)/1000000 AS area, water_area/(ST_Area(way)/1000000)*100 as per_water,forest_area/(ST_Area(way)/1000000)*100 as per_forest,building_area/(ST_Area(way)/1000000)*100 AS per_building, CASE WHEN EXISTS(SELECT ST_CONTAINS(c.way, r.way) FROM communities c, planet_osm_point r WHERE r.railway='Station') THEN 'YES' ELSE 'NO' END AS railway FROM communities WHERE ST_CONTAINS("+selected_level[1]+",way);",
        conn,
        geom_col="way",
        index_col="osm_id",
    ).to_dict("records")
    conn.close()
    return render_template(
        "subdiv.html", selected_level=selected_level, adminLevel8=adminLevel8,iframe=get_map(gdf, water_gdf, forest_gdf, building_gdf), wiki=get_wiki(selected_level[0]), communities=community_gdf
    )

@app.route("/community", methods=["GET","POST"])
def get_community():
    selected_community = request.form["community"][1:-1].split(",")
    conn = get_db_connection()
    gdf = gpd.GeoDataFrame.from_postgis(
        "SELECT * FROM planet_osm_polygon WHERE admin_level='8' AND ST_CONTAINS("+ selected_community[1]+ ",way) ORDER BY name;", conn, geom_col="way"
    )
    water_gdf = gpd.GeoDataFrame.from_postgis(
        "SELECT ST_Intersection(water.geom,"+selected_community[1]+") FROM water;", conn, geom_col="geom"
    )
    forest_gdf = gpd.GeoDataFrame.from_postgis(
        "SELECT ST_Intersection(forest.geom,"+selected_community[1]+") FROM forest;", conn, geom_col="geom"
    )
    building_gdf = gpd.GeoDataFrame.from_postgis(
        "SELECT ST_Intersection(building.geom,"+selected_community[1]+") FROM building;", conn, geom_col="geom"
    )
    conn.close()
    return render_template(
        "community.html", selected_community=selected_community, iframe=get_map(gdf,water_gdf,forest_gdf,building_gdf), wiki=get_wiki(selected_community[0])
    )

# Oliver's Part
# refresh function: selects unique amenities
def refresh_amenity():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT DISTINCT amenity FROM planet_osm_polygon;")
    amenity_values = cur.fetchall()
    cur.close()
    conn.close()
    return amenity_values


# Query page to select amenities
@app.route("/querrys", methods=["GET"])
def querrys():
    amenity_values = refresh_amenity()
    return render_template("querrys.html", amenity_values=amenity_values)


@app.route("/result", methods=["POST"])
def process_query():
    try:
        selected_amenities = request.json.get("selectedAmenities")

        if not selected_amenities:
            return jsonify([])

        # Build the SQL query with OR conditions for selected amenities
        query = "SELECT osm_id, building, 'addr:housename', name, ST_Area(way) AS way_area, way FROM planet_osm_polygon WHERE amenity IN ("
        query += ", ".join(["%s" for _ in selected_amenities])
        query += ");"

        conn = get_db_connection()
        cur = conn.cursor()

        cur.execute(query, selected_amenities)
        results = cur.fetchall()

        return jsonify(results)

    finally:
        if conn is not None:
            conn.close()


@app.route("/result", methods=["GET"])
def show_results():
    return redirect(url_for("querrys"))


@app.route("/predefined_query", methods=["POST"])
def predefined_query():
    selected_query = request.json.get("selectedQuery")

    if selected_query == "historicalChimneys":
        query = "SELECT osm_id, building, historic, man_made, ST_Area(way) AS way_area, way FROM planet_osm_polygon WHERE historic = 'industrial' AND man_made = 'chimney';"
    elif selected_query == "commercialBuildings":
        query = "SELECT osm_id, building, historic, man_made, ST_Area(way) AS way_area, way FROM planet_osm_polygon WHERE man_made = 'works' AND building IS NOT NULL AND historic IS NULL;"
    elif selected_query == "schools":
        query = "SELECT osm_id, building, historic, man_made, ST_Area(way) AS way_area, way FROM planet_osm_polygon WHERE amenity = 'school';"

    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(query)
    results = cur.fetchall()
    conn.close()

    return jsonify(results)


if __name__ == "__main__":
    app.run()
