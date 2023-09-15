from flask import Flask, request, render_template
import nearest_station 
import pyodbc
from cachetools import TTLCache
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

app = Flask(__name__)

cache = TTLCache(maxsize=1000, ttl=60) 
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

doc = nearest_station.readKMLFile()

@app.route("/")
def home():
    return render_template('home.html')

@app.route('/', methods=['POST'])
@limiter.limit("1 per second")
def my_home_post():
    text = request.form['text'] 

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
    print(type(doc))
    # return geojson_file
    geojson_file = nearest_station.getNearestStation(cursor, cnxn, x, y, z, doc)
    cache[text] = geojson_file
    return geojson_file

if __name__ == "__main__":
    app.run(debug=True, port = 8000)
