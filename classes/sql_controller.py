# Controller to handle the projector UI and camera mainloop talking with the SQLite database

import os
import platform
import sqlite3
import time
from PyQt5.QtGui import *
from classes.capra_data_types import Picture, Hike
from classes.sql_statements import SQLStatements


class SQLController:
    def __init__(self, database: str, directory=None):
        # TODO - be aware that this could potentially be dangerous for thread safety
        self.connection = sqlite3.connect(database, check_same_thread=False)
        self.directory = directory
        self.statements = SQLStatements()

    # --------------------------------------------------------------------------
    # New Functions 2020 / 2021
    # --------------------------------------------------------------------------

    # Private functions
    def _execute_query(self, query) -> Picture:
        '''Returns the first (row) `Picture` from a given query'''
        self.connection.row_factory = sqlite3.Row
        cursor = self.connection.cursor()
        cursor.execute(query)
        all_rows = cursor.fetchall()
        if not all_rows:
            print("ERROR UPON CALLING QUERY:")
            print(query)
            return None
        else:
            # TESTING: used for testing the original 4 database
            picture = self._test_build_picture_from_row(all_rows[0])

            # PRODUCTION: create Picture object from database row
            # picture = self._build_picture_from_row(all_rows[0])

            return picture

    def _execute_query_for_int(self, query) -> int:
        '''Returns an integer from a given query'''
        cursor = self.connection.cursor()
        cursor.execute(query)
        rows = cursor.fetchall()

        if rows is None or len(rows) == 0:
            print(query)
            raise ValueError('No data returned from database from _execute_query_for_int()')
        else:
            value = rows[0][0]

        return int(value)

    def _execute_query_for_float(self, query) -> float:
        '''Returns a float from a given query'''
        cursor = self.connection.cursor()
        cursor.execute(query)
        rows = cursor.fetchall()

        if rows is None or len(rows) == 0:
            print(query)
            raise ValueError('No data returned from database from _execute_query_for_float()')
        else:
            value = rows[0][0]

        return float(value)

    def _execute_query_for_anything(self, query):
        cursor = self.connection.cursor()
        cursor.execute(query)
        rows = cursor.fetchall()

        return rows

    def _test_build_picture_from_row(self, row: list) -> Picture:
        """Builds old (winter 2021 verion) of Picture object from an old `pictures` row
        ::

            :param row: from `pictures` table
            :return: Picture (old winter 2021 version)
        """

        # Finalized Database schema
        picture = Picture(picture_id=row['picture_id'], time=row['time'], year=row['year'], month=row['month'], day=row['day'],
                          minute=row['minute'], dayofweek=row['dayofweek'], hike_id=row['hike'], index_in_hike=row['index_in_hike'], timerank_global='--',
                          altitude=row['altitude'], altrank_hike=row['altrank_hike'], altrank_global=row['altrank_global'], altrank_global_h=row['altrank_global_h'],
                          color_hsv=row['color_hsv'], color_rgb=row['color_rgb'], colorrank_hike=row['color_rank_hike'], colorrank_global=row['color_rank_global'],
                          colorrank_global_h=row['color_rank_global_h'], colors_count=row['colors_count'], colors_rgb=row['colors_rgb'], colors_conf=row['colors_conf'],
                          camera1=row['camera1'], camera2=row['camera2'], camera3=row['camera3'], cameraf=row['camera_landscape'],
                          created=row['created_date_time'], updated=row['updated_date_time'])

        return picture

    def _build_picture_from_row(self, row: list) -> Picture:
        """Build Picture object from `pictures` row
        ::

            :param row: from `pictures` table
            :return: Picture (custom object)
        """

        camera1 = self.directory + row['camera1']
        camera2 = self.directory + row['camera2']
        camera3 = self.directory + row['camera3']
        cameraf = self.directory + row['camera_landscape']

        # Finalized Database schema
        picture = Picture(picture_id=row['picture_id'], time=row['time'], year=row['year'], month=row['month'], day=row['day'],
                          minute=row['minute'], dayofweek=row['dayofweek'], hike_id=row['hike'], index_in_hike=row['index_in_hike'], timerank_global=row['time_rank_global'],
                          altitude=row['altitude'], altrank_hike=row['altrank_hike'], altrank_global=row['altrank_global'], altrank_global_h=row['altrank_global_h'],
                          color_hsv=row['color_hsv'], color_rgb=row['color_rgb'], colorrank_hike=row['color_rank_hike'], colorrank_global=row['color_rank_global'],
                          colorrank_global_h=row['color_rank_global_h'], colors_count=row['colors_count'], colors_rgb=row['colors_rgb'], colors_conf=row['colors_conf'],
                          camera1=camera1, camera2=camera2, camera3=camera3, cameraf=cameraf,
                          created=row['created_date_time'], updated=row['updated_date_time'])

        return picture

    def _build_hike_from_row(self, row: list) -> Hike:
        """Build Hike object from `hikes` row
        ::

            :param row: from `hikes` table
            :return: Hike (custom object)
        """

        hikepath = self.directory + row['path']

        # Finalized Database schema
        hike = Hike(hike_id=row['hike_id'], avg_altitude=row['avg_altitude'], avg_altrank=row['avg_altitude_rank'],
                    start_time=row['start_time'], start_year=row['start_year'], start_month=row['start_month'], start_day=row['start_day'], start_minute=row['start_minute'], start_dayofweek=row['start_dayofweek'],
                    end_time=row['end_time'], end_year=row['end_year'], end_month=row['end_month'], end_day=row['end_day'], end_minute=row['end_minute'], end_dayofweek=row['end_dayofweek'],
                    color_rgb=row['color_rgb'], color_rank=row['color_rank'], num_pictures=row['pictures'], path=hikepath, created=row['created_date_time'], updated=row['updated_date_time'])

        return hike

    # Selecting by ID and index
    # --------------------------------------------------------------------------
    def get_picture_with_id(self, id: int) -> Picture:
        sql = self.statements.select_picture_by_id(id)
        return self._execute_query(sql)

    def get_hike_with_id(self, id: int) -> Hike:
        sql = self.statements.select_hike_by_id(id)
        rows = self._execute_query_for_anything(sql)

        if not rows:
            print("ERROR UPON QUERYING FOR HIKE:")
            print(sql)
            return None
        else:
            # Hike object was created from database row
            hike = self._build_hike_from_row(rows[0])
            return hike

    def get_current_hike(self, current: Picture) -> Hike:
        return self.get_hike_with_id(current.hike_id)

    # TODO - write tests for all of these functions
    # Initializing queries - used to get the initial row from the database
    # --------------------------------------------------------------------------
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

    # Sizes
    # --------------------------------------------------------------------------
    def get_hike_size(self, current: Picture) -> int:
        sql = self.statements.select_hike_size(current.hike_id)
        return self._execute_query_for_int(sql)

    def get_hike_size_with_id(self, hike_id: int) -> int:
        sql = self.statements.select_hike_size(hike_id)
        return self._execute_query_for_int(sql)

    def get_archive_size(self) -> int:
        sql = self.statements.select_archive_size()
        return self._execute_query_for_int(sql)

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
        sql = self.statements.select_previous_time_skip_in_global(current.minute, current.time)
        return self._execute_query(sql)

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

    # Altitude Skip in Hikes
    def get_next_altitude_skip_in_hikes(self, current: Picture) -> Picture:
        sql = self.statements.select_next_altitude_skip_in_hikes(current.hike_id, current.altrank_hike)
        return self._execute_query(sql)

    def get_previous_altitude_skip_in_hikes(self, current: Picture) -> Picture:
        sql = self.statements.select_previous_altitude_skip_in_hikes(current.hike_id, current.altrank_hike)
        return self._execute_query(sql)

    # Altitude Skip in Global
    def get_next_altitude_skip_in_global(self, current: Picture) -> Picture:
        sql = self.statements.select_next_altitude_skip_in_global(current.altrank_global)
        return self._execute_query(sql)

    def get_previous_altitude_skip_in_global(self, current: Picture) -> Picture:
        sql = self.statements.select_previous_altitude_skip_in_global(current.altrank_global)
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

    # Color Skip in Hikes
    def get_next_color_skip_in_hikes(self, current: Picture) -> Picture:
        sql = self.statements.select_next_color_skip_in_hikes(current.hike_id, current.colorrank_hike)
        return self._execute_query(sql)

    def get_previous_color_skip_in_hikes(self, current: Picture) -> Picture:
        sql = self.statements.select_previous_color_skip_in_hikes(current.hike_id, current.colorrank_hike)
        return self._execute_query(sql)

    # Color Skip in Global
    def get_next_color_skip_in_global(self, current: Picture) -> Picture:
        sql = self.statements.select_next_color_skip_in_global(current.colorrank_global)
        return self._execute_query(sql)

    def get_previous_color_skip_in_global(self, current: Picture) -> Picture:
        sql = self.statements.select_previous_color_skip_in_global(current.colorrank_global)
        return self._execute_query(sql)

    # --------------------------------------------------------------------------
    # UI Calls (2021)
    # --------------------------------------------------------------------------
    # Colors
    def ui_get_colors_for_hike_sortby(self, m: str, current: Picture) -> list:
        sql = self.statements.ui_select_colors_for_hike_sortby(m, current.hike_id)

        cursor = self.connection.cursor()
        cursor.execute(sql)
        rows = cursor.fetchall()

        # Error safety check
        if rows is None:
            raise ValueError('No data returned!')
        else:
            colorlist = list()
            for r in rows:
                c = r[0].split(',')
                color = QColor(int(c[0]), int(c[1]), int(c[2]))
                # print(color.red())

                colorlist.append(color)

            return colorlist

    def ui_get_colors_for_archive_sortby(self, m: str) -> list:
        sql = self.statements.ui_select_colors_for_archive_sortby(m)

        cursor = self.connection.cursor()
        cursor.execute(sql)
        rows = cursor.fetchall()

        # Error safety check
        if rows is None:
            raise ValueError('No data returned!')
        else:
            colorlist = list()
            for r in rows:
                c = r[0].split(',')
                color = QColor(int(c[0]), int(c[1]), int(c[2]))
                colorlist.append(color)

            return colorlist

    # Time & Indicator Percentage
    # (also needed for the indicators on the other modes)
    def ui_get_percentage_in_hike_with_mode(self, m: str, current: Picture) -> list:
        sql = self.statements.ui_select_percentage_in_hike_with_mode(m, current.picture_id, current.hike_id)
        return round(self._execute_query_for_float(sql), 4)

    def ui_get_percentage_in_archive_with_mode(self, m: str, current: Picture) -> list:
        sql = self.statements.ui_select_percentage_in_archive_with_mode(m, current.picture_id)
        return round(self._execute_query_for_float(sql), 4)

    # --------------------------------------------------------------------------
    # TODO REMOVE - Eventually go through and remove all the old methods that aren't needed anymore
    # likely it will be most of them
    # --------------------------------------------------------------------------

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


    # NOTE : Everything down is verified as needed, don't touch

    # --------------------------------------------------------------------------
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
