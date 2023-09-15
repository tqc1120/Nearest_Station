# Nearest_Station
## Write up
1. Create a function that takes a location and finds the nearest SEPTA Regional Rail train station using data set in local file.
The return format of the train station must be in GeoJSON.
Return infomation should include: station name, station coordination, walking directions.
2. Build an HTTP API to expose the function.
3. Ensure the API does not search for the same location more than once at a time.  
(I use a database to store the searched information, so the same location will not be searched repeatedly. Also, I use a table as a lock so that before the first instance finishes processing, other instances can not start searching.)
4. Make a single reasonably-sized instance of the API able to serve millions of requests per day.
5. Protect the API against malicious users.
6. Add another two cities data. Users can finds the nearest Rail train station in city they choose.

## Instructions
    python3 main.py
