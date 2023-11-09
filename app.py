import os
import psycopg2
from flask import Flask, render_template, request
import folium
import geopandas as gpd
import wikipedia

app = Flask(__name__)


#postgresql database connection as function to clean up the code a bit.
def get_db_connection():
    conn = psycopg2.connect(host='localhost',
                            database=os.environ['DB_NAME'],
                            user=os.environ['DB_USERNAME'],
                            password=os.environ['DB_PASSWORD'])
    return conn

#creates map of country
def get_map(gdf,water,forest,building):
    centroid = gdf.to_crs(epsg='4326').unary_union.centroid
    m = folium.Map(location=[centroid.y, centroid.x], zoom_start=6)

    folium.GeoJson(gdf.to_crs(epsg='4326'),overlay=False,control=False,style_function=lambda feature:{
        "fill": False,
        "color": "black"
    },).add_to(m)
    folium.GeoJson(water,name="Water",style_function=lambda feature:{
        "color": "#627fde",
        "stroke": False,
        "fillOpacity": "0.8"
    },).add_to(m)
    folium.GeoJson(forest,name="Forest",style_function=lambda feature:{
        "color": "#228a3b",
        "stroke": False,
        "fillOpacity": "0.8"
    }).add_to(m)
    folium.GeoJson(building,name="Buildings",style_function=lambda feature:{
        "color": "#949494",
        "stroke": False,
        "fillOpacity": "0.8"
    }).add_to(m)

    folium.LayerControl().add_to(m)

    m.get_root().width = "800px"
    m.get_root().height = "600px"
    iframe = m.get_root()._repr_html_()
    return iframe

def get_wiki(country):
    return wikipedia.page(country)

#home directory of website. You're able to select a country.
@app.route('/', methods=['GET','POST'])
def index():
    countries=refresh()
    if request.method == 'POST':
        return get_amenity()
    return render_template('index.html', countries=countries)

#refresh function: selects all countries
def refresh():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM planet_osm_polygon WHERE admin_level='2' ORDER BY NAME;")
    entries= cur.fetchall()
    cur.close()
    conn.close()
    print(len(entries))
    return entries

#Display of country's details
@app.route('/amenity', methods=['GET','POST'])
def get_amenity():
    selected_amenity = request.form['country']
    selected_amenity =selected_amenity[1:-1].split(',')
    query_st="SELECT * FROM planet_osm_polygon WHERE admin_level='8' AND ST_CONTAINS((SELECT way FROM planet_osm_polygon WHERE osm_id=\'"+selected_amenity[0]+'\'),way) ORDER BY name;'
    conn = get_db_connection()
    gdf=gpd.GeoDataFrame.from_postgis(query_st,conn,geom_col='way',index_col='osm_id')
    water_gdf=gpd.GeoDataFrame.from_postgis("SELECT * FROM water;",conn,geom_col='geom',index_col='osm_id')
    forest_gdf=gpd.GeoDataFrame.from_postgis("SELECT * FROM forest;",conn,geom_col='geom',index_col='osm_id')
    building_gdf=gpd.GeoDataFrame.from_postgis("SELECT * FROM building;",conn,geom_col='geom',index_col='osm_id')
    conn.close()

    return render_template('country.html', country=selected_amenity, iframe=get_map(gdf,water_gdf,forest_gdf,building_gdf), wiki=get_wiki(selected_amenity[38]))

if __name__ == '__main__':
    app.run()