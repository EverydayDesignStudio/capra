from datetime import date, time, datetime
from PyQt5.QtGui import QColor

# Defines custom data types for capra. Currently all are only used in conjunction
# with the projector


class CapraDataType:
    """Superclass for shared functionality between Picture and Hike objects"""
    def _parse_hr_min(self, timestamp: float) -> str:
        """Parses timestamp into string
        ::

            :param timestamp: Unix timestamp
            :return str: '5:19 PM'
        """
        t = datetime.fromtimestamp(timestamp)
        s = t.strftime('%-I:%M')
        return s

    def _parse_sec(self, timestamp: float) -> str:
        """Parses timestamp into string
        ::

            :param timestamp: Unix timestamp
            :return str: ':24'
        """
        t = datetime.fromtimestamp(timestamp)
        s = t.strftime(':%S %p')
        return s

    def _parse_date(self, timestamp: float) -> str:
        """Parses timestamp into string
        ::

            :param timestamp: Unix timestamp
            :return str: 'April 27, 2019'
        """
        d = datetime.fromtimestamp(timestamp)
        s = d.strftime('%B %-d, %Y')
        return s

    def _parse_hike(self, hike: int) -> str:
        """Parses `int` into string
        ::

            :param hike: int
            :return str: 'Hike 2'
        """
        s = 'Hike {h}'.format(h=hike)
        return s

    def _parse_color(self, text: str) -> QColor:
        """Parses `,` separated text into QColor
        ::

            :param text: input format "217,220,237"
            :return: QColor in RBG format
        """

        c = text.split(',')
        color = QColor(int(c[0]), int(c[1]), int(c[2]))
        return color

    def _parse_color_HSV(self, text: str) -> QColor:
        """Parses `,` separated text into QColor
        ::

            :param text: input format "217,220,237"
            :return: QColor in HSV format
        """
        c = text.split(',')
        color = QColor()
        color.setHsv(int(c[0]), int(c[1]), int(c[2]))
        return color

    def _parse_color_list(self, text: str) -> list:
        """Parses `|` and `,` separated text into list of QColors
        ::

            :param text: input format "217,220,237|92,78,69|50,49,43|50,42,31|78,75,82"
            :return: list of QColors
        """

        color_strs = text.split('|')
        colorlist = list()
        for c in color_strs:
            color = self._parse_color(c)
            colorlist.append(color)
        return colorlist

    def _parse_percent_list(self, text: str) -> list:
        """Parses `,` separated text into a list of floats
        ::

            :param text: input format "0.46,0.16,0.15,0.15,0.09"
            :return: list of float (each value is between 0.0 - .99)
        """

        percents = text.split(',')
        percents = list(map(float, percents))
        return percents


class Picture(CapraDataType):
    """Defines object which hold a row from the database table 'pictures'"""

    def __init__(self, picture_id, time, year, month, day, minute, dayofweek, hike_id, index_in_hike, timerank_global,
                 altitude, altrank_hike, altrank_global, altrank_global_h,
                 color_hsv, color_rgb, colorrank_hike, colorrank_global, colorrank_global_h,
                 colors_count, colors_rgb, colors_conf,
                 camera1, camera2, camera3, cameraf, created, updated):
        super().__init__()
        self.picture_id = picture_id
        self.time = time
        self.year = year
        self.month = month
        self.day = day
        self.minute = minute
        self.dayofweek = dayofweek

        self.hike_id = hike_id
        self.index_in_hike = index_in_hike
        self.timerank_global = timerank_global

        self.altitude = altitude
        self.altrank_hike = altrank_hike
        self.altrank_global = altrank_global
        self.altrank_global_h = altrank_global_h

        self.color_hsv = self._parse_color_HSV(color_hsv)
        self.color_rgb = self._parse_color(color_rgb)
        self.colorrank_hike = colorrank_hike
        self.colorrank_global = colorrank_global
        self.colorrank_global_h = colorrank_global_h
        self.colors_count = colors_count
        self.colors_rgb = self._parse_color_list(colors_rgb)
        self.colors_conf = self._parse_percent_list(colors_conf)

        self.camera1 = camera1
        self.camera2 = camera2
        self.camera3 = camera3
        self.cameraf = cameraf

        self.created = created
        self.updated = updated

        # Labels for the UI
        self.uitime_hrmm = self._parse_hr_min(self.time)
        self.uitime_sec = self._parse_sec(self.time)
        self.uidate = self._parse_date(self.time)
        self.uihike = self._parse_hike(self.hike_id)
        self.uialtitude = str(int(self.altitude))

    def print_obj_mvp(self):
        print('({id}, {t}, {yr}, {mth}, {day}, {min}, {dow}, {hike_id}, {index}, {alt}, {altr}, {hsv}, {rgb}, {crh}, {crg}, {c1}, {c2}, {c3}, {cf})\
            '.format(id=self.picture_id, t=self.time, yr=self.year, mth=self.month, day=self.day,
                     min=self.minute, dow=self.dayofweek, hike_id=self.hike_id, index=self.index_in_hike,
                     alt=self.altitude, altr=self.altrank_global, hsv=self.color_hsv, rgb=self.color_rgb,
                     crh=self.colorrank_hike, crg=self.colorrank_global, c1=self.camera1, c2=self.camera2, c3=self.camera3, cf=self.cameraf))

    def print_obj(self):
        print('id\ttime\t\taltitude\thike_id\tindex\taltrank_hike\tcolorrank_hike\tpath')
        print('{id}\t{t}\t{alt}\t\t{hike_id}\t{index}\t{ar}\t\t{cr}\t{pth}\n\
            '.format(id=self.picture_id, t=self.time, alt=self.altitude,
                     hike_id=self.hike_id, index=self.index_in_hike, ar=self.altrank_hike, cr=self.colorrank_hike, pth=self.cameraf))


