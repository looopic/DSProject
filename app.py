import os
import psycopg2
from flask import Flask, render_template, request
import geopandas

app = Flask(__name__)

def get_db_connection():
    conn = psycopg2.connect(host='localhost',
                            database=os.environ['DB_NAME'],
                            user=os.environ['DB_USERNAME'],
                            password=os.environ['DB_PASSWORD'])
    return conn

@app.route('/', methods=['GET','POST'])
def index():
    amenities=refresh()
    if request.method == 'POST':
        return get_amenity()
    return render_template('index.html', amenities=amenities)

def refresh():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('SELECT DISTINCT amenity FROM planet_osm_polygon;')
    amenities = cur.fetchall()
    cur.close()
    conn.close()
    return amenities

@app.route('/amenity', methods=['GET','POST'])
def get_amenity():
    selected_amenity = request.form['amenity']
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('SELECT DISTINCT amenity FROM planet_osm_polygon;')
    amenities = cur.fetchall()
    cur.execute('SELECT * FROM planet_osm_polygon WHERE amenity='+selected_amenity+';')
    query=cur.fetchall()
    cur.close()
    conn.close()
    return render_template('index.html', amenities=amenities, query=query)

if __name__ == '__main__':
    app.run()