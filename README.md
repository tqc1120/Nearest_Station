# Nearest_Station
## Write up
1. Create a function that takes a location and finds the nearest SEPTA Regional Rail train station using data set in local file.
The return format of the train station must be in GeoJSON.
Return infomation should include: station name, station coordination, walking directions.
2. Build an HTTP API to expose the function.
3. Ensure the API does not search for the same location more than once at a time, even if multiple instances are running concurrently.