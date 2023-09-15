from flask import Flask, request, render_template
import nearest_station 

app = Flask(__name__)
doc = nearest_station.readKMLFile()

@app.route("/")
def home():
    return render_template('home.html')

@app.route('/', methods=['POST'])
def my_home_post():
    text = request.form['text'] 
    coords = text.split(",")
    if len(coords) != 3:
        return "Wrong format!"

    for str in coords:
        try:
            float(str)
        except ValueError:
            return "Please input number as coordinate"
    
    x, y, z = float(coords[0]), float(coords[1]), float(coords[2])
    return nearest_station.getNearestStation(x, y, z, doc)

if __name__ == "__main__":
    app.run(debug=True)
    