#!/usr/bin/env python3

import time
import sqlite3
from capra_data_types import Picture, Hike
from sql_controller import SQLController

SQLITE_DB = '/Volumes/capra-hd/capra_projector_clean.db'
connection = sqlite3.connect(SQLITE_DB)
cursor = connection.cursor()


def main():
    print('Starting SQLite3 program')
    clean_times(8, 1556499600)


def clean_altitudes():
    # Get starting picture_id
    # TODO: Change the hike value
    cursor.execute('SELECT * FROM pictures WHERE hike=19 LIMIT 1')
    all_rows = cursor.fetchall()
    picture_id = all_rows[0][0]
    print(picture_id)

    # TODO: Change these variables
    last_altitude = 0  # Change to a reasonable starting altitude value
    for x in range(picture_id, 9753):  # Change the upper bound
        try:
            cursor.execute('SELECT * FROM pictures WHERE picture_id={id}'.format(id=x))
            all_rows = cursor.fetchall()

            alt = all_rows[0][2]
            if alt > 60000:
                cursor.execute('UPDATE pictures SET altitude={a} WHERE picture_id={id}'.format(a=last_altitude, id=x))
                connection.commit()

                print('ERROR: {a} ||  last altitude: {a2}'.format(a=alt, a2=last_altitude))
            else:
                last_altitude = alt
                # print('normal: {a}'.format(a=alt))
        except:
            print('SORRY NO DATA HERE')
            continue


def clean_times(hike: int, start_time: float):
    # Get starting and ending picture_id
    cursor.execute('SELECT * FROM pictures WHERE hike={h} ORDER BY picture_id ASC LIMIT 1'.format(h=hike))
    all_rows = cursor.fetchall()
    start_id = all_rows[0][0]
    print(start_id)

    cursor.execute('SELECT * FROM pictures WHERE hike={h} ORDER BY picture_id DESC LIMIT 1'.format(h=hike))
    all_rows = cursor.fetchall()
    end_id = all_rows[0][0]
    print(end_id)

    new_time = start_time

    # Loop through
    for x in range(start_id, end_id+1):
        try:
            cursor.execute('SELECT * FROM pictures WHERE picture_id={id}'.format(id=x))

            cursor.execute('UPDATE pictures SET time={t} WHERE picture_id={id}'.format(t=new_time, id=x))
            connection.commit()
            new_time = new_time + 4
        except:
            print('SORRY NO DATA HERE')
            continue

    # Now update the start and end values on the hike
    # START
    cursor.execute('UPDATE hikes SET start_time={t} WHERE hike_id={id}'.format(t=start_time, id=hike))
    connection.commit()

    # END
    cursor.execute('SELECT * FROM pictures WHERE hike={h} ORDER BY index_in_hike DESC LIMIT 1'.format(h=hike))
    all_rows = cursor.fetchall()
    end_time = all_rows[0][1]

    cursor.execute('UPDATE hikes SET end_time={t} WHERE hike_id={id}'.format(t=end_time, id=hike))
    connection.commit()


def helper_function():
    print('hello there')
    # for x in range(1, 2334):
    # cursor.execute('SELECT * FROM pictures WHERE hike=15 AND index_in_hike={x}'.format(x=x))


if __name__ == "__main__":
    main()