class Hike(CapraDataType):
    """Defines object which hold a row from the database table 'hikes'"""

    def __init__(self, hike_id, avg_altitude, avg_altrank,
                 start_time, start_year, start_month, start_day, start_minute, start_dayofweek,
                 end_time, end_year, end_month, end_day, end_minute, end_dayofweek,
                 color_rgb, color_rank,
                 num_pictures, path, created, updated):
        super().__init__()

        self.hike_id = hike_id
        self.avg_altitude = avg_altitude
        self.avg_altrank = avg_altrank

        self.start_time = start_time
        self.start_year = start_year
        self.start_month = start_month
        self.start_day = start_day
        self.start_minute = start_minute
        self.start_dayofweek = start_dayofweek
        self.end_time = end_time
        self.end_year = end_year
        self.end_month = end_month
        self.end_day = end_day
        self.end_minute = end_minute
        self.end_dayofweek = end_dayofweek

        self.color_rgb = self._parse_color(color_rgb)
        self.color_rank = color_rank
        self.num_pictures = num_pictures
        self.path = path

        self.created = created
        self.updated = updated

        self.uistarttime_hrmm = self._parse_hr_min(self.start_time)
        self.uistartdate = self._parse_date(self.start_time)
        self.uihike = self._parse_hike(self.hike_id)
        self.uialtitude = str(int(self.avg_altitude))

    def print_obj(self):
        print('Hike ID\tstart time\t\tavg_alt\tavg_altrank\tcolor\tcolor_rank\tpictures\tpath')
        print('{id}\t{t}\t{avg_alt}\t{avg_altrank}\t{color}\t{color_rank}\t{pic}\t{path}\n\
            '.format(id=self.hike_id, t=self.start_time, avg_alt=self.avg_altitude, avg_altrank=self.avg_altrank,
                        color=self.color_rgb, color_rank=self.color_rank, pic=self.num_pictures, path=self.path))

    def get_hike_length_seconds(self) -> float:
        return round(self.end_time - self.start_time, 0)

    def get_hike_length_minutes(self) -> float:
        return round((self.end_time - self.start_time)/60, 1)


class UIData:
    """Defines object which holds all the UI data for the archive"""

    def __init__(self):
        super().__init__()

        # Hikes UI data
        self.indexListForHike = {}

        self.altitudesSortByAltitudeForHike = {}
        self.altitudesSortByColorForHike = {}
        self.altitudesSortByTimeForHike = {}

        self.colorSortByAltitudeForHike = {}
        self.colorSortByColorForHike = {}
        self.colorSortByTimeForHike = {}

        # Archive UI data
        self.indexListForArchive = []

        self.altitudesSortByAltitudeForArchive = []
        self.altitudesSortByColorForArchive = []
        self.altitudesSortByTimeForArchive = []

        self.colorSortByAltitudeForArchive = []
        self.colorSortByColorForArchive = []
        self.colorSortByTimeForArchive = []
