#!/usr/bin/env python3

# Script to insert all pictures from the camera db onto the projector db
# The actual pictures will need to be transferred over as well

# READ ME!!!
# This program was last used to insert hikes that needed to be renamed
# Make sure you read through the code before blindly running,
# and always duplicate your db before inserting via script

import sqlite3

# Local
# DB_PROJECTOR = '/Users/Jordan/Developer/eds/capra-database/capra-projector.db'
DB_PROJECTOR = '/Users/Jordan/Dropbox/CapraData/july2020/capra_projector.db'
# DB_CAMERA = '/Users/Jordan/Developer/eds/capra-database/capra-camera.db'
DB_CAMERA = '/Users/Jordan/Dropbox/CapraData/july2020/capra_camera.db'

# External (Mac)
# DB_CAMERA = '/Volumes/capra-hd/capra_camera.db'
# DB_PROJECTOR = '/Volumes/capra-hd/capra_projector.db'

# External (Raspberry Pi)
# DB_CAMERA = '/media/pi/capra-hd/capra_camera.db'
# DB_PROJECTOR = '/media/pi/capra-hd/capra_projector.db'


def main():
    print('Starting the insert/transfer script')

    # Attach the camera to the projector database
    connection_projector = sqlite3.connect(DB_PROJECTOR)
    cursor_projector = connection_projector.cursor()
    attach_statement = "ATTACH '{db}' AS camera".format(db=DB_CAMERA)
    cursor_projector.execute(attach_statement)

    # Insert Pictures
    # insert_pictures(connection_projector, cursor_projector)

    # Insert Hikes
    # insert_hikes(connection_projector, cursor_projector)

    # TODO test this functionality first
    # Delete the pictures and hikes on the camera database
    # delete_pictures_hikes(connection_projector, cursor_projector)


def insert_pictures(connection: sqlite3.Connection, cursor: sqlite3.Connection.cursor):
    # Get number of pictures
    cursor.execute("SELECT COUNT(*) FROM camera.pictures")
    all_rows = cursor.fetchall()
    num_pics = all_rows[0][0]

    # Insert all pictures
    cursor.execute("SELECT * FROM camera.pictures")
    all_rows = cursor.fetchall()
    picture_count = 0

    count17 = 0
    count18 = 0
    count19 = 0
    count20 = 0

    old_id = 0
    new_id = 0

    for row in all_rows:
        # print(row)

        if row[2] == 17:
            old_id = 17
            new_id = 30
            count17 += 1

        elif row[2] == 18:
            old_id = 18
            new_id = 31
            count18 += 1

        elif row[2] == 19:
            old_id = 19
            new_id = 32
            count19 += 1

        elif row[2] == 20:
            old_id = 20
            new_id = 33
            count20 += 1

        path1 = change_cam_location(row[4], old_id, new_id)
        path2 = change_cam_location(row[5], old_id, new_id)
        path3 = change_cam_location(row[6], old_id, new_id)

        statement = "INSERT INTO pictures (time, altitude, hike, index_in_hike, camera1, camera2, camera3, created_date_time, updated_date_time) VALUES ({t}, {a}, {h}, {i}, '{c1}', '{c2}', '{c3}', '{t1}', '{t2}')".format(t=row[0], a=row[1], h=new_id, i=row[3], c1=path1, c2=path2, c3=path3, t1=row[7], t2=row[8])
        cursor.execute(statement)
        connection.commit()
        picture_count += 1

    print('Finished inserting {i} of {n} pictures from camera'.format(i=picture_count, n=num_pics))
    print('HIKE17 : {c17}  |  HIKE18 : {c18}  |  HIKE19 : {c19}  |  HIKE20 : {c20}'.format(c17=count17, c18=count18, c19=count19, c20=count20))


def change_cam_location(path, old_id, new_id):
    path_split = path.split(str(old_id))
    new_path = path_split[0] + str(new_id) + path_split[1]
    return new_path


def insert_hikes(connection: sqlite3.Connection, cursor: sqlite3.Connection.cursor):
    # Get number of hikes
    cursor.execute("SELECT COUNT(*) FROM camera.hikes")
    all_rows = cursor.fetchall()
    num_hikes = all_rows[0][0]

    # Insert all hikes
    cursor.execute("SELECT * FROM camera.hikes")
    all_rows = cursor.fetchall()
    hike_count = 0
    for row in all_rows:
        # print(row)

        new_id = row[0] + 13
        new_path = change_cam_location(row[4], row[0], new_id)

        statement = "INSERT INTO hikes (hike_id, start_time, end_time, pictures, path, created_date_time, updated_date_time) VALUES ({id}, {st}, {et}, {p}, '{pth}', '{t1}', '{t2}')".format(id=new_id, st=row[1], et=row[2], p=row[3], pth=new_path, t1=row[5], t2=row[6])
        cursor.execute(statement)
        connection.commit()
        hike_count += 1
    print('Finished inserting {i} of {n} hikes from camera'.format(i=hike_count, n=num_hikes))

    # Old Insert Hikes
    # cursor_projector.execute("INSERT INTO hikes SELECT * FROM camera.hikes")
    # connection_projector.commit()
    # print('Finished inserting {n} hikes from camera'.format(n=num_hikes))


def delete_pictures_hikes(connection: sqlite3.Connection, cursor: sqlite3.Connection.cursor):
    cursor.execute("DELETE FROM camera.pictures")
    connection.commit()
    cursor.execute("DELETE FROM camera.hikes")
    connection.commit()


if __name__ == "__main__":
    main()
