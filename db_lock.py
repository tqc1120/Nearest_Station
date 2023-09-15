def acquire(cursor, cnxn):
    while True:
        if not check_db_is_locked(cursor):
            break

    cursor.execute("UPDATE DB_Lock SET lock_on = ?;""", "True")
    cnxn.commit()

def release(cursor, cnxn):
    cursor.execute("UPDATE DB_Lock SET lock_on = ?;""", "False")
    cnxn.commit()

def check_db_is_locked(cursor):
    query = "SELECT lock_on FROM DB_Lock"
    cursor.execute(query)
    rows = cursor.fetchall()

    if rows[0][0] == "True":
        return True
    return False
