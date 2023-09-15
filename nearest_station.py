from zipfile import ZipFile
from pykml import parser
from bs4 import BeautifulSoup
import math
from collections import defaultdict
import re
import get_gj
import database
import db_lock

def readKMLFile():
    kml_file = "SEPTARegionalRailStations2016.kmz"
    kmz = ZipFile(kml_file, 'r')
    with kmz.open('doc.kml', 'r') as f:
        doc = parser.parse(f)
        return doc

def getNearestStation(cursor, cnxn, x, y, z, doc):
    LONGITUDEDISTANCE = 54.6
    LATTITUDEDISTANCE = 69
    
    # build station name to coordinate map
    nameToCoordinate = defaultdict(list)

    db_lock.acquire(cursor, cnxn)

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

    # check if coordinate in database
    coord_in_db = database.check_coords_in_db(cursor, x, y, z)

    if coord_in_db:
        db_lock.release(cursor, cnxn)
        return coord_in_db

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

    direction = ""
    if eastWest != 0:
        direction += direction1 + ", "
    if northSouth!= 0:
        direction += direction2
        
    # add new info to database
    database.add_info_to_db(cursor, cnxn, x, y, z, float(targetX), float(targetY), float(targetZ), nearestStation, direction)
    db_lock.release(cursor, cnxn)

    return get_gj.generate_geojson(float(targetX), float(targetY), float(targetZ), nearestStation, direction)
