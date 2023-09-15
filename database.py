import get_gj

def check_coords_in_db(cursor, x, y, z):
  query = "SELECT * FROM Nearest_Station WITH (HOLDLOCK)"

  cursor.execute(query)
  rows = cursor.fetchall()

  for row in rows:
    if row[0] == x and row[1] == y and row[2] == z:
      return get_gj.generate_geojson(row[3], row[4], row[5], row[6], row[7])
  return None

def add_info_to_db(cursor, cnxn, in_x, in_y, in_z, out_x, out_y, out_z, station, direct): 
  cursor.execute("""INSERT INTO Nearest_Station (input_x, input_y, input_z, output_x, output_y, output_z, station_name, direction) 
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?) """, (in_x, in_y, in_z, out_x, out_y, out_z, station, direct))
  cnxn.commit()
