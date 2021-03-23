# Holds all SQL statements for the program
# The only class that should ever interact with is the SQL_Controller


class SQLStatements:

    # Select by ID and index
    def select_picture_by_hike_ids(self, hike_id: int, index_in_hike: int) -> str:
        statement = 'SELECT * FROM pictures WHERE hike={id} AND \
            index_in_hike={index}'.format(id=hike_id, index=index_in_hike)
        return statement

    def select_picture_by_id(self, picture_id: int) -> str:
        statement = 'SELECT * FROM pictures WHERE picture_id={id}'.format(id=picture_id)
        return statement

    # --------------------------------------------------------------------------
    # Projector -- New Functions 2020 / 2021
    # --------------------------------------------------------------------------

    # Time
    # --------------------------------------------------------------------------

    # Time in Hikes
    def select_next_time_in_hikes(self, time: int, offset: int) -> str:
        statement = 'SELECT * FROM pictures WHERE picture_id = ( \
            SELECT \
        CASE WHEN (SELECT count(*) FROM pictures WHERE time > {t}) >= ({off}%(SELECT count(*) FROM pictures)) \
            THEN (SELECT picture_id FROM pictures WHERE time >= {t} ORDER BY time ASC LIMIT 1 OFFSET ({off}%(SELECT count(*) FROM pictures))) \
            ELSE (SELECT picture_id FROM pictures ORDER BY time ASC LIMIT 1 OFFSET ({off}%(SELECT count(*) FROM pictures) - (SELECT count(*) FROM pictures WHERE time > {t}) - 1)) \
        END);'.format(t=time, off=offset)
        return statement

    def select_previous_time_in_hikes(self, time: int, offset: int) -> str:
        statement = 'SELECT * FROM pictures WHERE picture_id = ( \
            SELECT \
        CASE WHEN (SELECT count(*) FROM pictures WHERE time < {t}) >= ({off}%(SELECT count(*) FROM pictures)) \
            THEN (SELECT picture_id FROM pictures WHERE time <= {t} ORDER BY time DESC LIMIT 1 OFFSET ({off}%(SELECT count(*) FROM pictures))) \
            ELSE (SELECT picture_id FROM pictures ORDER BY time DESC LIMIT 1 OFFSET ({off}%(SELECT count(*) FROM pictures) - (SELECT count(*) FROM pictures WHERE time < {t}) - 1)) \
        END);'.format(t=time, off=offset)
        return statement

    # Time in Global
    def select_next_time_in_global(self, minute: int, time: int, offset: int) -> str:
        statement = 'SELECT * FROM pictures WHERE picture_id = ( \
        SELECT CASE WHEN ((SELECT count(*) FROM pictures WHERE minute={m} AND time >{t}) >= ({off}%(SELECT count(*) FROM pictures))) \
            THEN (SELECT picture_id FROM pictures WHERE minute={m} AND time>={t} ORDER BY minute ASC, time ASC LIMIT 1 OFFSET {off}%(SELECT count(*) FROM pictures)) \
            ELSE CASE WHEN ((SELECT count(*) FROM pictures WHERE minute>{m}) > (({off}-(SELECT count(*) FROM pictures WHERE minute={m} AND time >={t}))%(SELECT count(*) FROM pictures))) \
                THEN (SELECT picture_id FROM pictures WHERE minute>{m} ORDER BY minute ASC, time ASC LIMIT 1 OFFSET (({off}-(SELECT count(*) FROM pictures WHERE minute={m} AND time >={t}))%(SELECT count(*) FROM pictures))) \
                ELSE (SELECT picture_id FROM pictures ORDER BY minute ASC, time ASC LIMIT 1 OFFSET (({off}-(SELECT count(*) FROM pictures WHERE minute={m} AND time>={t})-(SELECT count(*) FROM pictures WHERE minute>{m}))%(SELECT count(*) FROM pictures))) \
                END \
            END);'.format(m=minute, t=time, off=offset)
        return statement

    def select_previous_time_in_global(self, minute: int, time: int, offset: int) -> str:
        statement = 'SELECT * FROM pictures WHERE picture_id = ( \
        SELECT CASE WHEN ((SELECT count(*) FROM pictures WHERE minute={m} AND time<{t}) >= ({off}%(SELECT count(*) FROM pictures))) \
            THEN (SELECT picture_id FROM pictures WHERE minute={m} AND time<={t} ORDER BY minute DESC, time DESC LIMIT 1 OFFSET {off}%(SELECT count(*) FROM pictures)) \
            ELSE CASE WHEN ((SELECT count(*) FROM pictures WHERE minute<{m}) > (({off}-(SELECT count(*) FROM pictures WHERE minute={m} AND time <={t}))%(SELECT count(*) FROM pictures))) \
                THEN (SELECT picture_id FROM pictures WHERE minute<{m} ORDER BY minute DESC, time DESC LIMIT 1 OFFSET (({off}-(SELECT count(*) FROM pictures WHERE minute={m} AND time <={t}))%(SELECT count(*) FROM pictures))) \
                ELSE (SELECT picture_id FROM pictures ORDER BY minute DESC, time DESC LIMIT 1 OFFSET (({off}-(SELECT count(*) FROM pictures WHERE minute={m} AND time<={t})-(SELECT count(*) FROM pictures WHERE minute<{m}))%(SELECT count(*) FROM pictures))) \
                END \
            END);'.format(m=minute, t=time, off=offset)
        return statement

    # Time Skip in Hikes
    def select_next_time_skip_in_hikes(self, hike: int, time: int) -> str:
        skip_ahead = 1  # private variable in case we want to change how big the skip is
        statement = 'SELECT * FROM pictures WHERE picture_id = ( \
            SELECT CASE WHEN (SELECT count(*) FROM pictures WHERE hike>{h}) \
                THEN (									  /* hike + skip */ \
                    SELECT picture_id FROM pictures WHERE hike>=({h}+{s}) ORDER BY time ASC LIMIT 1 OFFSET ( \
                        SELECT CAST(( \
                            (CAST((SELECT count(*) FROM pictures WHERE hike={h} AND time<={t}) AS REAL) \
                            /(SELECT count(*) FROM pictures WHERE hike={h})) \
                            * (SELECT count(*) FROM pictures WHERE hike=(SELECT hike FROM pictures WHERE hike>={h}+{s} LIMIT 1)) \
                        ) AS INT) - 1 \
                    ) \
                ) \
                ELSE ( \
                    SELECT picture_id FROM pictures WHERE hike=(SELECT hike FROM pictures WHERE hike>=0 LIMIT 1) ORDER BY time ASC LIMIT 1 OFFSET ( \
                        SELECT CAST(( \
                            (CAST((SELECT count(*) FROM pictures WHERE hike={h} AND time<={t}) AS REAL) \
                            /(SELECT count(*) FROM pictures WHERE hike={h})) \
                            * (SELECT count(*) FROM pictures WHERE hike=(SELECT hike FROM pictures WHERE hike>=0 LIMIT 1)) \
                        ) AS INT) - 1 \
                    ) \
                ) \
            END END);'.format(h=hike, t=time, s=skip_ahead)
        return statement

    def select_previous_time_skip_in_hikes(self, hike: int, time: int) -> str:
        skip_back = 1  # private variable in case we want to change how big the skip is
        statement = 'SELECT * FROM pictures WHERE picture_id = ( \
            SELECT CASE WHEN (SELECT count(*) FROM pictures WHERE hike<{h}) \
                THEN (									  /* hike + skip */ \
                    SELECT picture_id FROM pictures WHERE hike=(SELECT hike FROM pictures WHERE hike<={h}-{s} ORDER BY time DESC LIMIT 1) ORDER BY time ASC LIMIT 1 OFFSET ( \
                        SELECT CAST(( \
                            (CAST((SELECT count(*) FROM pictures WHERE hike={h} AND time<={t}) AS REAL) \
                            /(SELECT count(*) FROM pictures WHERE hike={h})) \
                            * (SELECT count(*) FROM pictures WHERE hike=(SELECT hike FROM pictures WHERE hike<={h}-{s} ORDER BY time DESC LIMIT 1)) \
                        ) AS INT) - 1 \
                    ) \
                ) \
                ELSE ( \
                    SELECT picture_id FROM pictures WHERE hike=(SELECT hike FROM pictures ORDER BY hike DESC LIMIT 1) ORDER BY time ASC LIMIT 1 OFFSET ( \
                        SELECT CAST(( \
                            (CAST((SELECT count(*) FROM pictures WHERE hike={h} AND time<={t}) AS REAL) \
                            /(SELECT count(*) FROM pictures WHERE hike={h})) \
                            * (SELECT count(*) FROM pictures WHERE hike=(SELECT hike FROM pictures ORDER BY hike DESC LIMIT 1)) \
                        ) AS INT) - 1 \
                    ) \
                ) \
            END END);'.format(h=hike, t=time, s=skip_back)
        return statement

    # Time Skip in Global
    def select_next_time_skip_in_global(self, minute: int, time: int) -> str:
        skip_ahead = 15  # private variable in case we want to change how big the skip is
        statement = 'SELECT * FROM pictures WHERE picture_id = ( \
            SELECT CASE WHEN ( \
                (SELECT count(DISTINCT minute) FROM pictures WHERE minute>=({m}+{s})) >= 1) \
                THEN ( /*there is a next minute below in table*/ \
                    SELECT picture_id FROM pictures WHERE minute>=({m}+{s}) ORDER BY minute ASC, time ASC LIMIT 1 OFFSET ( \
                    SELECT CAST(( \
                        (CAST((SELECT count(*) FROM pictures WHERE minute={m} AND time<={t}) AS REAL) /*get # it is in minute (<= for next) casted as float*/ \
                        /(SELECT count(*) FROM pictures WHERE minute={m})) /*divide by the total for this minute*/ \
                        * (SELECT count(*) FROM pictures WHERE minute=(SELECT minute FROM pictures WHERE minute>={m}+{s} ORDER BY minute ASC, time ASC LIMIT 1)) /*multiple by count for next available minute at least 15min ahead*/ \
                    ) AS INT) ) - 1 /*cast back to integer. move back 1 (first value of minute has offset of 0)*/ \
                ) \
                ELSE ( /*wrap back around to top of table*/ \
                    SELECT picture_id FROM pictures WHERE minute>=( \
                            /* first minute value */						 /* skip value */	 /* how many minutes from top of table */ \
                        (SELECT minute FROM pictures ORDER BY minute ASC LIMIT 1)+ {s} - (SELECT count(DISTINCT minute) FROM pictures WHERE minute>=({m})) \
                    ) ORDER BY minute ASC, time ASC LIMIT 1 OFFSET ( \
                    SELECT CAST(( \
                        (CAST((SELECT count(*) FROM pictures WHERE minute={m} AND time<={t}) AS REAL) \
                        /(SELECT count(*) FROM pictures WHERE minute={m})) \
                        * (SELECT count(*) FROM pictures WHERE minute=(SELECT minute FROM pictures WHERE minute>=( \
                            (SELECT minute FROM pictures ORDER BY minute ASC LIMIT 1)+{s} - (SELECT count(DISTINCT minute) FROM pictures WHERE minute>={m}) /* same from 6 lines above */ \
                        ) ORDER BY minute ASC, time ASC LIMIT 1)) \
                    ) AS INT) ) - 1 \
                ) \
                END \
            END);'.format(m=minute, t=time, s=skip_ahead)
        return statement


    # Altitude
    # --------------------------------------------------------------------------

    # Altitude in Hikes
    def select_next_altitude_in_hikes(self, altrank_global_h: float, offset: int) -> str:
        statement = 'SELECT * FROM pictures WHERE picture_id = ( \
        SELECT CASE WHEN (SELECT count(*) FROM pictures WHERE altrank_global_h > {a}) >= ({o}%(SELECT count(*) FROM pictures)) \
            THEN (SELECT picture_id FROM pictures WHERE altrank_global_h >= {a} ORDER BY altrank_global_h ASC LIMIT 1 OFFSET ({o}%(SELECT count(*) FROM pictures))) \
            ELSE (SELECT picture_id FROM pictures ORDER BY altrank_global_h ASC LIMIT 1 OFFSET ({o}%(SELECT count(*) FROM pictures) - (SELECT count(*) FROM pictures WHERE altrank_global_h > {a}) - 1)) \
        END);'.format(a=altrank_global_h, o=offset)
        return statement

    def select_previous_altitude_in_hikes(self, altrank_global_h: float, offset: int) -> str:
        statement = 'SELECT * FROM pictures WHERE picture_id = ( \
        SELECT CASE WHEN (SELECT count(*) FROM pictures WHERE altrank_global_h < {a}) >= ({o}%(SELECT count(*) FROM pictures)) \
            THEN (SELECT picture_id FROM pictures WHERE altrank_global_h <= {a} ORDER BY altrank_global_h DESC LIMIT 1 OFFSET ({o}%(SELECT count(*) FROM pictures))) \
            ELSE (SELECT picture_id FROM pictures ORDER BY altrank_global_h DESC LIMIT 1 OFFSET ({o}%(SELECT count(*) FROM pictures) - (SELECT count(*) FROM pictures WHERE altrank_global_h < {a}) - 1)) \
        END);'.format(a=altrank_global_h, o=offset)
        return statement

    # Altitude in Global
    def select_next_altitude_in_global(self, altrank_global: float, offset: int) -> str:
        statement = 'SELECT * FROM pictures WHERE picture_id = ( \
        SELECT CASE WHEN (SELECT count(*) FROM pictures WHERE altrank_global > {a}) >= ({o}%(SELECT count(*) FROM pictures)) \
            THEN (SELECT picture_id FROM pictures WHERE altrank_global >= {a} ORDER BY altrank_global ASC LIMIT 1 OFFSET ({o}%(SELECT count(*) FROM pictures))) \
            ELSE (SELECT picture_id FROM pictures ORDER BY altrank_global ASC LIMIT 1 OFFSET ({o}%(SELECT count(*) FROM pictures) - (SELECT count(*) FROM pictures WHERE altrank_global > {a}) - 1)) \
        END);'.format(a=altrank_global, o=offset)
        return statement

    def select_previous_altitude_in_global(self, altrank_global: float, offset: int) -> str:
        statement = 'SELECT * FROM pictures WHERE picture_id = ( \
        SELECT CASE WHEN (SELECT count(*) FROM pictures WHERE altrank_global < {a}) >= ({o}%(SELECT count(*) FROM pictures)) \
            THEN (SELECT picture_id FROM pictures WHERE altrank_global <= {a} ORDER BY altrank_global DESC LIMIT 1 OFFSET ({o}%(SELECT count(*) FROM pictures))) \
            ELSE (SELECT picture_id FROM pictures ORDER BY altrank_global DESC LIMIT 1 OFFSET ({o}%(SELECT count(*) FROM pictures) - (SELECT count(*) FROM pictures WHERE altrank_global < {a}) - 1)) \
        END);'.format(a=altrank_global, o=offset)
        return statement

    # Altitude Skip in Hikes

    # Altitude Skip in Global

    # Color
    # --------------------------------------------------------------------------

    # Color in Hikes
    def select_next_color_in_hikes(self, colorrank_global_h: float, offset: int) -> str:
        statement = 'SELECT * FROM pictures WHERE picture_id = ( \
        SELECT CASE WHEN (SELECT count(*) FROM pictures WHERE color_rank_global_h > {c}) >= ({o}%(SELECT count(*) FROM pictures)) \
            THEN (SELECT picture_id FROM pictures WHERE color_rank_global_h >= {c} ORDER BY color_rank_global_h ASC LIMIT 1 OFFSET ({o}%(SELECT count(*) FROM pictures))) \
            ELSE (SELECT picture_id FROM pictures ORDER BY color_rank_global_h ASC LIMIT 1 OFFSET ({o}%(SELECT count(*) FROM pictures) - (SELECT count(*) FROM pictures WHERE color_rank_global_h > {c}) - 1)) \
        END);'.format(c=colorrank_global_h, o=offset)
        return statement

    def select_previous_color_in_hikes(self, colorrank_global_h: float, offset: int) -> str:
        statement = 'SELECT * FROM pictures WHERE picture_id = ( \
        SELECT CASE WHEN (SELECT count(*) FROM pictures WHERE color_rank_global_h < {c}) >= ({o}%(SELECT count(*) FROM pictures)) \
            THEN (SELECT picture_id FROM pictures WHERE color_rank_global_h <= {c} ORDER BY color_rank_global_h DESC LIMIT 1 OFFSET ({o}%(SELECT count(*) FROM pictures))) \
            ELSE (SELECT picture_id FROM pictures ORDER BY color_rank_global_h DESC LIMIT 1 OFFSET ({o}%(SELECT count(*) FROM pictures) - (SELECT count(*) FROM pictures WHERE color_rank_global_h < {c}) - 1)) \
        END);'.format(c=colorrank_global_h, o=offset)
        return statement

    # Color in Global

    # Color Skip in Hikes

    # Color Skip in Global

    # --------------------------------------------------------------------------
    # Old Projector Functions
    # --------------------------------------------------------------------------
    # ******************************     Time     ******************************

    # Time - first & last across hikes
    def select_by_time_first_picture(self) -> str:
        statement = 'SELECT * FROM pictures ORDER BY time ASC LIMIT 1'
        return statement

    def select_by_time_last_picture(self) -> str:
        statement = 'SELECT * FROM pictures ORDER BY time DESC LIMIT 1'
        return statement

    # Time - next & previous across hikes
    def select_by_time_next_picture(self, time: float) -> str:
        statement = 'SELECT * FROM pictures WHERE time>{t} \
            ORDER BY time ASC LIMIT 1'.format(t=time)
        return statement

    def select_by_time_previous_picture(self, time: float) -> str:
        statement = 'SELECT * FROM pictures WHERE time<{t} \
            ORDER BY time DESC LIMIT 1'.format(t=time)
        return statement

    # Time - first & last in a hike
    def select_by_time_first_picture_in_hike(self, hike_id: float) -> str:
        statement = 'SELECT * FROM pictures WHERE hike={id} \
            ORDER BY time ASC LIMIT 1'.format(id=hike_id)
        return statement

    def select_by_time_last_picture_in_hike(self, hike_id: float) -> str:
        statement = 'SELECT * FROM pictures WHERE hike={id} \
            ORDER BY time DESC LIMIT 1'.format(id=hike_id)
        return statement

    # Time - next & previous in a hike
    def select_by_time_next_picture_in_hike(self, hike_id: float, time: float) -> str:
        statement = 'SELECT * FROM pictures WHERE hike={id} AND time>{t} \
            ORDER BY time ASC LIMIT 1'.format(id=hike_id, t=time)
        return statement

    def select_by_time_previous_picture_in_hike(self, hike_id: float, time: float) -> str:
        statement = 'SELECT * FROM pictures WHERE hike={id} AND time<{t} \
            ORDER BY time DESC LIMIT 1'.format(id=hike_id, t=time)
        return statement

    # ****************************     Altitude     ****************************

    # Altitude - greatest & least across hikes
    def select_by_altitude_greatest_picture(self) -> str:
        statement = 'SELECT * FROM pictures ORDER BY altitude DESC LIMIT 1'
        return statement

    def select_by_altitude_least_picture(self) -> str:
        statement = 'SELECT * FROM pictures ORDER BY altitude ASC LIMIT 1'
        return statement

    # Altitude - count of same altitude across hikes
    def find_size_by_altitude_greater_time(self, altitude: float, time: float) -> str:
        statement = 'SELECT count(*) FROM pictures WHERE altitude={alt} \
            AND time>{t}'.format(alt=altitude, t=time)
        return statement

    def find_size_by_altitude_less_time(self, altitude: float, time: float) -> str:
        statement = 'SELECT count(*) FROM pictures WHERE altitude={alt} \
            AND time<{t}'.format(alt=altitude, t=time)
        return statement

    # Altitude - next across hikes
    def select_by_greater_altitude_next_picture(self, altitude: float) -> str:
        statement = 'SELECT * FROM pictures WHERE altitude>{alt} \
            ORDER BY altitude ASC, time ASC LIMIT 1'.format(alt=altitude)
        return statement

    def select_by_equal_altitude_next_picture(self, altitude: float, time: float) -> str:
        statement = 'SELECT * FROM pictures WHERE altitude={alt} AND \
            time>{t} ORDER BY altitude ASC, time ASC LIMIT 1'.format(alt=altitude, t=time)
        return statement

    # Altitude - previous across hikes
    def select_by_less_altitude_previous_picture(self, altitude: float) -> str:
        statement = 'SELECT * FROM pictures WHERE altitude<{alt} \
            ORDER BY altitude DESC, time DESC LIMIT 1'.format(alt=altitude)
        return statement

    def select_by_equal_altitude_previous_picture(self, altitude: float, time: float) -> str:
        statement = 'SELECT * FROM pictures WHERE altitude={alt} AND \
            time<{t} ORDER BY altitude DESC, time DESC LIMIT 1'.format(alt=altitude, t=time)
        return statement

    # Altitude - greatest and least in a hike
    def select_by_altitude_greatest_picture_in_hike(self, hike_id: float) -> str:
        statement = 'SELECT * FROM pictures WHERE hike={id} \
            ORDER BY altitude DESC LIMIT 1'.format(id=hike_id)
        return statement

    def select_by_altitude_least_picture_in_hike(self, hike_id: float) -> str:
        statement = 'SELECT * FROM pictures WHERE hike={id} \
            ORDER BY altitude ASC LIMIT 1'.format(id=hike_id)
        return statement

    # Altitude - count of same altitude in a hike
    def find_size_by_altitude_greater_time_in_hike(self, hike_id: float,
                                                   altitude: float, time: float) -> str:
        statement = 'SELECT count(*) FROM pictures WHERE hike={id} AND altitude={alt} \
            AND time>{t}'.format(id=hike_id, alt=altitude, t=time)
        return statement

    def find_size_by_altitude_less_time_in_hike(self, hike_id: float,
                                                altitude: float, time: float) -> str:
        statement = 'SELECT count(*) FROM pictures WHERE hike={id} AND altitude={alt} \
            AND time<{t}'.format(id=hike_id, alt=altitude, t=time)
        return statement

    # Altitdue - next in a hike
    def select_by_greater_altitude_next_picture_in_hike(self, hike_id: float,
                                                        altitude: float) -> str:
        statement = 'SELECT * FROM pictures WHERE hike={id} AND altitude>{alt} \
            ORDER BY altitude ASC, time ASC LIMIT 1'.format(id=hike_id, alt=altitude)
        return statement

    def select_by_equal_altitude_next_picture_in_hike(self, hike_id: float,
                                                      altitude: float, time: float) -> str:
        statement = 'SELECT * FROM pictures WHERE hike={id} AND altitude={alt} AND \
            time>{t} ORDER BY altitude ASC, time ASC LIMIT 1'.format(id=hike_id, alt=altitude, t=time)
        return statement

    # Altitdue - previous in a hike
    def select_by_less_altitude_previous_picture_in_hike(self, hike_id: float,
                                                         altitude: float) -> str:
        statement = 'SELECT * FROM pictures WHERE hike={id} AND altitude<{alt} \
            ORDER BY altitude DESC, time DESC LIMIT 1'.format(id=hike_id, alt=altitude)
        return statement

    def select_by_equal_altitude_previous_picture_in_hike(self, hike_id: float,
                                                          altitude: float, time: float) -> str:
        statement = 'SELECT * FROM pictures WHERE hike={id} AND altitude={alt} AND \
            time<{t} ORDER BY altitude DESC, time DESC LIMIT 1'.format(id=hike_id, alt=altitude, t=time)
        return statement

    # Color
    # def select_by_color_next_picture() -> str:

    # def select_by_color_previous_picture() -> str:

    # Hike
    def select_size_of_hike(self, hike_id: float) -> str:
        statement = 'SELECT pictures FROM hikes WHERE hike_id={id}'.format(id=hike_id)
        return statement

    def select_hike_by_id(self, hike_id: float) -> str:
        statement = 'SELECT * FROM hikes WHERE hike_id={id}'.format(id=hike_id)
        return statement

    # --------------------------------------------------------------------------
    # Camera
    # --------------------------------------------------------------------------
    def select_hike_count(self) -> str:
        statement = 'SELECT count(*) FROM hikes'
        return statement

    def select_last_hike_id(self) -> str:
        statement = 'SELECT hike_id FROM hikes ORDER BY hike_id DESC LIMIT 1'
        return statement

    def select_last_hike_end_time(self) -> str:
        statement = 'SELECT end_time FROM hikes ORDER BY end_time DESC LIMIT 1'
        return statement

    def select_last_photo_index_of_hike(self, hike_id: int) -> str:
        statement = 'SELECT index_in_hike FROM pictures WHERE hike={n} \
            ORDER BY index_in_hike DESC LIMIT 1'.format(n=hike_id)
        return statement

    def select_last_altitude_recorded(self) -> str:
        statement = 'SELECT altitude FROM pictures ORDER BY ROWID DESC LIMIT 1'
        return statement

    def select_last_row_id(self) -> str:
        statement = 'SELECT ROWID FROM pictures ORDER BY ROWID DESC LIMIT 1'
        return statement

    def insert_new_hike(self, time: float) -> str:
        statement = 'INSERT INTO hikes(start_time, end_time, pictures) VALUES({t}, {t}, 0)'.format(t=time)
        return statement

    def insert_new_picture(self, time: float, hike_id: int, photo_index: int) -> str:
        statement = 'INSERT INTO pictures(time, hike, index_in_hike) VALUES \
            ({t}, {h}, {p})'.format(t=time, h=hike_id, p=photo_index)
        return statement

    def update_picture_image_path(self, cam_num: int, path: str, hike_id: int, photo_index: int) -> str:
        # Only difference between statements is cameraX=
        if cam_num == 1:
            statement = 'UPDATE pictures SET camera1="{p}", updated_date_time=datetime() \
                WHERE hike={h} AND index_in_hike={i} \
                    '.format(p=path, h=hike_id, i=photo_index)
        elif cam_num == 2:
            statement = 'UPDATE pictures SET camera2="{p}", updated_date_time=datetime() \
                WHERE hike={h} AND index_in_hike={i} \
                    '.format(p=path, h=hike_id, i=photo_index)
        elif cam_num == 3:
            statement = 'UPDATE pictures SET camera3="{p}", updated_date_time=datetime() \
                WHERE hike={h} AND index_in_hike={i} \
                    '.format(p=path, h=hike_id, i=photo_index)
        else:
            raise Exception('cam_num should be 1, 2, or 3. The value was: {n}'.format(n=cam_num))

        return statement

    def update_picture_altitude(self, altitude: float, hike_id: int, photo_index: int) -> str:
        statement = 'UPDATE pictures SET altitude={a}, updated_date_time=datetime() \
            WHERE hike={h} AND index_in_hike={p}'.format(a=altitude, h=hike_id, p=photo_index)
        print(statement)
        return statement

    def update_picture_altitude_for_id(self, altitude: float, rowid: int) -> str:
        statement = 'UPDATE  pictures SET altitude={a}, updated_date_time=datetime() \
            WHERE ROWID={r}'.format(a=altitude, r=rowid)
        return statement

    def update_hike_path(self, path: str, hike_id: int) -> str:
        statement = 'UPDATE hikes SET path="{p}", updated_date_time=datetime() \
            WHERE hike_id={h}'.format(p=path, h=hike_id)
        return statement

    def update_hike_endtime_picture_count(self, time: float, count: int, hike_id: int) -> str:
        statement = 'UPDATE hikes SET end_time={t}, pictures={c}, updated_date_time=datetime() WHERE hike_id={h} \
            '.format(t=time, c=count, h=hike_id)
        return statement

    # Transfer
    # --------------------------------------------------------------------------
    def select_valid_photos_in_given_hike(self, hike_id: int) -> int:
        statement = 'SELECT * FROM pictures WHERE hike == {h} AND altitude < 10000 AND altitude >= 0 AND \
            camera1 IS NOT NULL AND camera2 IS NOT NULL AND camera3 IS NOT NULL'.format(h=hike_id)
        return statement

    # def upsert_picture_row(self, time: float, hike: int, index_in_hike: int, altitude: float, hue: float, saturation: float, value: float, red: float, green: float, blue: float, camera1: str, camera2: str, camera3: str, camera_landscape: str) -> int:
    #     statement = 'INSERT OR REPLACE INTO pictures \
    #         (time, hike, index_in_hike, altitude, hue, saturation, value, red, green, blue, camera1, camera2, camera3, camera_landscape) \
    #         VALUES ({}, {}, {}, {}, {}, {}, {}, {}, {}, {}, "{}", "{}", "{}", "{}")\
    #         '.format(time, hike, index_in_hike, altitude, hue, saturation, value, red, green, blue, camera1, camera2, camera3, camera_landscape)
    #     return statement

    def upsert_picture_row(self,
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
                            camera_landscape: str) -> int:
        statement = 'INSERT OR REPLACE INTO pictures \
            (time, \
                year, month, day, minute, dayofweek, \
                hike, index_in_hike, altitude, \
                camera1, camera1_color_hsv, camera1_color_rgb, \
                camera2, camera2_color_hsv, camera2_color_rgb, \
                camera3, camera3_color_hsv, camera3_color_rgb, camera_landscape) \
            VALUES ({}, \
                    {}, {}, {}, {}, {}, \
                    {}, {}, {}, \
                    "{}", "{}", "{}", \
                    "{}", "{}", "{}", \
                    "{}", "{}", "{}", "{}")\
            '.format(time,
                        year, month, day, minute, dayofweek,
                        hike, index_in_hike, altitude,
                        camera1, camera1_color_hsv, camera1_color_rgb,
                        camera2, camera2_color_hsv, camera2_color_rgb,
                        camera3, camera3_color_hsv, camera3_color_rgb, camera_landscape)
        return statement

    # def upsert_hike_row(self, hike_id: int, avg_altitude: float, avg_hue: float, avg_saturation: float, avg_value: float, start_time: float, end_time: float, pictures: int, path: str) -> str:
    #     statement = 'INSERT OR REPLACE INTO hikes \
    #         (hike_id, avg_altitude, avg_hue, avg_saturation, avg_value, start_time, end_time, pictures, path) \
    #         VALUES ({}, {}, {}, {}, {}, {}, {}, {}, "{}")\
    #         '.format(hike_id, avg_altitude, avg_hue, avg_saturation, avg_value, start_time, end_time, pictures, path)
    #     return statement

    def upsert_hike_row(self,
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
                        path: str) -> str:
        statement = 'INSERT OR REPLACE INTO hikes \
            (hike_id, avg_altitude, \
                avg_color_camera1_hsv, avg_color_camera2_hsv, avg_color_camera3_hsv, \
                start_time, start_year, start_month, start_day, start_minute, start_dayofweek, \
                end_time, end_year, end_month, end_day, end_minute, end_dayofweek, \
                pictures, path) \
            VALUES ({}, {}, \
                    "{}", "{}", "{}", \
                    {}, {}, {}, {}, {}, {}, \
                    {}, {}, {}, {}, {}, {}, \
                    {}, "{}")\
            '.format(hike_id, avg_altitude,
                        avg_color_camera1_hsv, avg_color_camera2_hsv, avg_color_camera3_hsv,
                        start_time, start_year, start_month, start_day, start_minute, start_dayofweek,
                        end_time, end_year, end_month, end_day, end_minute, end_dayofweek,
                        pictures, path)
        return statement

    # def get_hike_average_color(self, hike_id: int):
    #     statement = 'SELECT avg_hue, avg_saturation, avg_value FROM hikes WHERE hike_id == {}'.format(hike_id)
    #     return statement

    def get_hike_average_color(self, hike_id: int, camNum : int = 0):
        statement = ""

        # for default color, return cam2's color (the middle one)
        if (camNum == 0):
            statement = 'SELECT avg_color_camera2_hsv FROM hikes WHERE hike_id == {}'.format(hike_id)
        else:
            statement = 'SELECT avg_color_camera{}_hsv FROM hikes WHERE hike_id == {}'.format(camNum, hike_id)

        return statement


    def get_size_of_hike(self, hike_id: int):
        statement = 'SELECT pictures FROM hikes WHERE hike_id == {}'.format(hike_id)
        return statement

    def get_picture_with_timestamp(self, time: float):
        statement = 'SELECT count(*) FROM pictures WHERE time == {}'.format(time)
        return statement

    # def get_dominant_color_for_picture_of_given_timestamp(self, time: float):
    #     statement = 'SELECT hue, saturation, value FROM pictures WHERE time == {}'.format(time)
    #     return statement

    def get_dominant_color_for_picture_of_given_timestamp(self, time: float, camNum : int = 0):
        statement = ""

        # for default color, return cam2's color (the middle one)
        if (camNum == 0):
            statement = 'SELECT camera2_color_hsv, camera2_color_rgb FROM pictures WHERE time == {}'.format(time)
        else:
            statement = 'SELECT camera{}_color_hsv, camera{}_color_rgb FROM pictures WHERE time == {}'.format(camNum, camNum, time)

        return statement

    def delete_pictures(self) -> str:
        statement = 'DELETE FROM pictures'
        return statement

    def delete_hikes(self) -> str:
        statement = 'DELETE FROM hikes'
        return statement

    def get_hike_path(self, hike_id: int) -> str:
        statement = "SELECT path FROM hikes WHERE hike_id == {}".format(hike_id)
        return statement
