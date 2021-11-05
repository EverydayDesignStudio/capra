#!/usr/bin/env python3

'''Easily round column values for a Capra database
Set the SQLITE_DB path before running'''

import sqlite3
from capra_data_types import Picture, Hike
from sql_controller import SQLController

SQLITE_DB = '/Volumes/capra-hd/capra_projector_clean.db'
connection = sqlite3.connect(SQLITE_DB)
cursor = connection.cursor()


# TODO: Uncomment a function, depending on what you want to clean
def main():
    print('Starting Database cleaning program:\n')

    round_times()
    round_altitudes()

    # TODO: Make sure you go through the TODO's in clean_altitudes()
    # clean_altitudes()

    # insert_new_times(8, 1556499600)


def round_times():
    '''Rounds `time` for table `pictures`.
    Rounds `start_time`, `end_time` for table `hikes`'''

    # Round the time for table: pictures
    cursor.execute('SELECT * FROM pictures ORDER BY picture_id ASC')
    all_rows = cursor.fetchall()
    i = 0
    for row in all_rows:
        id = row[0]
        time = round(row[1], 0)

        cursor.execute('UPDATE pictures SET time={t}, updated_date_time=datetime() WHERE picture_id={id}'.format(t=time, id=id))
        connection.commit()
        i += 1

        if i % 1000 == 0:
            print(f'{i} rows in pictures updated')
    print(f'Updated time in [{i}] rows in pictures\n')

    # Round the start_time and end_time for table: hikes
    cursor.execute('SELECT * FROM hikes ORDER BY hike_id ASC')
    all_rows = cursor.fetchall()
    i = 0
    for row in all_rows:
        hike_id = row[0]
        start_time = round(row[3], 0)
        end_time = round(row[9], 0)

        cursor.execute('UPDATE hikes SET start_time={st}, end_time={et}, updated_date_time=datetime() WHERE hike_id={id}'.format(st=start_time, et=end_time, id=hike_id))
        connection.commit()
        i += 1
    print(f'Updated start_time, end_time in [{i}] rows in hikes')


def round_altitudes():
    '''Round the avg_altitude for table: hikes'''

    cursor.execute('SELECT * FROM hikes ORDER BY hike_id ASC')
    all_rows = cursor.fetchall()
    i = 0
    for row in all_rows:
        hike_id = row[0]
        avg_altitude = round(row[1], 3)
        print(f'{hike_id} \t {avg_altitude}')

        cursor.execute('UPDATE hikes SET avg_altitude={a}, updated_date_time=datetime() WHERE hike_id={id}'.format(a=avg_altitude, id=hike_id))
        connection.commit()
        i += 1
    print(f'Updated avg_altitude in [{i}] rows in hikes')


def insert_new_times(hike: int, start_time: float):
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


if __name__ == "__main__":
    main()
