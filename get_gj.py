from geojson import Feature, Point

def generate_geojson(x, y, z, nearestStation, direction):
      point = Point((x, y, z))
      nearestStation = nearestStation
      direction = direction
      return Feature(geometry=point, properties={"stationName": nearestStation, "direction": direction})
