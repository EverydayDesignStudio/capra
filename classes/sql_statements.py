class SQLStatements:
    '''Holds all SQL statements for the program\n
    The only class that should ever interact with this is SQLController'''

    # REMOVE - check for usage, eventually remove
    def select_picture_by_hike_ids(self, hike_id: int, index_in_hike: int) -> str:
        statement = 'SELECT * FROM pictures WHERE hike={id} AND \
            index_in_hike={index}'.format(id=hike_id, index=index_in_hike)
        return statement

    # Selecting by ID and index
    # --------------------------------------------------------------------------
    def select_picture_by_id(self, picture_id: int) -> str:
        statement = 'SELECT * FROM pictures WHERE picture_id={id}'.format(id=picture_id)
        return statement

    def select_hike_by_id(self, hike_id: float) -> str:
        statement = 'SELECT * FROM hikes WHERE hike_id={id}'.format(id=hike_id)
        return statement

    # Select random picture
    # --------------------------------------------------------------------------
    def select_random_picture(self) -> str:
        statement = 'SELECT * FROM pictures ORDER BY RANDOM() LIMIT 1;'
        return statement

    # Initialization Statements - initially written 2019
    # --------------------------------------------------------------------------
    # Time - first & last across hikes
    def select_by_time_first_picture(self) -> str:
        statement = 'SELECT * FROM pictures ORDER BY time ASC LIMIT 1'
        return statement

    def select_by_time_last_picture(self) -> str:
        statement = 'SELECT * FROM pictures ORDER BY time DESC LIMIT 1'
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

    # Altitude - greatest & least across hikes
    def select_by_altitude_greatest_picture(self) -> str:
        statement = 'SELECT * FROM pictures ORDER BY altitude DESC LIMIT 1'
        return statement

    def select_by_altitude_least_picture(self) -> str:
        statement = 'SELECT * FROM pictures ORDER BY altitude ASC LIMIT 1'
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

    # Size information
    # --------------------------------------------------------------------------
    def select_hike_size(self, hike: int) -> str:
        statement = 'SELECT count(*) FROM pictures WHERE hike={h}'.format(h=hike)
        return statement

    def select_archive_size(self) -> str:
        statement = 'SELECT count(*) FROM pictures'
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
    # NOTE : round(x + 0.499999999999) is used to get the ceiling
    # this is used to get a balanced distribution on skips
    # Otherwise: 0-1.99   ==> 1
    #            only 223 ==> 223
    def select_next_time_skip_in_hikes(self, hike: int, time: int) -> str:
        skip_ahead = 1  # private variable in case we want to change how big the skip is
        statement = 'SELECT * FROM pictures WHERE picture_id = ( \
            SELECT CASE WHEN (SELECT count(*) FROM pictures WHERE hike>{h}) \
                THEN (									  /* hike + skip */ \
                    SELECT picture_id FROM pictures WHERE hike>=({h}+{s}) ORDER BY time ASC LIMIT 1 OFFSET ( \
                        SELECT round( \
                            (CAST((SELECT count(*) FROM pictures WHERE hike={h} AND time<={t}) AS REAL) \
                            /(SELECT count(*) FROM pictures WHERE hike={h})) \
                            * (SELECT count(*) FROM pictures WHERE hike=(SELECT hike FROM pictures WHERE hike>={h}+{s} ORDER BY time ASC LIMIT 1)) \
                        + 0.499999999999) - 1 \
                    ) \
                ) \
                ELSE ( \
                    SELECT picture_id FROM pictures WHERE hike=(SELECT hike FROM pictures WHERE hike>=0 ORDER BY hike ASC LIMIT 1) ORDER BY time ASC LIMIT 1 OFFSET ( \
                        SELECT round( \
                            (CAST((SELECT count(*) FROM pictures WHERE hike={h} AND time<={t}) AS REAL) \
                            /(SELECT count(*) FROM pictures WHERE hike={h})) \
                            * (SELECT count(*) FROM pictures WHERE hike=(SELECT hike FROM pictures WHERE hike>=0 ORDER BY time ASC LIMIT 1)) \
                        + 0.499999999999) - 1 \
                    ) \
                ) \
            END END);'.format(h=hike, t=time, s=skip_ahead)
        return statement

    def select_previous_time_skip_in_hikes(self, hike: int, time: int) -> str:
        skip_back = 1  # private variable in case we want to change how big the skip is
        statement = 'SELECT * FROM pictures WHERE picture_id = ( \
            SELECT CASE WHEN (SELECT count(*) FROM pictures WHERE hike<{h}) \
                THEN (									  /* hike + skip */ /* it requires this extra selection because we want the previous hike, but results need to be returned in ASC order */\
                    SELECT picture_id FROM pictures WHERE hike=(SELECT hike FROM pictures WHERE hike<={h}-{s} ORDER BY time DESC LIMIT 1) ORDER BY time ASC LIMIT 1 OFFSET ( \
                        SELECT round( \
                            (CAST((SELECT count(*) FROM pictures WHERE hike={h} AND time<={t}) AS REAL) \
                            /(SELECT count(*) FROM pictures WHERE hike={h})) \
                            * (SELECT count(*) FROM pictures WHERE hike=(SELECT hike FROM pictures WHERE hike<={h}-{s} ORDER BY time DESC LIMIT 1)) \
                        + 0.499999999999) - 1 \
                    ) \
                ) \
                ELSE ( \
                    SELECT picture_id FROM pictures WHERE hike=(SELECT hike FROM pictures ORDER BY hike DESC LIMIT 1) ORDER BY time ASC LIMIT 1 OFFSET ( \
                        SELECT round( \
                            (CAST((SELECT count(*) FROM pictures WHERE hike={h} AND time<={t}) AS REAL) \
                            /(SELECT count(*) FROM pictures WHERE hike={h})) \
                            * (SELECT count(*) FROM pictures WHERE hike=(SELECT hike FROM pictures ORDER BY hike DESC LIMIT 1)) \
                        + 0.499999999999) - 1 \
                    ) \
                ) \
            END END);'.format(h=hike, t=time, s=skip_back)
        return statement

    # Time Skip in Global
    # Skips every 15 minutes
    # Currently doesn't use the newer rounding logic with 0.499999999999
    def select_next_time_skip_in_global(self, minute: int, time: int) -> str:
        skip_ahead = 15  # private variable in case we want to change how big the skip is
        statement = 'SELECT * FROM pictures WHERE picture_id = ( \
            SELECT CASE WHEN ((SELECT count(DISTINCT minute) FROM pictures WHERE minute>=({m}+{s})) > 0) \
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
                            /* first minute value */						 /* skip value */	 /* how many minutes from bottom of table */ \
                        (SELECT minute FROM pictures ORDER BY minute ASC LIMIT 1) + {s} - (SELECT count(DISTINCT minute) FROM pictures WHERE minute>=({m})) \
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

    def select_previous_time_skip_in_global(self, minute: int, time: int) -> str:
        skip_back = 15  # private variable in case we want to change how big the skip is
        statement = 'SELECT * FROM pictures WHERE picture_id = ( \
        SELECT CASE WHEN ((SELECT count(DISTINCT minute) FROM pictures WHERE minute<=({m}-{s})) > 0) \
            THEN ( /*there is a previous minute above in the table*/ \
                SELECT picture_id FROM pictures WHERE minute=(SELECT DISTINCT minute FROM pictures WHERE minute<={m} ORDER BY minute DESC LIMIT 1 OFFSET {s}) ORDER BY minute ASC, time ASC LIMIT 1 OFFSET ( \
                SELECT CAST(( \
                    (CAST((SELECT count(*) FROM pictures WHERE minute={m} AND time<={t}) AS REAL) /*get # it is in minute (<= for both) casted as float*/ \
                    /(SELECT count(*) FROM pictures WHERE minute={m})) /*divide by the total for this minute*/ \
                    * (SELECT count(*) FROM pictures WHERE minute=(SELECT minute FROM pictures WHERE minute<={m}-{s} ORDER BY minute ASC, time ASC LIMIT 1)) /*multiple by count for next available minute at least 15min ahead*/ \
                ) AS INT) ) - 1 /*cast back to integer. move back 1 (first value of minute has offset of 0)*/ \
            ) \
            ELSE ( /*wrap around to bottom of table*/ \
                SELECT picture_id FROM pictures WHERE minute=( \
                    /* first minute value */						                  /* skip value */	    /* how many minutes from top of table */ \
                    (SELECT DISTINCT minute FROM pictures ORDER BY minute DESC LIMIT 1 OFFSET {s} - (SELECT count(DISTINCT minute) FROM pictures WHERE minute<={m})) \
                ) ORDER BY minute ASC, time ASC LIMIT 1 OFFSET ( \
                SELECT CAST(( \
                    (CAST((SELECT count(*) FROM pictures WHERE minute={m} AND time<={t}) AS REAL) /*get # it is in the minute casted as float */ \
                    /(SELECT count(*) FROM pictures WHERE minute={m})) /*divide by the total for this minute to get percentage*/ \
                    * (SELECT count(*) FROM pictures WHERE minute=(SELECT minute FROM pictures WHERE minute<=( /*multiple this percent by the count of minute with correct offset */ \
                        (SELECT minute FROM pictures ORDER BY minute DESC LIMIT 1) - {s} + (SELECT count(DISTINCT minute) FROM pictures WHERE minute<={m}) /* same from 6 lines above */ \
                    ) ORDER BY minute DESC, time DESC LIMIT 1)) \
                ) AS INT) ) - 1 \
            ) \
            END \
        END);'.format(m=minute, t=time, s=skip_back)
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
    # NOTE : round(x + 0.499999999999) is used to get the ceiling
    # this is used to get a balanced distribution on skips
    # Otherwise: 0-1.99   ==> 1
    #            only 223 ==> 223
    def select_next_altitude_skip_in_hikes(self, hike: int, altrank_hike: float) -> str:
        statement = 'SELECT * FROM pictures WHERE picture_id = ( \
        SELECT CASE WHEN (SELECT count(*) FROM hikes WHERE avg_altitude_rank > (SELECT avg_altitude_rank FROM hikes WHERE hike_id={h})) > 0 \
            THEN ( \
                SELECT picture_id FROM pictures WHERE hike=(SELECT hike_id FROM hikes WHERE avg_altitude_rank>(SELECT avg_altitude_rank FROM hikes WHERE hike_id={h}) ORDER BY avg_altitude_rank ASC LIMIT 1 /*also need to order for next, not just prev*/) \
                ORDER BY altrank_hike ASC LIMIT 1 OFFSET ( \
                    SELECT round( \
                        (CAST((SELECT count(*) FROM pictures WHERE hike={h} AND altrank_hike<={a}) AS REAL) /*numerator of percentage*/ \
                        /(SELECT count(*) FROM pictures WHERE hike={h})) /*denominator of percentage*/ \
                        * (SELECT count(*) FROM pictures WHERE hike=(SELECT hike_id FROM hikes WHERE avg_altitude_rank>(SELECT avg_altitude_rank FROM hikes WHERE hike_id={h}) ORDER BY avg_altitude_rank ASC LIMIT 1 /*also need to order for next, not just prev*/)) \
                    + 0.499999999999) - 1 \
                ) \
            ) \
            ELSE ( \
                SELECT picture_id FROM pictures WHERE hike=(SELECT hike_id FROM hikes ORDER BY avg_altitude_rank ASC LIMIT 1) \
                ORDER BY altrank_hike ASC LIMIT 1 OFFSET ( \
                    SELECT round( \
                        (CAST((SELECT count(*) FROM pictures WHERE hike={h} AND altrank_hike<={a}) AS REAL) /*numerator of percentage*/ \
                        /(SELECT count(*) FROM pictures WHERE hike={h})) /*denominator of percentage*/ \
                        * (SELECT count(*) FROM pictures WHERE hike=(SELECT hike_id FROM hikes ORDER BY avg_altitude_rank ASC LIMIT 1)) \
                    + 0.499999999999) - 1 \
                ) \
            ) \
        END END);'.format(h=hike, a=altrank_hike)
        return statement

    def select_previous_altitude_skip_in_hikes(self, hike: int, altrank_hike: float) -> str:
        statement = 'SELECT * FROM pictures WHERE picture_id = ( \
        SELECT CASE WHEN (SELECT count(*) FROM hikes WHERE avg_altitude_rank < (SELECT avg_altitude_rank FROM hikes WHERE hike_id={h})) > 0 \
            THEN ( \
                SELECT picture_id FROM pictures WHERE hike=(SELECT hike_id FROM hikes WHERE avg_altitude_rank<(SELECT avg_altitude_rank FROM hikes WHERE hike_id={h}) ORDER BY avg_altitude_rank DESC LIMIT 1) \
                ORDER BY altrank_hike ASC LIMIT 1 OFFSET ( \
                    SELECT round( \
                        (CAST((SELECT count(*) FROM pictures WHERE hike={h} AND altrank_hike<={a}) AS REAL) /*numerator of percentage*/ \
                        /(SELECT count(*) FROM pictures WHERE hike={h})) /*denominator of percentage*/ \
                        * (SELECT count(*) FROM pictures WHERE hike=(SELECT hike_id FROM hikes WHERE avg_altitude_rank<(SELECT avg_altitude_rank FROM hikes WHERE hike_id={h}) ORDER BY avg_altitude_rank DESC LIMIT 1)) \
                    + 0.499999999999) - 1 \
                ) \
            ) \
            ELSE ( \
                SELECT picture_id FROM pictures WHERE hike=(SELECT hike_id FROM hikes ORDER BY avg_altitude_rank DESC LIMIT 1) \
                ORDER BY altrank_hike ASC LIMIT 1 OFFSET ( \
                    SELECT round( \
                        (CAST((SELECT count(*) FROM pictures WHERE hike={h} AND altrank_hike<={a}) AS REAL) /*numerator of percentage*/ \
                        /(SELECT count(*) FROM pictures WHERE hike={h})) /*denominator of percentage*/ \
                        * (SELECT count(*) FROM pictures WHERE hike=(SELECT hike_id FROM hikes ORDER BY avg_altitude_rank DESC LIMIT 1)) \
                    + 0.499999999999) - 1 \
                ) \
            ) \
        END END);'.format(h=hike, a=altrank_hike)
        return statement

    # Altitude Skip in Global
    # Also uses the ceiling round, otherwise it would stop at the end of the archive
    # and it wouldn’t wrap back around the same point on the 20th click
    def select_next_altitude_skip_in_global(self, altrank_global: float) -> str:
        skip_perc = 0.05  # variable to change size of the percentage skip
        statement = 'SELECT * FROM pictures WHERE picture_id = ( \
        SELECT CASE WHEN (SELECT count(*) FROM pictures WHERE altrank_global > {a}) >= (SELECT round({p} * (SELECT count(*) FROM pictures) + 0.499999999999)) \
            THEN (SELECT picture_id FROM pictures WHERE altrank_global >= {a} ORDER BY altrank_global ASC LIMIT 1 OFFSET (SELECT round({p} * (SELECT count(*) FROM pictures) + 0.499999999999))) \
            ELSE (SELECT picture_id FROM pictures ORDER BY altrank_global ASC LIMIT 1 OFFSET (SELECT round({p} * (SELECT count(*) FROM pictures) + 0.499999999999) - (SELECT count(*) FROM pictures WHERE altrank_global > {a}) - 1)) \
        END);'.format(a=altrank_global, p=skip_perc)
        return statement

    def select_previous_altitude_skip_in_global(self, altrank_global: float) -> str:
        skip_perc = 0.05  # variable to change size of the percentage skip
        statement = 'SELECT * FROM pictures WHERE picture_id = ( \
        SELECT CASE WHEN (SELECT count(*) FROM pictures WHERE altrank_global < {a}) >= (SELECT round({p} * (SELECT count(*) FROM pictures) + 0.499999999999)) \
            THEN (SELECT picture_id FROM pictures WHERE altrank_global <= {a} ORDER BY altrank_global DESC LIMIT 1 OFFSET (SELECT round({p} * (SELECT count(*) FROM pictures) + 0.499999999999))) \
            ELSE (SELECT picture_id FROM pictures ORDER BY altrank_global DESC LIMIT 1 OFFSET (SELECT round({p} * (SELECT count(*) FROM pictures) + 0.499999999999) - (SELECT count(*) FROM pictures WHERE altrank_global < {a}) - 1)) \
        END);'.format(a=altrank_global, p=skip_perc)
        return statement

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
    def select_next_color_in_global(self, colorrank_global: float, offset: int) -> str:
        statement = 'SELECT * FROM pictures WHERE picture_id = ( \
        SELECT CASE WHEN (SELECT count(*) FROM pictures WHERE color_rank_global > {c}) >= ({o}%(SELECT count(*) FROM pictures)) \
            THEN (SELECT picture_id FROM pictures WHERE color_rank_global >= {c} ORDER BY color_rank_global ASC LIMIT 1 OFFSET ({o}%(SELECT count(*) FROM pictures))) \
            ELSE (SELECT picture_id FROM pictures ORDER BY color_rank_global ASC LIMIT 1 OFFSET ({o}%(SELECT count(*) FROM pictures) - (SELECT count(*) FROM pictures WHERE color_rank_global > {c}) - 1)) \
        END);'.format(c=colorrank_global, o=offset)
        return statement

    def select_previous_color_in_global(self, colorrank_global: float, offset: int) -> str:
        statement = 'SELECT * FROM pictures WHERE picture_id = ( \
        SELECT CASE WHEN (SELECT count(*) FROM pictures WHERE color_rank_global < {c}) >= ({o}%(SELECT count(*) FROM pictures)) \
            THEN (SELECT picture_id FROM pictures WHERE color_rank_global <= {c} ORDER BY color_rank_global DESC LIMIT 1 OFFSET ({o}%(SELECT count(*) FROM pictures))) \
            ELSE (SELECT picture_id FROM pictures ORDER BY color_rank_global DESC LIMIT 1 OFFSET ({o}%(SELECT count(*) FROM pictures) - (SELECT count(*) FROM pictures WHERE color_rank_global < {c}) - 1)) \
        END);'.format(c=colorrank_global, o=offset)
        return statement

    # Color Skip in Hikes
    # NOTE : round(x + 0.499999999999) is used to get the ceiling
    # this is used to get a balanced distribution on skips
    # Otherwise: 0-1.99   ==> 1
    #            only 223 ==> 223
    def select_next_color_skip_in_hikes(self, hike: int, colorrank_hike: float) -> str:
        statement = 'SELECT * FROM pictures WHERE picture_id = ( \
        SELECT CASE WHEN (SELECT count(*) FROM hikes WHERE color_rank > (SELECT color_rank FROM hikes WHERE hike_id={h})) > 0 \
            THEN ( \
                SELECT picture_id FROM pictures WHERE hike=(SELECT hike_id FROM hikes WHERE color_rank>(SELECT color_rank FROM hikes WHERE hike_id={h}) ORDER BY color_rank ASC LIMIT 1 /*also need to order for next, not just prev*/) \
                ORDER BY color_rank_hike ASC LIMIT 1 OFFSET ( \
                    SELECT round( \
                        (CAST((SELECT count(*) FROM pictures WHERE hike={h} AND color_rank_hike<={c}) AS REAL) /*numerator of percentage*/ \
                        /(SELECT count(*) FROM pictures WHERE hike={h})) /*denominator of percentage*/ \
                        * (SELECT count(*) FROM pictures WHERE hike=(SELECT hike_id FROM hikes WHERE color_rank>(SELECT color_rank FROM hikes WHERE hike_id={h}) ORDER BY color_rank ASC LIMIT 1 /*also need to order for next, not just prev*/)) \
                    + 0.499999999999) - 1 \
                ) \
            ) \
            ELSE ( \
                SELECT picture_id FROM pictures WHERE hike=(SELECT hike_id FROM hikes ORDER BY color_rank ASC LIMIT 1) \
                ORDER BY color_rank_hike ASC LIMIT 1 OFFSET ( \
                    SELECT round( \
                        (CAST((SELECT count(*) FROM pictures WHERE hike={h} AND color_rank_hike<={c}) AS REAL) /*numerator of percentage*/ \
                        /(SELECT count(*) FROM pictures WHERE hike={h})) /*denominator of percentage*/ \
                        * (SELECT count(*) FROM pictures WHERE hike=(SELECT hike_id FROM hikes ORDER BY color_rank ASC LIMIT 1)) \
                    + 0.499999999999) - 1 \
                ) \
            ) \
        END END);'.format(h=hike, c=colorrank_hike)
        return statement

    def select_previous_color_skip_in_hikes(self, hike: int, colorrank_hike: float) -> str:
        statement = 'SELECT * FROM pictures WHERE picture_id = ( \
        SELECT CASE WHEN (SELECT count(*) FROM hikes WHERE color_rank < (SELECT color_rank FROM hikes WHERE hike_id={h})) > 0 \
            THEN ( \
                SELECT picture_id FROM pictures WHERE hike=(SELECT hike_id FROM hikes WHERE color_rank<(SELECT color_rank FROM hikes WHERE hike_id={h}) ORDER BY color_rank DESC LIMIT 1) \
                ORDER BY color_rank_hike ASC LIMIT 1 OFFSET ( \
                    SELECT round( \
                        (CAST((SELECT count(*) FROM pictures WHERE hike={h} AND color_rank_hike<={c}) AS REAL) /*numerator of percentage*/ \
                        /(SELECT count(*) FROM pictures WHERE hike={h})) /*denominator of percentage*/ \
                        * (SELECT count(*) FROM pictures WHERE hike=(SELECT hike_id FROM hikes WHERE color_rank<(SELECT color_rank FROM hikes WHERE hike_id={h}) ORDER BY color_rank DESC LIMIT 1)) \
                    + 0.499999999999) - 1 \
                ) \
            ) \
            ELSE ( \
                SELECT picture_id FROM pictures WHERE hike=(SELECT hike_id FROM hikes ORDER BY color_rank DESC LIMIT 1) \
                ORDER BY color_rank_hike ASC LIMIT 1 OFFSET ( \
                    SELECT round( \
                        (CAST((SELECT count(*) FROM pictures WHERE hike={h} AND color_rank_hike<={c}) AS REAL) /*numerator of percentage*/ \
                        /(SELECT count(*) FROM pictures WHERE hike={h})) /*denominator of percentage*/ \
                        * (SELECT count(*) FROM pictures WHERE hike=(SELECT hike_id FROM hikes ORDER BY color_rank DESC LIMIT 1)) \
                    + 0.499999999999) - 1 \
                ) \
            ) \
        END END);'.format(h=hike, c=colorrank_hike)
        return statement

    # Color Skip in Global
    # Also uses the ceiling round, otherwise it would stop at the end of the archive
    # and it wouldn’t wrap back around the same point on the 20th click
    def select_next_color_skip_in_global(self, colorrank_global: float) -> str:
        skip_perc = 0.05  # variable to change size of the percentage skip
        statement = 'SELECT * FROM pictures WHERE picture_id = ( \
        SELECT CASE WHEN (SELECT count(*) FROM pictures WHERE color_rank_global > {c}) >= (SELECT round({p} * (SELECT count(*) FROM pictures) + 0.499999999999)) \
            THEN (SELECT picture_id FROM pictures WHERE color_rank_global >= {c} ORDER BY color_rank_global ASC LIMIT 1 OFFSET (SELECT round({p} * (SELECT count(*) FROM pictures) + 0.499999999999))) \
            ELSE (SELECT picture_id FROM pictures ORDER BY color_rank_global ASC LIMIT 1 OFFSET (SELECT round({p} * (SELECT count(*) FROM pictures) + 0.499999999999) - (SELECT count(*) FROM pictures WHERE color_rank_global > {c}) - 1)) \
        END);'.format(c=colorrank_global, p=skip_perc)
        return statement

    def select_previous_color_skip_in_global(self, colorrank_global: float) -> str:
        skip_perc = 0.05  # variable to change size of the percentage skip
        statement = 'SELECT * FROM pictures WHERE picture_id = ( \
        SELECT CASE WHEN (SELECT count(*) FROM pictures WHERE color_rank_global < {c}) >= (SELECT round({p} * (SELECT count(*) FROM pictures) + 0.499999999999)) \
            THEN (SELECT picture_id FROM pictures WHERE color_rank_global <= {c} ORDER BY color_rank_global DESC LIMIT 1 OFFSET (SELECT round({p} * (SELECT count(*) FROM pictures) + 0.499999999999))) \
            ELSE (SELECT picture_id FROM pictures ORDER BY color_rank_global DESC LIMIT 1 OFFSET (SELECT round({p} * (SELECT count(*) FROM pictures) + 0.499999999999) - (SELECT count(*) FROM pictures WHERE color_rank_global < {c}) - 1)) \
        END);'.format(c=colorrank_global, p=skip_perc)
        return statement

    # --------------------------------------------------------------------------
    # UI Calls (2021)
    # --------------------------------------------------------------------------

    # Altitude Graph in hikes
    def ui_select_altitudes_for_hike_sortby(self, mode: str, hike: int, idxList: str) -> str:
        if mode == 'alt':
            ordering = 'altrank_hike ASC'
        elif mode == 'color':
            ordering = 'color_rank_hike ASC'
        elif mode == 'time':
            ordering = 'time ASC'
        else:
            raise ValueError('Expected a str parameter which was not given.')

        statement = 'SELECT altitude FROM pictures WHERE hike = {h} AND index_in_hike IN {iL} ORDER BY {o}'.format(h=hike, iL=idxList, o=ordering)
        return statement

    # Altitude Graph in archive
    def ui_select_altitudes_for_archive_sortby(self, mode: str, idxList: str) -> str:
        if mode == 'alt':
            ordering = 'altrank_global ASC'
        elif mode == 'color':
            ordering = 'color_rank_global ASC'
        elif mode == 'time':
            ordering = 'time_rank_global ASC'  # minute rank (not chronological)
        else:
            raise ValueError('Expected a str parameter which was not given.')

        statement = 'SELECT altitude FROM pictures WHERE index_in_hike IN {iL} ORDER BY {o}'.format(iL=idxList, o=ordering)
        return statement

    # Color Bar in hikes
    def ui_select_colors_for_hike_sortby(self, mode: str, hike: int, idxList: str) -> str:
        if mode == 'alt':
            ordering = 'altrank_hike ASC'
        elif mode == 'color':
            ordering = 'color_rank_hike ASC'
        elif mode == 'time':
            ordering = 'time ASC'
        else:
            raise ValueError('Expected a str parameter which was not given.')

        statement = 'SELECT color_rgb FROM pictures WHERE hike = {h} AND index_in_hike IN {iL} ORDER BY {o}'.format(h=hike, iL=idxList, o=ordering)
        return statement

    # Color Bar in archive
    def ui_select_colors_for_archive_sortby(self, mode: str, idxList: str) -> str:
        if mode == 'alt':
            ordering = 'altrank_global ASC'
        elif mode == 'color':
            ordering = 'color_rank_global ASC'
        elif mode == 'time':
            ordering = 'time_rank_global ASC'
        else:
            raise ValueError('Expected a str parameter which was not given.')

        statement = 'SELECT color_rgb FROM pictures WHERE index_in_hike IN {iL} ORDER BY {o}'.format(iL=idxList, o=ordering)
        return statement

    # Time Bar & Indicators Percentage in hikes
    # (also needed for the indicators on the other modes)
    def ui_select_percentage_in_hike_with_mode(self, mode: str, picture_id: int, hike: int) -> str:
        if mode == 'alt':
            ordering = 'altrank_hike'
        elif mode == 'color':
            ordering = 'color_rank_hike'
        elif mode == 'time':
            ordering = 'index_in_hike'
        else:
            raise ValueError('Expected a str parameter which was not given.')

        statement = 'SELECT CAST((SELECT {o} FROM pictures WHERE picture_id={p}) AS REAL)/(SELECT count(*) FROM pictures \
        WHERE hike={h});'.format(o=ordering, p=picture_id, h=hike)

        return statement

    # Time Bar & Indicators Percentage in archive
    # (also needed for the indicators on the other modes)
    def ui_select_percentage_in_archive_with_mode(self, mode: str, picture_id: int) -> str:
        if mode == 'alt':
            ordering = 'altrank_global'
        elif mode == 'color':
            ordering = 'color_rank_global'
        elif mode == 'time':
            ordering = 'time_rank_global'  # minute rank (not chronological)
        else:
            raise ValueError('Expected a str parameter which was not given.')

        statement = 'SELECT CAST((SELECT {o} FROM pictures WHERE picture_id={p}) AS REAL)/(SELECT count(*) FROM pictures \
        );'.format(o=ordering, p=picture_id)

        return statement

    # --------------------------------------------------------------------------
    # Old Projector Functions
    # --------------------------------------------------------------------------
    # ******************************     Time     ******************************

    # Time - next & previous across hikes
    def select_by_time_next_picture(self, time: float) -> str:
        statement = 'SELECT * FROM pictures WHERE time>{t} \
            ORDER BY time ASC LIMIT 1'.format(t=time)
        return statement

    def select_by_time_previous_picture(self, time: float) -> str:
        statement = 'SELECT * FROM pictures WHERE time<{t} \
            ORDER BY time DESC LIMIT 1'.format(t=time)
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
        statement = 'SELECT * FROM pictures WHERE hike == {h} AND altitude < 10000 AND altitude > -400 AND \
            camera1 IS NOT NULL AND camera2 IS NOT NULL AND camera3 IS NOT NULL'.format(h=hike_id)
        return statement

    def select_hikerow_by_index(self, hike_id: int, index_in_hike: int) -> int:
        statement = 'SELECT * FROM pictures WHERE hike == {h} AND index_in_hike == {i}'.format(h=hike_id, i=index_in_hike)
        return statement

    def upsert_picture_row(self,
                            time: float,
                            year: int,
                            month: int,
                            day: int,
                            minute: int,
                            dayofweek: int,
                            hike: int,
                            index_in_hike: int,
                            time_rank_global: int,
                            altitude: float,
                            altrank_hike: int,
                            altrank_global: int,
                            altrank_global_h: int,
                            color_hsv: str,         # most dominant color in hsv
                            color_rgb: str,         # most dominant color in rgb
                            color_rank_value: str,
                            color_rank_hike: int,
                            color_rank_global: int,
                            color_rank_global_h: int,
                            colors_count: int,
                            colors_rgb: str,       # at most 10 dominant colors in rgb
                            colors_conf: str,
                            camera1: str,
                            camera2: str,
                            camera3: str,
                            camera_landscape: str,
                            created_date_time: str) -> int:
        statement = 'INSERT OR REPLACE INTO pictures \
            (time, \
                year, month, day, minute, dayofweek, \
                hike, index_in_hike, time_rank_global, altitude, altrank_hike, altrank_global, altrank_global_h, \
                color_hsv, color_rgb, color_rank_value, color_rank_hike, color_rank_global, color_rank_global_h, \
                colors_count, colors_rgb, colors_conf, \
                camera1, camera2, camera3, camera_landscape, created_date_time) \
            VALUES ({}, \
                    {}, {}, {}, {}, {}, \
                    {}, {}, {}, {}, {}, {}, {}, \
                    "{}", "{}", {}, {}, {}, {}, \
                    {}, "{}", "{}", \
                    "{}", "{}", "{}", "{}", "{}")\
            '.format(time,
                        year, month, day, minute, dayofweek,
                        hike, index_in_hike, time_rank_global, altitude, altrank_hike, altrank_global, altrank_global_h,
                        color_hsv, color_rgb, color_rank_value, color_rank_hike, color_rank_global, color_rank_global_h,
                        colors_count, colors_rgb, colors_conf,
                        camera1, camera2, camera3, camera_landscape, created_date_time)
        return statement

    def upsert_hike_row(self,
                        hike_id: int,
                        avg_altitude: float,
                        avg_altitude_rank: int,
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
                        color_hsv: str,
                        color_rgb: str,
                        color_rank_value: str,
                        color_rank: int,
                        pictures: int,
                        path: str,
                        created_date_time: str) -> str:
        statement = 'INSERT OR REPLACE INTO hikes \
            (hike_id, avg_altitude, avg_altitude_rank, \
                start_time, start_year, start_month, start_day, start_minute, start_dayofweek, \
                end_time, end_year, end_month, end_day, end_minute, end_dayofweek, \
                color_hsv, color_rgb, color_rank_value, color_rank, \
                pictures, path, created_date_time) \
            VALUES ({}, {}, {}, \
                    {}, {}, {}, {}, {}, {}, \
                    {}, {}, {}, {}, {}, {}, \
                    "{}", "{}", "{}", {}, \
                    {}, "{}", "{}")\
            '.format(hike_id, avg_altitude, avg_altitude_rank,
                        start_time, start_year, start_month, start_day, start_minute, start_dayofweek,
                        end_time, end_year, end_month, end_day, end_minute, end_dayofweek,
                        color_hsv, color_rgb, color_rank_value, color_rank,
                        pictures, path, created_date_time)
        return statement

    def get_hike_average_color(self, hike_id: int):
        statement = 'SELECT color_rgb FROM hikes WHERE hike_id == {}'.format(hike_id)
        return statement


    def get_size_of_hike(self, hike_id: int):
        statement = 'SELECT pictures FROM hikes WHERE hike_id == {}'.format(hike_id)
        return statement

    def get_picture_with_timestamp(self, time: float):
        statement = 'SELECT count(*) FROM pictures WHERE time == {}'.format(time)
        return statement

    # format = ('hsv'|'HSV') or ('rgb'|'RGB')
    def get_dominant_color_for_picture_of_given_timestamp(self, time: float, format: str):
        statement = ""

        # for default color, return cam2's color (the middle one)
        if (format == 'hsv' or format == 'HSV'):
            statement = 'SELECT color_hsv FROM pictures WHERE time == {}'.format(time)
        elif (format == 'rgb' or format == 'RGB'):
            statement = 'SELECT color_rgb FROM pictures WHERE time == {}'.format(time)
        else:
            return -1

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

    def get_hike_created_date_time(self, hike_id: int) -> str:
        statement = "SELECT created_date_time FROM hikes WHERE hike_id == {}".format(hike_id)
        return statement


    ### Global rankings for pictures

    def get_pictures_time_altitude_domcol(self):
        statement = 'SELECT time, altitude, color_hsv, color_rgb, minute FROM pictures'
        return statement

    def update_pictures_globalTimeRank(self, timestamp: float, timeRank: int):
        statement = 'UPDATE pictures SET time_rank_global = {} WHERE time = {}'.format(timeRank, timestamp)
        return statement

    def update_pictures_globalAltRank(self, timestamp: float, altRank: int):
        statement = 'UPDATE pictures SET altrank_global = {} WHERE time = {}'.format(altRank, timestamp)
        return statement

    def update_pictures_globalColRank(self, timestamp: float, colRank: int):
        statement = 'UPDATE pictures SET color_rank_global = {} WHERE time = {}'.format(colRank, timestamp)
        return statement


    ### Global rankings for hikes

    def get_hikes_id_altitude_domcol(self):
        statement = 'SELECT hike_id, avg_altitude, color_hsv, color_rgb FROM hikes'
        return statement

    def update_hikes_globalAltRank(self, hike_id: int, altRank: int):
        statement = 'UPDATE hikes SET avg_altitude_rank = {} WHERE hike_id = {}'.format(altRank, hike_id)
        return statement

    def update_hikes_globalColRank(self, hike_id: int, colRank: int):
        statement = 'UPDATE hikes SET color_rank = {} WHERE hike_id = {}'.format(colRank, hike_id)
        return statement

    # altrank_global_h
    def get_hikes_by_avg_altrank(self):
        statement = 'SELECT hike_id, pictures FROM hikes ORDER BY avg_altitude_rank'
        return statement

    def get_pictures_of_specific_hike_by_altrank(self, hike_id: int):
        statement = 'SELECT picture_id FROM pictures WHERE hike = {} ORDER BY altrank_hike'.format(hike_id)
        return statement

    def update_pictures_altrank_global_h(self, rankIndex: int, picture_id: int):
        statement = 'UPDATE pictures SET altrank_global_h = {} WHERE picture_id = {}'.format(rankIndex, picture_id)
        return statement

    # color_rank_global_h
    def get_hikes_by_color_rank(self):
        statement = 'SELECT hike_id, pictures FROM hikes ORDER BY color_rank'
        return statement

    def get_pictures_of_specific_hike_by_color_rank(self, hike_id: int):
        statement = 'SELECT picture_id FROM pictures WHERE hike = {} ORDER BY color_rank_hike'.format(hike_id)
        return statement

    def update_pictures_color_rank_global_h(self, rankIndex: int, picture_id: int):
        statement = 'UPDATE pictures SET color_rank_global_h = {} WHERE picture_id = {}'.format(rankIndex, picture_id)
        return statement


    ### Color Spectrum

    def get_pictures_rgb_hike(self, hike: int):
        statement = 'SELECT color_rgb FROM pictures WHERE hike = {} ORDER BY color_rank_hike'.format(hike)
        return statement

    def get_pictures_rgb_global(self):
        statement = 'SELECT color_rgb FROM pictures ORDER BY color_rank_global'
        return statement

    def get_pictures_rgb_global_h(self):
        statement = 'SELECT color_rgb FROM pictures ORDER BY color_rank_global_h'
        return statement

    def get_hikes_rgb_global(self):
        statement = 'SELECT color_rgb FROM hikes ORDER BY color_rank'
        return statement


    ### Zero-byte filtering

    def get_pictures_count_of_selected_hike(self, hike: int):
        statement = 'select count(*) from pictures where hike = {}'.format(hike)
        return statement

    def get_pictures_of_selected_hike(self, hike: int):
        statement = 'select * from pictures where hike = {}'.format(hike)
        return statement

    def delete_picture_of_given_timestamp(self, timestamp: float):
        statement = 'delete from pictures where time = {}'.format(timestamp)
        return statement

    def update_hikes_total_picture_count_of_given_hike(self, picCount: int, hike: int):
        statement = 'update hikes set pictures = {} where hike_id = {}'.format(picCount, hike)
        return statement
