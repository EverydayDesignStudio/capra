# Controller to handle the projector UI and camera mainloop talking with the SQLite database

import os
import sqlite3
import time
from classes.capra_data_types import Picture, Hike
from classes.sql_statements import SQLStatements


class SQLController:
    def __init__(self, database: str):
        # TODO - be aware that this could potentially be dangerous for thread safety
        self.connection = sqlite3.connect(database, check_same_thread=False)
        self.statements = SQLStatements()

    # Helper methods
    # _underscores signify that they should be treated as private functions to  this class
    def _build_picture_from_row(self, row: list) -> Picture:
        picture = Picture(picture_id=row[0], time=row[1], altitude=row[2],
                          brightness=row[3], b_rank=row[4], hue=row[5], h_rank=row[6],
                          hue_lumosity=row[7], hl_rank=row[8], hike_id=row[9], index_in_hike=row[10],
                          camera1=row[11], camera2=row[12], camera3=row[13], camera_land=row[14])

        return picture

    def _build_hike_from_row(self, row: list) -> Hike:
        hike = Hike(hike_id=row[0], avg_altitude=row[1],
                    avg_brightness=row[2], avg_hue=row[3], avg_hue_lumosity=row[4],
                    start_time=row[5], end_time=row[6], pictures_num=row[7], path=row[8])

        return hike

    def _get_picture_from_sql_statement(self, statement: str) -> Picture:
        cursor = self.connection.cursor()
        cursor.execute(statement)
        all_rows = cursor.fetchall()
        picture = self._build_picture_from_row(all_rows[0])

        picture.print_obj()

        return picture

    def _get_num_from_statement(self, statement: str):
        cursor = self.connection.cursor()
        cursor.execute(statement)
        row = cursor.fetchone()

        # Error safety check
        if row is None:
            return 0
        else:
            return row[0]

    # Projector
    # --------------------------------------------------------------------------
    def get_next_picture(self, current_picture: Picture, mode: int, is_across_hikes: bool) -> Picture:
        if is_across_hikes:     # Across all hikes: rotary encoder is pressed
            if mode == 0:       # Time
                return self.next_time_picture_across_hikes(current_picture)
            elif mode == 1:     # Altitude
                return self.next_altitude_picture_across_hikes(current_picture)
            elif mode == 2:     # Color
                # TODO return self.next_color_picture_across_hikes(current_picture)
                print('Color across hikes not implemented yet')
                return current_picture
        else:                   # In current hike: rotary encoder not pressed
            if mode == 0:       # Time
                return self.next_time_picture_in_hike(current_picture)
            elif mode == 1:     # Altitude
                return self.next_altitude_picture_in_hike(current_picture)
            elif mode == 2:     # Color
                # TODO return self.next_altitude_picture_in_hike(current_picture)
                print('Color in hikes is not implemented yet')
                return current_picture

    def get_previous_picture(self, current_picture: Picture, mode: int, is_across_hikes: bool) -> Picture:
        if is_across_hikes:     # Across all hikes: rotary encoder is pressed
            if mode == 0:       # Time
                return self.previous_time_picture_across_hikes(current_picture)
            elif mode == 1:     # Altitude
                return self.previous_altitude_picture_across_hikes(current_picture)
            elif mode == 2:     # Color
                # TODO return self.previous_color_picture_in_hike(current_picture)
                print('Color across hikes not implemented yet')
                return current_picture
        else:                   # In current hike: rotary encoder not pressed
            if mode == 0:       # Time
                return self.previous_time_picture_in_hike(current_picture)
            elif mode == 1:     # Altitude
                return self.previous_altitude_picture_in_hike(current_picture)
            elif mode == 2:     # Color
                # TODO return self.previous_altitude_picture_in_hike(current_picture)
                print('Color in hikes is not implemented yet')
                return current_picture

    # Time - across hikes
    def get_first_time_picture(self) -> Picture:
        sql = self.statements.select_by_time_first_picture()
        return self._get_picture_from_sql_statement(sql)

    def get_last_time_picture(self) -> Picture:
        sql = self.statements.select_by_time_last_picture()
        return self._get_picture_from_sql_statement(sql)

    def next_time_picture_across_hikes(self, current_picture: Picture) -> Picture:
        cursor = self.connection.cursor()
        cursor.execute(self.statements.select_by_time_next_picture(current_picture.time))
        all_rows = cursor.fetchall()
        if not all_rows:
            return self.get_first_time_picture()
        else:  # there is a next time picture
            return self._build_picture_from_row(all_rows[0])

    def previous_time_picture_across_hikes(self, current_picture: Picture) -> Picture:
        cursor = self.connection.cursor()
        cursor.execute(self.statements.select_by_time_previous_picture(current_picture.time))
        all_rows = cursor.fetchall()
        if not all_rows:
            return self.get_last_time_picture()
        else:  # there is a previous time picture
            return self._build_picture_from_row(all_rows[0])

    # Time - in a hike
    def get_first_time_picture_in_hike(self, hike_id: float) -> Picture:
        sql = self.statements.select_by_time_first_picture_in_hike(hike_id)
        return self._get_picture_from_sql_statement(sql)

    def get_last_time_picture_in_hike(self, hike_id: float) -> Picture:
        sql = self.statements.select_by_time_last_picture_in_hike(hike_id)
        return self._get_picture_from_sql_statement(sql)

    def next_time_picture_in_hike(self, current_picture: Picture) -> Picture:
        cursor = self.connection.cursor()
        h = current_picture.hike_id
        t = current_picture.time

        cursor.execute(self.statements.select_by_time_next_picture_in_hike(hike_id=h, time=t))
        all_rows = cursor.fetchall()
        if not all_rows:
            return self.get_first_time_picture_in_hike(hike_id=h)
        else:  # there is a next time picture
            return self._build_picture_from_row(all_rows[0])

    def previous_time_picture_in_hike(self, current_picture: Picture) -> Picture:
        cursor = self.connection.cursor()
        h = current_picture.hike_id
        t = current_picture.time

        cursor.execute(self.statements.select_by_time_previous_picture_in_hike(hike_id=h, time=t))
        all_rows = cursor.fetchall()
        if not all_rows:
            return self.get_last_time_picture_in_hike(hike_id=h)
        else:  # there is a next time picture
            return self._build_picture_from_row(all_rows[0])

    # Altitude - get starting picture
    def get_greatest_altitude_picture(self) -> Picture:
        sql = self.statements.select_by_altitude_greatest_picture()
        return self._get_picture_from_sql_statement(sql)

    def get_least_altitude_picture(self) -> Picture:
        sql = self.statements.select_by_altitude_least_picture()
        return self._get_picture_from_sql_statement(sql)

    # Altitude - next & previous across hikes
    def next_altitude_picture_across_hikes(self, current_picture: Picture) -> Picture:
        cursor = self.connection.cursor()
        t = current_picture.time
        alt = current_picture.altitude

        cursor.execute(self.statements.find_size_by_altitude_greater_time(altitude=alt, time=t))
        all_rows = cursor.fetchall()
        count = all_rows[0][0]
        print(count)

        if count == 0:
            cursor.execute(self.statements.select_by_greater_altitude_next_picture(altitude=alt))
        elif count > 0:
            cursor.execute(
                self.statements.select_by_equal_altitude_next_picture(altitude=alt, time=t))
        all_rows = cursor.fetchall()

        # end of the list of altitudes, loop back around to least altitude
        if not all_rows:
            return self.get_least_altitude_picture()
        else:  # there is a next picture
            return self._build_picture_from_row(all_rows[0])

    def previous_altitude_picture_across_hikes(self, current_picture: Picture) -> Picture:
        cursor = self.connection.cursor()
        t = current_picture.time
        alt = current_picture.altitude

        cursor.execute(self.statements.find_size_by_altitude_less_time(altitude=alt, time=t))
        all_rows = cursor.fetchall()
        count = all_rows[0][0]

        if count == 0:
            cursor.execute(self.statements.select_by_less_altitude_previous_picture(altitude=alt))
        elif count > 0:
            cursor.execute(
                self.statements.select_by_equal_altitude_previous_picture(altitude=alt, time=t))
        all_rows = cursor.fetchall()

        # end of the list of altitudes, loop back around to greatest altitude
        if not all_rows:
            return self.get_greatest_altitude_picture()
        else:  # there is a previous picture
            return self._build_picture_from_row(all_rows[0])

    # Altitude - greatest & least in a hike
    def get_greatest_altitude_picture_in_hike(self, hike_id: float) -> Picture:
        sql = self.statements.select_by_altitude_greatest_picture_in_hike(hike_id)
        return self._get_picture_from_sql_statement(sql)

    def get_least_altitude_picture_in_hike(self, hike_id: float) -> Picture:
        sql = self.statements.select_by_altitude_least_picture_in_hike(hike_id)
        return self._get_picture_from_sql_statement(sql)

    # Altitude - next & previous in a hike
    def next_altitude_picture_in_hike(self, current_picture: Picture) -> Picture:
        cursor = self.connection.cursor()
        h = current_picture.hike_id
        t = current_picture.time
        alt = current_picture.altitude

        cursor.execute(self.statements.find_size_by_altitude_greater_time_in_hike(hike_id=h, altitude=alt, time=t))
        all_rows = cursor.fetchall()
        count = all_rows[0][0]
        # print(count)
        if count == 0:
            cursor.execute(self.statements.select_by_greater_altitude_next_picture_in_hike(hike_id=h, altitude=alt))
        elif count > 0:
            cursor.execute(
                self.statements.select_by_equal_altitude_next_picture_in_hike(hike_id=h, altitude=alt, time=t))
        all_rows = cursor.fetchall()

        if not all_rows:
            return self.get_least_altitude_picture_in_hike(hike_id=h)
        else:
            return self._build_picture_from_row(all_rows[0])

    def previous_altitude_picture_in_hike(self, current_picture: Picture) -> Picture:
        cursor = self.connection.cursor()
        h = current_picture.hike_id
        t = current_picture.time
        alt = current_picture.altitude

        cursor.execute(self.statements.find_size_by_altitude_less_time_in_hike(hike_id=h, altitude=alt, time=t))
        all_rows = cursor.fetchall()
        count = all_rows[0][0]

        if count == 0:
            cursor.execute(self.statements.select_by_less_altitude_previous_picture_in_hike(hike_id=h, altitude=alt))
        elif count > 0:
            cursor.execute(
                self.statements.select_by_equal_altitude_previous_picture_in_hike(hike_id=h, altitude=alt, time=t))
        all_rows = cursor.fetchall()

        # end of the list of previous altitudes, loop back around to greatest altitude
        if not all_rows:
            return self.get_greatest_altitude_picture_in_hike(hike_id=h)
        else:  # there is a previous picture in hike
            return self._build_picture_from_row(all_rows[0])

    # Hikes
    # --------------------------------------------------------------------------
    def get_size_of_hike(self, current_picture: Picture) -> int:
        cursor = self.connection.cursor()
        h = current_picture.hike_id
        cursor.execute(self.statements.select_size_of_hike(hike_id=h))
        row = cursor.fetchone()
        size = int(row[0])
        return size

    def get_current_hike(self, current_picture: Picture) -> Hike:
        cursor = self.connection.cursor()
        h = current_picture.hike_id
        cursor.execute(self.statements.select_hike_by_id(hike_id=h))
        all_rows = cursor.fetchall()
        return self._build_hike_from_row(all_rows[0])

    # Camera
    # --------------------------------------------------------------------------
    def _get_time_since_last_hike(self) -> float:
        cursor = self.connection.cursor()
        cursor.execute(self.statements.select_last_hike_end_time())
        row = cursor.fetchone()

        # First hike on camera won't have a time to return yet
        if row is None:
            return -1
        else:
            last_time = row[0]
            current_time = time.time()
            time_since = current_time - last_time
            return round(time_since, 0)

    def _create_new_hike(self):
        cursor = self.connection.cursor()
        t = time.time()
        cursor.execute(self.statements.insert_new_hike(t))
        self.connection.commit()

    def get_hike_count(self) -> int:
        return self._get_num_from_statement(self.statements.select_hike_count())

    def get_last_hike_id(self) -> int:
        cursor = self.connection.cursor()
        cursor.execute(self.statements.select_last_hike_id())
        row = cursor.fetchone()

        if row is None:
            return 0
        else:
            return row[0]

    def get_valid_photos_in_given_hike(self, hike_id: int) -> int:
        cursor = self.connection.cursor()
        cursor.execute(self.statements.select_valid_photos_in_given_hike(hike_id))
        row = cursor.fetchall()
        return row

    def get_last_photo_index_of_hike(self, hike_id: int) -> int:
        cursor = self.connection.cursor()
        cursor.execute(self.statements.select_last_photo_index_of_hike(hike_id))
        row = cursor.fetchone()

        # A new hike won't have an index to return yet, hence it will be null
        if row is None:
            return 0
        else:
            return row[0]

    def get_last_altitude(self) -> float:
        alt = self._get_num_from_statement(self.statements.select_last_altitude_recorded())
        return alt

    def get_last_rowid(self) -> int:
        rowid = self._get_num_from_statement(self.statements.select_last_row_id())
        return rowid

    # Determine whether to create new hike or continue the last hike
    def will_create_new_hike(self, NEW_HIKE_TIME, DIRECTORY) -> bool:
        time_since_last_hike = self._get_time_since_last_hike()

        # Create a new hike; -1 indicates this is the first hike in db
        if time_since_last_hike > NEW_HIKE_TIME or time_since_last_hike == -1:
            print('Creating new hike:')
            self._create_new_hike()

            # Create folder in harddrive to save photos
            hike_num = self.get_last_hike_id()
            folder = 'hike{n}/'.format(n=hike_num)
            path = DIRECTORY + folder

            os.makedirs(path)
            self._set_hike_path(hike_num, path)

            return True
        else:
            print('Continuing last hike:')
            return False

    def create_new_picture(self, hike_id: int, photo_index: int, photo_time: float):
        cursor = self.connection.cursor()
        ts = photo_time
        cursor.execute(self.statements.insert_new_picture(ts, hike_id, photo_index))
        self.connection.commit()

    def _set_hike_path(self, hike_id: int, hike_path: str):
        cursor = self.connection.cursor()
        cursor.execute(self.statements.update_hike_path(hike_path, hike_id))
        self.connection.commit()

    def set_image_path(self, cam_num: int, path: str, hike_id: int, photo_index: int):
        cursor = self.connection.cursor()
        cursor.execute(self.statements.update_picture_image_path(cam_num, path, hike_id, photo_index))
        self.connection.commit()

    def set_picture_time_altitude(self, altitude: float, hike_id: int, photo_index: int):
        cursor = self.connection.cursor()
        ts = time.time()
        cursor.execute(self.statements.update_picture_time_altitude(ts, altitude, hike_id, photo_index))
        self.connection.commit()

    def set_hike_endtime_picture_count(self, count: int, hike_id: int):
        cursor = self.connection.cursor()
        ts = time.time()
        cursor.execute(self.statements.update_hike_endtime_picture_count(ts, count, hike_id))
        self.connection.commit()

    def set_altitude_for_rowid(self, alt: float, id: int):
        cursor = self.connection.cursor()
        cursor.execute(self.statements.update_picture_altitude(alt, id))
        self.connection.commit()

    # Transfer
    # --------------------------------------------------------------------------
    def delete_picture_and_hikes_tables(self):
        cursor = self.connection.cursor()

        cursor.execute(self.statements.delete_pictures())
        self.connection.commit()

        cursor.execute(self.statements.delete_hikes())
        self.connection.commit()

    def upsert_hike(self, hike_id: str, avg_altitude: float, avg_hue: float, avg_saturation: float, avg_value: float, start_time: float, end_time: float, pictures: int, path: str):
        cursor = self.connection.cursor()
        cursor.execute(self.statements.upsert_hike_row(hike_id, avg_altitude, avg_hue, avg_saturation, avg_value, start_time, end_time, pictures, path))
        self.connection.commit()

    def upsert_picture(self, time: float, hike: int, index_in_hike: int, altitude: float, hue: float, saturation: float, value: float, red: float, green: float, blue: float, camera1: str, camera2: str, camera3: str, camera_landscape: str):
        cursor = self.connection.cursor()
        cursor.execute(self.statements.upsert_picture_row(time, hike, index_in_hike, altitude, hue, saturation, value, red, green, blue, camera1, camera2, camera3, camera_landscape))
        self.connection.commit()

    def get_size_of_hike(self, hike_id: int) -> int:
        cursor = self.connection.cursor()
        cursor.execute(self.statements.get_size_of_hike(hike_id=hike_id))
        row = cursor.fetchone()
        if (row is None):
            return None
        else:
            return row[0]

    def get_hike_average_color(self, hike_id: int):
        cursor = self.connection.cursor()
        cursor.execute(self.statements.get_hike_average_color(hike_id=hike_id))
        res = cursor.fetchall()
        if (res is None):
            return None
        else:
            return res[0]

    def get_picture_dominant_color(self, time: float):
        cursor = self.connection.cursor()
        cursor.execute(self.statements.get_dominant_color_for_picture_of_given_timestamp(time=time))
        res = cursor.fetchall()
        return res[0]

    def get_picture_at_timestamp(self, time: float):
        cursor = self.connection.cursor()
        cursor.execute(self.statements.get_picture_with_timestamp(time=time))
        res = cursor.fetchone()
        return res[0]

    def get_hike_path(self, hike_id: int):
        cursor = self.connection.cursor()
        cursor.execute(self.statements.get_hike_path(hike_id))
        row = cursor.fetchone()
        return row
