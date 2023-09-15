from flask import Flask, request, render_template
import pyodbc
from cachetools import TTLCache
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import other_cities, database, nearest_station

app = Flask(__name__)

# shared variable: specific city
app.config['city'] = None

# save searched data to cache
cache = TTLCache(maxsize=1000, ttl=60) 

# limit user's request in certain time frame
limiter = Limiter(
    get_remote_address,
    app=app,
    default_limits=["1 per second"],
    storage_uri="memory://",
)

# connect with database
conn_str = (
    r'driver={SQL Server};'
    r'server=(local);'
    r'database=nearest_station;'
    r'trusted_connection=yes;'
    )
cnxn = pyodbc.connect(conn_str, autocommit=False)
cursor = cnxn.cursor()

# dafault data: Philadelphia
doc = nearest_station.readKMLFile()
# D.C. data
station2coords_dc = other_cities.read_dc_csv()
# NYC data
station2coords_nyc = other_cities.read_nyc_csv()

@app.route("/")
def index():
    return render_template('index.html')

@app.route('/button_click', methods=['POST'])
def handle_form():
    database.clear_table(cursor, cnxn)
    cache.clear()

    button_clicked = request.form.get('button')
    if button_clicked == 'Button2':
        app.config['city'] = "DC"
    elif button_clicked == 'Button3':
        app.config['city'] = "NYC"
    else:
        app.config['city'] = "Philadelphia"
    return render_template('search.html')

@app.route('/search', methods=['POST'])
@limiter.limit("1 per second")
def search():
    text = request.form.get('text')

    cached_data = cache.get(text)
    if cached_data:
        return cached_data

    coords = text.split(",")
    if len(coords) != 3:                                                                         
        return "Wrong format!"

    for str in coords:
        try:
            float(str)
        except ValueError:
            return "Please input number as coordinate"

    x, y, z = float(coords[0]), float(coords[1]), float(coords[2])
    
    if app.config['city'] == "DC":
        geojson_file = other_cities.getNearestStation(cursor, cnxn, x, y, z, station2coords_dc)
    elif app.config['city'] == "NYC":
        geojson_file = other_cities.getNearestStation(cursor, cnxn, x, y, z, station2coords_nyc)
    else:
        geojson_file = nearest_station.getNearestStation(cursor, cnxn, x, y, z, doc)
    cache[text] = geojson_file
    return geojson_file

if __name__ == "__main__":
    app.run(debug=True, port = 8000)
