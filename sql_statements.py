# Holds all SQL statements for the program


class SQLStatements:

    # Select by ID and index
    def select_by_ids_picture(self, hike_id: int, index_in_hike: int) -> str:
        statement = 'SELECT * FROM pictures WHERE hike={id} AND \
            index_in_hike={index}'.format(id=hike_id, index=index_in_hike)
        return statement

    # ********************     Time     ********************

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

    # ********************     Altitude     ********************

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
