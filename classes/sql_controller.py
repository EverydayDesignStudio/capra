# Controller to handle the projector UI and camera mainloop talking with the SQLite database

import os
import platform
import sqlite3
import time
from classes.capra_data_types import Picture, Hike
from classes.sql_statements import SQLStatements


class SQLController:
    def __init__(self, database: str, filepath=None):
        # TODO - be aware that this could potentially be dangerous for thread safety
        self.connection = sqlite3.connect(database, check_same_thread=False)
        self.filepath = filepath
        self.statements = SQLStatements()

    # --------------------------------------------------------------------------
    # New Functions 2020 / 2021
    # --------------------------------------------------------------------------

    # Private functions
    def _execute_query(self, query) -> Picture:
        '''Returns the first (row) Picture from a given query'''
        cursor = self.connection.cursor()
        cursor.execute(query)
        all_rows = cursor.fetchall()
        if not all_rows:
            print("ERROR UPON CALLING QUERY:")
            print(query)
            return None
        else:  # new Picture was retrieved from database
            # REMOVE - eventually remove once we have the new test database
            # HACK - due to having two database states, we have to toggle which version
            # of the row builder we currently use
            if platform.system() == 'Darwin' or platform.system() == 'Windows':
                # picture = self._old_build_picture_from_row(all_rows[0])  # slideshow program
                picture = self._build_picture_from_row(all_rows[0])  # database tests
            else:
                picture = self._build_picture_from_row(all_rows[0])
            return picture

    # REMOVE - eventually remove, but leave in for right now while testing hike10
    def _old_build_picture_from_row(self, row: list) -> Picture:
        '''Builds a (Dec. 2020) Picture object from a row in the database'''
        camera1 = self.filepath + '/hike' + str(row[7]) + '/' + str(row[8]) + '_cam1.jpg'
        camera2 = self.filepath + '/hike' + str(row[7]) + '/' + str(row[8]) + '_cam2.jpg'
        camera3 = self.filepath + '/hike' + str(row[7]) + '/' + str(row[8]) + '_cam3.jpg'
        cameraf = self.filepath + '/hike' + str(row[7]) + '/' + str(row[8]) + '_cam2f.jpg'

        picture = Picture(picture_id=row[0], time=row[1], year=row[2], month=row[3], day=row[4],
                          minute=row[5], dayofweek=row[6], hike_id=row[7], index_in_hike=row[8],
                          altitude=row[9], altrank_hike=row[10], altrank_global=row[11], altrank_global_h='nil',
                          color_hsv=row[12], color_rgb=row[13], colorrank_hike=row[15], colorrank_global=row[16],
                          colorrank_global_h='nil', colors_count='nil', colors_rgb='nil', colors_conf='nil',
                          camera1=camera1, camera2=camera2, camera3=camera3, cameraf=cameraf,
                          created=row[24], updated=row[25])
        return picture

    def _build_picture_from_row(self, row: list) -> Picture:
        '''Builds latest version of the Picture object from a row in the database'''

        # TODO - will need to be changed due to accepting the file path from a prompt on startup of the Mac program
        # camera1 = ''
        # camera2 = ''
        # camera3 = ''
        # cameraf = ''
        if platform.system() == 'Darwin' or platform.system() == 'Windows':
            camera1 = self.filepath + '/hike' + str(row[7]) + '/' + str(row[8]) + '_cam1.jpg'
            camera2 = self.filepath + '/hike' + str(row[7]) + '/' + str(row[8]) + '_cam2.jpg'
            camera3 = self.filepath + '/hike' + str(row[7]) + '/' + str(row[8]) + '_cam3.jpg'
            cameraf = self.filepath + '/hike' + str(row[7]) + '/' + str(row[8]) + '_cam2f.jpg'
        elif platform.system() == 'Linux':
            camera1 = row[22]
            camera2 = row[23]
            camera3 = row[24]
            cameraf = row[25]

        picture = Picture(picture_id=row[0], time=row[1], year=row[2], month=row[3], day=row[4],
                          minute=row[5], dayofweek=row[6], hike_id=row[7], index_in_hike=row[8],
                          altitude=row[9], altrank_hike=row[10], altrank_global=row[11], altrank_global_h=row[12],
                          color_hsv=row[13], color_rgb=row[14], colorrank_hike=row[16], colorrank_global=row[17],
                          colorrank_global_h=row[18], colors_count=row[19], colors_rgb=row[20], colors_conf=row[21],
                          camera1=camera1, camera2=camera2, camera3=camera3, cameraf=cameraf,
                          created=row[26], updated=row[27])

        return picture

    # Initializing queries - used to get the initial row from the database
    # TODO - write tests for all of these functions
    def get_picture_with_id(self, id: int) -> Picture:
        sql = self.statements.select_picture_by_id(id)
        return self._execute_query(sql)

    def get_first_time_picture(self) -> Picture:
        sql = self.statements.select_by_time_first_picture()
        return self._execute_query(sql)

    def get_last_time_picture(self) -> Picture:
        sql = self.statements.select_by_time_last_picture()
        return self._execute_query(sql)

    def get_first_time_picture_in_hike(self, hike_id: float) -> Picture:
        sql = self.statements.select_by_time_first_picture_in_hike(hike_id)
        return self._execute_query(sql)

    def get_last_time_picture_in_hike(self, hike_id: float) -> Picture:
        sql = self.statements.select_by_time_last_picture_in_hike(hike_id)
        return self._execute_query(sql)

    def get_greatest_altitude_picture(self) -> Picture:
        sql = self.statements.select_by_altitude_greatest_picture()
        return self._execute_query(sql)

    def get_least_altitude_picture(self) -> Picture:
        sql = self.statements.select_by_altitude_least_picture()
        return self._execute_query(sql)

    def get_greatest_altitude_picture_in_hike(self, hike_id: float) -> Picture:
        sql = self.statements.select_by_altitude_greatest_picture_in_hike(hike_id)
        return self._execute_query(sql)

    def get_least_altitude_picture_in_hike(self, hike_id: float) -> Picture:
        sql = self.statements.select_by_altitude_least_picture_in_hike(hike_id)
        return self._execute_query(sql)

    # Time
    # --------------------------------------------------------------------------

    # Time in Hikes
    def get_next_time_in_hikes(self, current: Picture, offset: int) -> Picture:
        sql = self.statements.select_next_time_in_hikes(current.time, offset)
        return self._execute_query(sql)

    def get_previous_time_in_hikes(self, current: Picture, offset: int) -> Picture:
        sql = self.statements.select_previous_time_in_hikes(current.time, offset)
        return self._execute_query(sql)

    # Time in Global
    def get_next_time_in_global(self, current: Picture, offset: int) -> Picture:
        sql = self.statements.select_next_time_in_global(current.minute, current.time, offset)
        return self._execute_query(sql)

    def get_previous_time_in_global(self, current: Picture, offset: int) -> Picture:
        sql = self.statements.select_previous_time_in_global(current.minute, current.time, offset)
        return self._execute_query(sql)

    # Time Skip in Hikes
    def get_next_time_skip_in_hikes(self, current: Picture) -> Picture:
        sql = self.statements.select_next_time_skip_in_hikes(current.hike_id, current.time)
        return self._execute_query(sql)

    def get_previous_time_skip_in_hikes(self, current: Picture) -> Picture:
        sql = self.statements.select_previous_time_skip_in_hikes(current.hike_id, current.time)
        return self._execute_query(sql)

    # Time Skip in Global
    def get_next_time_skip_in_global(self, current: Picture) -> Picture:
        sql = self.statements.select_next_time_skip_in_global(current.minute, current.time)
        return self._execute_query(sql)

    def get_previous_time_skip_in_global(self, current: Picture) -> Picture:
        pass
    # Altitude
    # --------------------------------------------------------------------------

    # Altitude in Hikes
    def get_next_altitude_in_hikes(self, current: Picture, offset: int) -> Picture:
        sql = self.statements.select_next_altitude_in_hikes(current.altrank_global_h, offset)
        return self._execute_query(sql)

    def get_previous_altitude_in_hikes(self, current: Picture, offset: int) -> Picture:
        sql = self.statements.select_previous_altitude_in_hikes(current.altrank_global_h, offset)
        return self._execute_query(sql)

    # Altitude in Global
    def get_next_altitude_in_global(self, current: Picture, offset: int) -> Picture:
        sql = self.statements.select_next_altitude_in_global(current.altrank_global, offset)
        return self._execute_query(sql)

    def get_previous_altitude_in_global(self, current: Picture, offset: int) -> Picture:
        sql = self.statements.select_previous_altitude_in_global(current.altrank_global, offset)
        return self._execute_query(sql)

    # Color
    # --------------------------------------------------------------------------

    # Color in Hikes
    def get_next_color_in_hikes(self, current: Picture, offset: int) -> Picture:
        sql = self.statements.select_next_color_in_hikes(current.colorrank_global_h, offset)
        return self._execute_query(sql)

    def get_previous_color_in_hikes(self, current: Picture, offset: int) -> Picture:
        sql = self.statements.select_previous_color_in_hikes(current.colorrank_global_h, offset)
        return self._execute_query(sql)

    # Color in Global
    def get_next_color_in_global(self, current: Picture, offset: int) -> Picture:
        sql = self.statements.select_next_color_in_global(current.colorrank_global, offset)
        return self._execute_query(sql)

    def get_previous_color_in_global(self, current: Picture, offset: int) -> Picture:
        sql = self.statements.select_previous_color_in_global(current.colorrank_global, offset)
        return self._execute_query(sql)

    # TODO REMOVE - go through and remove all the old methods that aren't needed anymore
    # likely it will be most of them
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

    # Helper methods
    def _build_hike_from_row(self, row: list) -> Hike:
        hike = Hike(hike_id=row[0], avg_altitude=row[1],
                    avg_brightness=row[2], avg_hue=row[3], avg_hue_lumosity=row[4],
                    start_time=row[5], end_time=row[6], pictures_num=row[7], path=row[8])

        return hike

    # Helper method for returning expected number
    # If nothing is returned from db, return 0
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
    # def get_next_picture(self, current_picture: Picture, mode: int, is_across_hikes: bool) -> Picture:
    #     if is_across_hikes:     # Across all hikes: rotary encoder is pressed
    #         if mode == 0:       # Time
    #             return self.next_time_picture_across_hikes(current_picture)
    #         elif mode == 1:     # Altitude
    #             return self.next_altitude_picture_across_hikes(current_picture)
    #         elif mode == 2:     # Color
    #             # TODO return self.next_color_picture_across_hikes(current_picture)
    #             print('Color across hikes not implemented yet')
    #             return current_picture
    #     else:                   # In current hike: rotary encoder not pressed
    #         if mode == 0:       # Time
    #             return self.next_time_picture_in_hike(current_picture)
    #         elif mode == 1:     # Altitude
    #             return self.next_altitude_picture_in_hike(current_picture)
    #         elif mode == 2:     # Color
    #             # TODO return self.next_altitude_picture_in_hike(current_picture)
    #             print('Color in hikes is not implemented yet')
    #             return current_picture

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

    def _create_new_hike(self, time):
        cursor = self.connection.cursor()
        cursor.execute(self.statements.insert_new_hike(time))
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
    def will_create_new_hike(self, NEW_HIKE_TIME, DIRECTORY, time) -> bool:
        time_since_last_hike = self._get_time_since_last_hike()

        # Create a new hike; -1 indicates this is the first hike in db
        if time_since_last_hike > NEW_HIKE_TIME or time_since_last_hike == -1:
            print('Creating new hike:')
            self._create_new_hike(time)

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

    def create_new_picture(self, hike_id: int, photo_index: int, time: float):
        cursor = self.connection.cursor()
        cursor.execute(self.statements.insert_new_picture(time, hike_id, photo_index))
        self.connection.commit()

    def _set_hike_path(self, hike_id: int, hike_path: str):
        cursor = self.connection.cursor()
        cursor.execute(self.statements.update_hike_path(hike_path, hike_id))
        self.connection.commit()

    def set_image_path(self, cam_num: int, path: str, hike_id: int, photo_index: int):
        cursor = self.connection.cursor()
        cursor.execute(self.statements.update_picture_image_path(cam_num, path, hike_id, photo_index))
        self.connection.commit()

    def set_picture_altitude(self, altitude: float, hike_id: int, photo_index: int):
        cursor = self.connection.cursor()
        cursor.execute(self.statements.update_picture_altitude(altitude, hike_id, photo_index))
        self.connection.commit()

    def set_hike_endtime_picture_count(self, time: float, count: int, hike_id: int):
        cursor = self.connection.cursor()
        cursor.execute(self.statements.update_hike_endtime_picture_count(time, count, hike_id))
        self.connection.commit()

    def set_altitude_for_rowid(self, alt: float, id: int):
        cursor = self.connection.cursor()
        cursor.execute(self.statements.update_picture_altitude_for_id(alt, id))
        self.connection.commit()

    # Transfer
    # --------------------------------------------------------------------------
    def delete_picture_and_hikes_tables(self):
        cursor = self.connection.cursor()

        cursor.execute(self.statements.delete_pictures())
        self.connection.commit()

        cursor.execute(self.statements.delete_hikes())
        self.connection.commit()

    def upsert_hike(self,
                        hike_id: int,
                        avg_altitude: float,
                        avg_color_camera1_hsv: str,
                        avg_color_camera2_hsv: str,
                        avg_color_camera3_hsv: str,
                        start_time: float,
                        start_year: int,
                        start_month: int,
                        start_day: int,
                        start_minute: int,
                        start_dayofweek: int,
                        end_time: float,
                        end_year: int,
                        end_month: int,
                        end_day: int,
                        end_minute: int,
                        end_dayofweek: int,
                        pictures: int,
                        path: str):
        cursor = self.connection.cursor()
        cursor.execute(self.statements.upsert_hike_row(hike_id, avg_altitude,
                                                        avg_color_camera1_hsv, avg_color_camera2_hsv, avg_color_camera3_hsv,
                                                        start_time, start_year, start_month, start_day, start_minute, start_dayofweek,
                                                        end_time, end_year, end_month, end_day, end_minute, end_dayofweek,
                                                        pictures, path))
        self.connection.commit()

    def upsert_picture(self,
                            time: float,
                            year: int,
                            month: int,
                            day: int,
                            minute: int,
                            dayofweek: int,
                            hike: int,
                            index_in_hike: int,
                            altitude: float,
                            camera1: str,
                            camera1_color_hsv: str,
                            camera1_color_rgb: str,
                            camera2: str,
                            camera2_color_hsv: str,
                            camera2_color_rgb: str,
                            camera3: str,
                            camera3_color_hsv: str,
                            camera3_color_rgb: str,
                            camera_landscape: str):
        cursor = self.connection.cursor()
        cursor.execute(self.statements.upsert_picture_row(time, year, month, day, minute, dayofweek,
                                                            hike, index_in_hike, altitude,
                                                            camera1, camera1_color_hsv, camera1_color_rgb,
                                                            camera2, camera2_color_hsv, camera2_color_rgb,
                                                            camera3, camera3_color_hsv, camera3_color_rgb,
                                                            camera_landscape))
        self.connection.commit()

    def get_size_of_hike(self, hike_id: int) -> int:
        cursor = self.connection.cursor()
        cursor.execute(self.statements.get_size_of_hike(hike_id=hike_id))
        row = cursor.fetchone()
        if (row is None):
            return None
        else:
            return row[0]

    def get_hike_average_color(self, hike_id: int, camNum: int = 0):
        cursor = self.connection.cursor()
        cursor.execute(self.statements.get_hike_average_color(hike_id=hike_id, camNum=camNum))
        res = cursor.fetchone()

        if (res is None or res[0] is None):
            return None

        tmp = res[0].strip("()").split(',')
        ret = []

        if (tmp is None):
            return None
        else:
            for i in tmp:
            	ret.append(float(i))
            return ret

    # returns an array that represents the dominant color in HSV value: [float, float, float]
    def get_picture_dominant_color(self, time: float, camNum: int = 0):
        cursor = self.connection.cursor()
        cursor.execute(self.statements.get_dominant_color_for_picture_of_given_timestamp(time=time, camNum=camNum))
        res = cursor.fetchone()

        if (res is None or res[0] is None):
            return None

        ret = []

        hsv = res[0].strip("()").split(',')
        for i in hsv:
            ret.append(float(i))

        rgb = res[0].strip("()").split(',')
        for i in rgb:
            ret.append(float(i))

        return ret

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
