#!/usr/bin/env python3

from PyQt5.QtGui import *
from classes.capra_data_types import Picture, Hike
from classes.sql_controller import SQLController
from classes.sql_statements import SQLStatements
import unittest


class DatabaseTest(unittest.TestCase):
    # no / infront makes the path relative
    # DB = 'tests/capra_projector_may2021.db'
    # DB = 'tests/capra_projector_jun2021_min_full_clean_0618.db'
    # DB = 'tests/capra_projector_apr2021_min_test_full.db'
    # DB = 'tests/capra_projector_jun2021_min_test_0623.db'
    DB = 'tests/capra_projector_jun2021_min_test_0708.db'
    directory = 'capra-storage'
    sql_controller = None
    sql_statements = None
    picture = None

    hikes = []
    picture_ids = []  # only the 1st picture_id in each hike

    @classmethod
    def setUpClass(self):
        # NOTE - if the database or id is changed, all the tests will break
        # They are dependent upon that
        self.sql_controller = SQLController(database=self.DB, directory=self.directory)
        self.picture = self.sql_controller.get_picture_with_id(11994)

        # For testing directly on the sql statements
        self.sql_statements = SQLStatements()

        # Grab an array of hikes from the database
        sql = 'SELECT hike_id FROM hikes ORDER BY hike_id ASC;'
        rows = self.sql_controller._execute_query_for_anything(sql)
        i = 0
        for r in rows:
            self.hikes.append(r[0])

            # Grab the first picture_id from each hike from the database
            sql = 'SELECT picture_id FROM pictures WHERE hike={h} ORDER BY index_in_hike ASC LIMIT 1;'.format(h=r[0])
            pid = self.sql_controller._execute_query_for_int(sql)
            self.picture_ids.append(pid)
            i += 1

    @classmethod
    def tearDownClass(self):
        self.sql_controller = None

    def test_get_picture_with_id(self):
        self.assertEqual(self.picture.picture_id, 11994)
        self.assertEqual(self.picture.altitude, 2128.38)

    # Size Calls
    # --------------------------------------------------------------------------
    def test_get_hike_size(self):
        size = self.sql_controller.get_hike_size(self.picture)
        self.assertEqual(size, 3561)

    def test_get_archive_size(self):
        size = self.sql_controller.get_archive_size()
        self.assertEqual(size, 30404)

    # Data Types
    # --------------------------------------------------------------------------
    def test_picture_object(self):
        picture = self.sql_controller.get_picture_with_id(1994)

        self.assertEqual(picture.picture_id, 1994)
        self.assertEqual(picture.time, 1556391512.0)
        self.assertEqual(picture.year, 2019)
        self.assertEqual(picture.month, 4)
        self.assertEqual(picture.day, 27)
        self.assertEqual(picture.minute, 718)
        self.assertEqual(picture.dayofweek, 5)

        self.assertEqual(picture.hike_id, 3)
        self.assertEqual(picture.index_in_hike, 879)

        self.assertEqual(picture.altitude, 936.62)
        self.assertEqual(picture.altrank_hike, 855)
        self.assertEqual(picture.altrank_global, 17954)
        self.assertEqual(picture.altrank_global_h, 19549)

        hsvColor = QColor()
        hsvColor.setHsv(25, 173, 49)
        self.assertEqual(picture.color_hsv, hsvColor)
        rgbColor = QColor(49, 43, 16)
        self.assertEqual(picture.color_rgb, rgbColor)
        self.assertEqual(picture.colorrank_hike, 167)
        self.assertEqual(picture.colorrank_global, 3310)
        self.assertEqual(picture.colorrank_global_h, 15042)
        self.assertEqual(picture.colors_count, 4)
        colorList = [QColor(49, 43, 16), QColor(117, 111, 69),
                     QColor(200, 201, 214), QColor(18, 18, 16)]

        self.assertEqual(picture.colors_rgb, colorList)
        self.assertEqual(picture.colors_conf, [0.17, 0.16, 0.15, 0.11])

        self.assertEqual(picture.camera1, 'capra-storage/hike3/878_cam1.jpg')
        self.assertEqual(picture.camera2, 'capra-storage/hike3/878_cam2.jpg')
        self.assertEqual(picture.camera3, 'capra-storage/hike3/878_cam3.jpg')
        self.assertEqual(picture.cameraf, 'capra-storage/hike3/878_cam2f.jpg')
        self.assertEqual(picture.created, '2019-08-22 17:44:51')
        self.assertEqual(picture.updated, '2021-07-08 19:44:47')

    def test_hike_object(self):
        hike = self.sql_controller.get_hike_with_id(59)

        self.assertEqual(hike.hike_id, 59)
        self.assertEqual(hike.avg_altitude, 916.65)
        self.assertEqual(hike.avg_altrank, 22)

        self.assertEqual(hike.start_time, 1598658160.0)
        self.assertEqual(hike.start_year, 2020)
        self.assertEqual(hike.start_month, 8)
        self.assertEqual(hike.start_day, 28)
        self.assertEqual(hike.start_minute, 1002)
        self.assertEqual(hike.start_dayofweek, 4)

        self.assertEqual(hike.end_time, 1598675747.0)
        self.assertEqual(hike.end_year, 2020)
        self.assertEqual(hike.end_month, 8)
        self.assertEqual(hike.end_day, 28)
        self.assertEqual(hike.end_minute, 1295)
        self.assertEqual(hike.end_dayofweek, 4)

        self.assertEqual(hike.color_rgb, QColor(78, 74, 61))
        self.assertEqual(hike.color_rank, 11)
        self.assertEqual(hike.num_pictures, 2134)
        self.assertEqual(hike.path, 'capra-storage/hike59/')
        self.assertEqual(hike.created, '2020-08-28 23:42:39')
        self.assertEqual(hike.updated, '2021-07-08 21:23:04')

    # UI Databse Calls
    # --------------------------------------------------------------------------
    def test_count_colors_for_hikes(self):
        size = 128.0  # variable to test different return size of elements

        # 16 - 24, 14891
        # 30 - 44, 18922
        # 41 - 81, 21252
        # 43 - 62, 21333

        # These all have 128 or more pictures
        picture_ids = [1, 893, 1116, 3274, 3659, 5049, 5953, 7369, 8817, 8996, 12557, 14915, 16641,
                       18966, 19526, 21395, 23513, 24632, 25116, 25592, 27019, 27286, 27656, 29790]

        for p in picture_ids:
            pic = self.sql_controller.get_picture_with_id(p)

            colors = self.sql_controller.ui_get_colors_for_hike_sortby('alt', pic)
            self.assertEqual(len(colors), size)
            colors = self.sql_controller.ui_get_colors_for_hike_sortby('color', pic)
            self.assertEqual(len(colors), size)
            colors = self.sql_controller.ui_get_colors_for_hike_sortby('time', pic)
            self.assertEqual(len(colors), size)

    # Altitude Graph
    # TODO - Tests for altitude graph list

    # Color Bar
    def test_ui_get_colors_for_hike(self):
        self.assertEqual(self.picture.picture_id, 11994)
        self.assertEqual(self.picture.hike_id, 10)
        rgbColor = QColor(79, 57, 48)
        self.assertEqual(self.picture.color_rgb, rgbColor)

        # Sorted by altrank_hike ASC
        colors = self.sql_controller.ui_get_colors_for_hike_sortby('alt', self.picture)
        self.assertEqual(len(colors), 128)
        color0 = QColor(48, 52, 44)
        color94 = QColor(165, 179, 197)
        color126 = QColor(200, 199, 210)

        self.assertEqual(colors[0], color0)
        self.assertEqual(colors[94], color94)
        self.assertEqual(colors[126], color126)

        # Sorted by color_rank_hike ASC
        colors = self.sql_controller.ui_get_colors_for_hike_sortby('color', self.picture)
        self.assertEqual(len(colors), 128)
        color0 = QColor(0, 0, 0)
        color94 = QColor(1, 1, 1)
        color126 = QColor(91, 87, 90)

        self.assertEqual(colors[0], color0)
        self.assertEqual(colors[94], color94)
        self.assertEqual(colors[126], color126)

        # Sorted by time ASC
        colors = self.sql_controller.ui_get_colors_for_hike_sortby('time', self.picture)
        self.assertEqual(len(colors), 128)
        color0 = QColor(48, 52, 44)
        color94 = QColor(205, 199, 202)
        color126 = QColor(0, 0, 0)

        self.assertEqual(colors[0], color0)
        self.assertEqual(colors[94], color94)
        self.assertEqual(colors[126], color126)

    def test_ui_get_colors_for_hike(self):
        colors = self.sql_controller.ui_get_colors_for_archive_sortby('alt')
        self.assertEqual(len(colors), 1280)
        self.assertEqual(colors[94], QColor(100, 135, 219))

        colors = self.sql_controller.ui_get_colors_for_archive_sortby('color')
        self.assertEqual(len(colors), 1280)
        self.assertEqual(colors[94], QColor(37, 56, 45))

        colors = self.sql_controller.ui_get_colors_for_archive_sortby('time')
        self.assertEqual(len(colors), 1280)
        self.assertEqual(colors[94], QColor(141, 143, 149))

    # Time Bar
    def test_ui_get_percent_for_hike(self):
        self.assertEqual(self.picture.picture_id, 11994)
        self.assertEqual(self.picture.hike_id, 10)

        percent = self.sql_controller.ui_get_percentage_in_hike_with_mode('alt', self.picture)
        self.assertEqual(percent, 0.7939)
        percent = self.sql_controller.ui_get_percentage_in_hike_with_mode('color', self.picture)
        self.assertEqual(percent, 0.1022)
        percent = self.sql_controller.ui_get_percentage_in_hike_with_mode('time', self.picture)
        self.assertEqual(percent, 0.8422)

    def test_ui_get_percent_for_archive(self):
        self.assertEqual(self.picture.picture_id, 11994)
        self.assertEqual(self.picture.hike_id, 10)

        percent = self.sql_controller.ui_get_percentage_in_archive_with_mode('alt', self.picture)
        self.assertEqual(percent, 0.9759)
        percent = self.sql_controller.ui_get_percentage_in_archive_with_mode('color', self.picture)
        self.assertEqual(percent, 0.1585)
        percent = self.sql_controller.ui_get_percentage_in_archive_with_mode('time', self.picture)
        self.assertEqual(percent, 0.3840)


if __name__ == '__main__':
    print('Results of : projector_ui_database_test.py\n')
    unittest.main()
