import os
import psycopg2
from flask import Flask, render_template, request
import folium
import geopandas as gpd

app = Flask(__name__)


#postgresql database connection as function to clean up the code a bit.
def get_db_connection():
    conn = psycopg2.connect(host='localhost',
                            database=os.environ['DB_NAME'],
                            user=os.environ['DB_USERNAME'],
                            password=os.environ['DB_PASSWORD'])
    return conn

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
    #print(selected_amenity[0:5])
    query_st='SELECT * FROM planet_osm_polygon WHERE osm_id=\''+selected_amenity[0]+'\';'
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM planet_osm_polygon WHERE admin_level='2';")
    countries = cur.fetchall()
    cur.execute(query_st)
    query=cur.fetchall()
    gdf=gpd.GeoDataFrame.from_postgis(query_st,conn,geom_col='way',index_col='osm_id')
    cur.close()
    conn.close()

    centroid = gdf.to_crs(epsg='4326').unary_union.centroid


    m = folium.Map(location=[centroid.y, centroid.x], zoom_start=6)
    folium.GeoJson(gdf.to_crs(epsg='4326')).add_to(m)

    # set the iframe width and height
    m.get_root().width = "800px"
    m.get_root().height = "600px"
    iframe = m.get_root()._repr_html_()

    return render_template('country.html', country=selected_amenity, iframe=iframe)

if __name__ == '__main__':
    app.run()