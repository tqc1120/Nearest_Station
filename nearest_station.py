from zipfile import ZipFile
from pykml import parser
from bs4 import BeautifulSoup
import math
from collections import defaultdict
from geojson import Feature, Point
import re

def getNearestStation(x, y, z):
    LONGITUDEDISTANCE = 54.6
    LATTITUDEDISTANCE = 69

    kml_file = "SEPTARegionalRailStations2016.kmz"
    kmz = ZipFile(kml_file, 'r')
    with kmz.open('doc.kml', 'r') as f:
        doc = parser.parse(f)

    # build station name to coordinate map
    nameToCoordinate = defaultdict(list)

    for pm in doc.getroot().Document.Folder.Placemark:
        coordinate = pm.Point.coordinates
        for d in pm.description:
            s = str(d)

            soup = BeautifulSoup(s, 'html.parser')
            elementList = soup.find_all("td")
            for i, element in enumerate(elementList):
                if "Station_Na" in element:
                    stationName = re.search(r"<td>(.+?)</td>", str(elementList[i + 1]))
                    nameToCoordinate[stationName.group(1)] = str(coordinate).split(',')
                    break
    
    # find nearest station
    minDistance = float("inf")
    nearestStation = ""

    for stationName,coords in nameToCoordinate.items():
        curX, curY, curZ = coords
        cur_Distance = math.sqrt((float(curX) - x) ** 2 + (float(curY) - y) ** 2 + (float(curZ) - z) ** 2)
        if cur_Distance < minDistance:
            minDistance = cur_Distance
            nearestStation = stationName
    
    targetX, targetY, targetZ = nameToCoordinate[nearestStation]

    # calculate distance and direction
    eastWest = round((float(targetX) - x) * LONGITUDEDISTANCE, 2)
    northSouth = round((float(targetY) - y) * LATTITUDEDISTANCE, 2)
    direction1 = ""
    direction2 = ""

    if northSouth > 0:
        direction1 += "To North " + str(northSouth) + " miles"
    else:
        direction1 += "To South " + str(abs(northSouth)) + " miles"
    if eastWest > 0:
        direction2 += "To East " + str(eastWest) + " miles"
    else:
        direction2 += "To West " + str(abs(eastWest)) + " miles"

    # create and return geojson object
    point = Point((float(targetX), float(targetY), float(targetZ)))
    direction = ""
    if eastWest != 0:
        direction += direction1 + ", "
    if northSouth!= 0:
        direction += direction2
    return Feature(geometry=point, properties={"stationName": nearestStation, "direction": direction})
