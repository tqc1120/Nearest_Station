import csv
from collections import defaultdict
import math
import get_gj, database, db_lock

dc_file_path = 'Metro_Stations_Regional.csv'
nyc_file_path = 'DOITT_SUBWAY_STATION_01_13SEPT2010.csv'

def read_dc_csv():
    # build station name to coordinate map
    nameToCoordinate = defaultdict(list)

    with open(dc_file_path, 'r', newline='') as csvfile:
        csvreader = csv.reader(csvfile)
        # Skip the header row 
        header = next(csvreader, None)
        for row in csvreader:
            station_name = row[2]
            coords = [row[0], row[1]]
            nameToCoordinate[station_name] = coords
        return nameToCoordinate

def read_nyc_csv():
    # build station name to coordinate map
    nameToCoordinate = defaultdict(list)

    with open(nyc_file_path, 'r', newline='') as csvfile:
        csvreader = csv.reader(csvfile)
        # Skip the header row 
        header = next(csvreader, None)
        for row in csvreader:
            station_name = row[2]
            coords = row[3][7: len(row[3]) - 1].split(" ")
            nameToCoordinate[station_name] = coords
        return nameToCoordinate

def getNearestStation(cursor, cnxn, x, y, z, nameToCoordinate):
    LONGITUDEDISTANCE = 54.6
    LATTITUDEDISTANCE = 69

    # find nearest station
    minDistance = float("inf")
    nearestStation = ""

    for stationName,coords in nameToCoordinate.items():
        curX, curY = coords
        cur_Distance = math.sqrt((float(curX) - x) ** 2 + (float(curY) - y) ** 2)
        if cur_Distance < minDistance:
            minDistance = cur_Distance
            nearestStation = stationName

    targetX, targetY = nameToCoordinate[nearestStation]

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
    database.add_info_to_db(cursor, cnxn, x, y, z, float(targetX), float(targetY), 0.0, nearestStation, direction)
    db_lock.release(cursor, cnxn)

    return get_gj.generate_geojson(float(targetX), float(targetY), 0.0, nearestStation, direction)
