#!/usr/bin/env python3

# Script to insert all pictures from the camera db onto the projector db
# The actual pictures will need to be transferred over as well

import sqlite3

DB_PROJECTOR = '/Users/Jordan/Developer/eds/capra-database/capra-projector.db'
DB_CAMERA = '/Users/Jordan/Developer/eds/capra-database/capra-camera.db'


def main():
    print('Starting the insert/transfer script')

    connection_projector = sqlite3.connect(DB_PROJECTOR)
    cursor_projector = connection_projector.cursor()
    attach_statment = "ATTACH '{db}' AS camera".format(db=DB_CAMERA)
    cursor_projector.execute(attach_statment)

    # Get number of pictures and hikes
    cursor_projector.execute("SELECT COUNT(*) FROM camera.pictures2")
    all_rows = cursor_projector.fetchall()
    num_pics = all_rows[0][0]

    cursor_projector.execute("SELECT COUNT(*) FROM camera.hikes")
    all_rows = cursor_projector.fetchall()
    num_hikes = all_rows[0][0]

    # Execute statements
    # cursor_projector.execute("INSERT INTO pictures SELECT * FROM camera.pictures2")
    # connection_projector.commit()
    # print('Finished inserting {n} pictures from camera'.format(n=num_pics))

    # cursor_projector.execute("INSERT INTO hikes SELECT * FROM camera.hikes")
    # connection_projector.commit()
    # print('Finished inserting {n} hikes from camera'.format(n=num_hikes))

    cursor_projector.execute("SELECT * FROM camera.pictures2")
    all_rows = cursor_projector.fetchall()
    for row in all_rows:
        # print(row)

        # pictures2
        statement = "INSERT INTO pictures (time, altitude, color, hike, index_in_hike, camera1, camera2, camera3) VALUES ({t}, {a}, '{c}', {h}, {i}, '{c1}', '{c2}', '{c3}')".format(t=row[0], a=row[1], c=row[2], h=row[3], i=row[4], c1=row[5], c2=row[6], c3=row[7])

        # pictures
        # statement = "INSERT INTO pictures (time, altitude, color, hike, index_in_hike, camera1, camera2, camera3) VALUES ({t}, {a}, '{c}', {h}, {i}, '{c1}', '{c2}', '{c3}')".format(t=row[1], a=row[2], c=row[3], h=row[4], i=row[5], c1=row[6], c2=row[7], c3=row[8])

        # print(statement)
        cursor_projector.execute(statement)
        connection_projector.commit()


def insert_pictures():
    print('')


if __name__ == "__main__":
    main()
