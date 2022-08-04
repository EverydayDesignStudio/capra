#!/usr/bin/env python3

from classes.capra_data_types import Picture, Hike
from classes.sql_controller import SQLController
from classes.sql_statements import SQLStatements
from PyQt5.QtGui import QColor
import unittest

print('⚠️  NOTE: To get these tests to run, you have to adjust the _execute_query() \n   \
in sql_controller.py to use _test_build_picture_from_row() instead.\n   \
This is due to updates that took place to the database, after the testing in this file was completed.\n')


# Tests for the merged database - May 2021
# Never got around to writing updated tests
# It would be useful, but also a lot of extra work, to write tests for
# the database logic on a large (> 10 hikes) and completely merged Database
class DatabaseMergedMayTests(unittest.TestCase):
    DB = 'tests/capra_projector_apr2021_min_test_full_merged.db'
    directory = 'capra-storage'
    sql_controller = None
    sql_statements = None
    picture = None

    @classmethod
    def setUpClass(self):
        # NOTE - if the database or id is changed, all the tests will break
        # They are dependent upon that
        self.sql_controller = SQLController(database=self.DB, directory=self.directory)
        self.picture = self.sql_controller.get_picture_with_id(11994)

        # For testing directly on the sql statements
        self.sql_statements = SQLStatements()


# Tests for the newer larger database version
class DatabaseMay2021Tests(unittest.TestCase):
    DB = 'tests/capra_projector_may2021.db'
    directory = 'capra-storage'
    sql_controller = None
    sql_statements = None
    picture = None

    @classmethod
    def setUpClass(self):
        # NOTE - if the database or id is changed, all the tests will break
        # They are dependent upon that
        self.sql_controller = SQLController(database=self.DB, directory=self.directory)
        self.picture = self.sql_controller.get_picture_with_id(11994)

        # For testing directly on the sql statements
        self.sql_statements = SQLStatements()

    def test_get_picture_with_id(self):
        self.assertEqual(self.picture.picture_id, 11994)
        self.assertEqual(self.picture.hike_id, 10)
        self.assertEqual(self.picture.altitude, 2123.5)

    # 20,284 total pictures in database
    # x  .05
    #  1,014.2  ->  rounds to 1,015 skip in the global ranks

    def test_get_next_color_skip_in_global(self):
        self.assertEqual(self.picture.picture_id, 11994)
        self.assertEqual(self.picture.colorrank_global, 10549)
        # id        color_rank_global
        # 11994     10549 + 1015
        pic = self.sql_controller.get_next_color_skip_in_global(self.picture)
        self.assertEqual(pic.colorrank_global, 11564)
        self.assertEqual(pic.picture_id, 1398)
        pic = self.sql_controller.get_next_color_skip_in_global(pic)
        self.assertEqual(pic.colorrank_global, 12579)
        pic = self.sql_controller.get_next_color_skip_in_global(pic)
        self.assertEqual(pic.colorrank_global, 13594)
        pic = self.sql_controller.get_next_color_skip_in_global(pic)
        pic = self.sql_controller.get_next_color_skip_in_global(pic)
        pic = self.sql_controller.get_next_color_skip_in_global(pic)
        pic = self.sql_controller.get_next_color_skip_in_global(pic)
        pic = self.sql_controller.get_next_color_skip_in_global(pic)
        pic = self.sql_controller.get_next_color_skip_in_global(pic)
        self.assertEqual(pic.colorrank_global, 19684)
        self.assertEqual(pic.picture_id, 30037)
        # wrap around
        pic = self.sql_controller.get_next_color_skip_in_global(pic)
        self.assertEqual(pic.colorrank_global, 415)
        self.assertEqual(pic.picture_id, 8493)

        # 4146      20284
        pic = self.sql_controller.get_picture_with_id(4146)
        pic = self.sql_controller.get_next_color_skip_in_global(pic)
        self.assertEqual(pic.colorrank_global, 1015)
        self.assertEqual(pic.picture_id, 10321)

        # 4887     19270
        pic = self.sql_controller.get_picture_with_id(4887)
        pic = self.sql_controller.get_next_color_skip_in_global(pic)
        self.assertEqual(pic.colorrank_global, 1)
        self.assertEqual(pic.picture_id, 1102)

    def test_get_previous_color_skip_in_global(self):
        self.assertEqual(self.picture.picture_id, 11994)
        self.assertEqual(self.picture.colorrank_global, 10549)
        # id        color_rank_global
        # 11994     10549 - 1015
        pic = self.sql_controller.get_previous_color_skip_in_global(self.picture)
        self.assertEqual(pic.colorrank_global, 9534)
        self.assertEqual(pic.picture_id, 29239)
        pic = self.sql_controller.get_previous_color_skip_in_global(pic)
        pic = self.sql_controller.get_previous_color_skip_in_global(pic)
        pic = self.sql_controller.get_previous_color_skip_in_global(pic)
        pic = self.sql_controller.get_previous_color_skip_in_global(pic)
        self.assertEqual(pic.colorrank_global, 5474)
        pic = self.sql_controller.get_previous_color_skip_in_global(pic)
        pic = self.sql_controller.get_previous_color_skip_in_global(pic)
        pic = self.sql_controller.get_previous_color_skip_in_global(pic)
        self.assertEqual(pic.colorrank_global, 2429)
        pic = self.sql_controller.get_previous_color_skip_in_global(pic)
        pic = self.sql_controller.get_previous_color_skip_in_global(pic)
        self.assertEqual(pic.colorrank_global, 399)
        # wrap back around
        pic = self.sql_controller.get_previous_color_skip_in_global(pic)
        self.assertEqual(pic.colorrank_global, 19668)
        self.assertEqual(pic.picture_id, 25289)

        # 8388      310
        pic = self.sql_controller.get_picture_with_id(8388)
        pic = self.sql_controller.get_previous_color_skip_in_global(pic)
        self.assertEqual(pic.colorrank_global, 19579)
        self.assertEqual(pic.picture_id, 6668)

        # 1102      1
        pic = self.sql_controller.get_picture_with_id(1102)
        pic = self.sql_controller.get_previous_color_skip_in_global(pic)
        self.assertEqual(pic.colorrank_global, 19270)
        self.assertEqual(pic.picture_id, 4887)

        # 10321     1015
        pic = self.sql_controller.get_picture_with_id(10321)
        pic = self.sql_controller.get_previous_color_skip_in_global(pic)
        self.assertEqual(pic.colorrank_global, 20284)
        self.assertEqual(pic.picture_id, 4146)


class DatabaseOriginal4Tests(unittest.TestCase):
    DB = 'tests/capra_projector_jan2021_min_test.db'  # no / infront makes the path relative
    directory = 'capra-storage'
    sql_controller = None
    sql_statements = None
    picture = None

    @classmethod
    def setUpClass(self):
        # NOTE - if the database or id is changed, all the tests will break
        # They are dependent upon that
        self.sql_controller = SQLController(database=self.DB, directory=self.directory)
        self.picture = self.sql_controller.get_picture_with_id(1994)

        # For testing directly on the sql statements
        self.sql_statements = SQLStatements()

    def test_get_picture_with_id(self):
        self.assertEqual(self.picture.picture_id, 1994)
        self.assertEqual(self.picture.altitude, 936.62)

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
        self.assertEqual(picture.index_in_hike, 878)

        self.assertEqual(picture.altitude, 936.62)
        self.assertEqual(picture.altrank_hike, 855)
        self.assertEqual(picture.altrank_global, 2355)
        self.assertEqual(picture.altrank_global_h, 1970)

        hsvColor = QColor()
        hsvColor.setHsv(91, 18, 220)
        self.assertEqual(picture.color_hsv, hsvColor)
        rgbColor = QColor(204, 219, 220)
        self.assertEqual(picture.color_rgb, rgbColor)
        self.assertEqual(picture.colorrank_hike, 1776)
        self.assertEqual(picture.colorrank_global, 2785)
        self.assertEqual(picture.colorrank_global_h, 2891)
        self.assertEqual(picture.colors_count, 4)
        colorList = [QColor(204, 219, 220), QColor(52, 46, 17),
                     QColor(122, 117, 75), QColor(17, 17, 15)]
        self.assertEqual(picture.colors_rgb, colorList)
        self.assertEqual(picture.colors_conf, [0.22, 0.18, 0.16, 0.11])

        self.assertEqual(picture.camera1, '/media/pi/capra-hd/hike3/878_cam1.jpg')
        self.assertEqual(picture.camera2, '/media/pi/capra-hd/hike3/878_cam2.jpg')
        self.assertEqual(picture.camera3, '/media/pi/capra-hd/hike3/878_cam3.jpg')
        self.assertEqual(picture.cameraf, '/media/pi/capra-hd/hike3/878_cam2f.jpg')
        self.assertEqual(picture.created, '2021-02-16 09:39:15')
        self.assertEqual(picture.updated, '2021-02-16 09:39:15')

    # Time
    # --------------------------------------------------------------------------

    def test_get_next_time_in_hikes(self):
        # next picture by 1
        pic = self.sql_controller.get_next_time_in_hikes(self.picture, 1)
        self.assertEqual(pic.time, 1556391516.0)
        self.assertEqual(pic.picture_id, 1995)

        # next picture by 94
        pic = self.sql_controller.get_next_time_in_hikes(self.picture, 94)
        self.assertEqual(pic.time, 1556391888.0)
        self.assertEqual(pic.picture_id, 2088)

        # next picture by enough to wrap it around
        pic = self.sql_controller.get_next_time_in_hikes(self.picture, 1674)
        self.assertEqual(pic.time, 1556323240.0)
        self.assertEqual(pic.picture_id, 10)

        # offset is more than total list size, but is below the row
        pic = self.sql_controller.get_next_time_in_hikes(self.picture, 27+3658)
        self.assertEqual(pic.time, 1556391620.0)
        self.assertEqual(pic.picture_id, 2021)

        # offset is more than total list size, but is above the row
        pic = self.sql_controller.get_next_time_in_hikes(self.picture, 1675+3658)
        self.assertEqual(pic.time, 1556323244.0)
        self.assertEqual(pic.picture_id, 11)

    def test_get_previous_time_in_hikes(self):
        # previous picture by 1
        pic = self.sql_controller.get_previous_time_in_hikes(self.picture, 1)
        self.assertEqual(pic.time, 1556391508.0)
        self.assertEqual(pic.picture_id, 1993)

        # previous picture by 94
        pic = self.sql_controller.get_previous_time_in_hikes(self.picture, 94)
        self.assertEqual(pic.time, 1556391136.0)
        self.assertEqual(pic.picture_id, 1900)

        # previous picture by enough to wrap it around
        pic = self.sql_controller.get_previous_time_in_hikes(self.picture, 1994)
        self.assertEqual(pic.time, 1556400336.0)
        self.assertEqual(pic.picture_id, 3658)

        pic = self.sql_controller.get_previous_time_in_hikes(self.picture, 2021)
        self.assertEqual(pic.time, 1556400228.0)
        self.assertEqual(pic.picture_id, 3631)

        # offset is more than total list size, but is above the row
        pic = self.sql_controller.get_previous_time_in_hikes(self.picture, 11+3658)
        self.assertEqual(pic.time, 1556391468.0)
        self.assertEqual(pic.picture_id, 1983)

        # offset is more than total list size, but is below the row
        pic = self.sql_controller.get_previous_time_in_hikes(self.picture, 2000+3658)
        self.assertEqual(pic.time, 1556400312.0)
        self.assertEqual(pic.picture_id, 3652)

    def test_get_next_time_in_global(self):
        # in minute
        pic = self.sql_controller.get_next_time_in_global(self.picture, 1)
        self.assertEqual(pic.picture_id, 1995)

        pic = self.sql_controller.get_next_time_in_global(self.picture, 6)
        self.assertEqual(pic.picture_id, 2000)

        # below
        pic = self.sql_controller.get_next_time_in_global(self.picture, 7)
        self.assertEqual(pic.picture_id, 2001)

        pic = self.sql_controller.get_next_time_in_global(self.picture, 2556)
        self.assertEqual(pic.picture_id, 892)

        # wrap around
        pic = self.sql_controller.get_next_time_in_global(self.picture, 2557)
        self.assertEqual(pic.picture_id, 893)

        pic = self.sql_controller.get_next_time_in_global(self.picture, 3657)
        self.assertEqual(pic.picture_id, 1993)

        # moding below
        pic = self.sql_controller.get_next_time_in_global(self.picture, 3659)
        self.assertEqual(pic.picture_id, 1995)

        pic = self.sql_controller.get_next_time_in_global(self.picture, 3668)
        self.assertEqual(pic.picture_id, 2004)

        # moding above
        pic = self.sql_controller.get_next_time_in_global(self.picture, 6216)
        self.assertEqual(pic.picture_id, 894)

        pic = self.sql_controller.get_next_time_in_global(self.picture, 6714)
        self.assertEqual(pic.picture_id, 1392)

    def test_get_previous_time_in_global(self):
        # in minute
        pic = self.sql_controller.get_previous_time_in_global(self.picture, 1)
        self.assertEqual(pic.picture_id, 1993)

        pic = self.sql_controller.get_previous_time_in_global(self.picture, 8)
        self.assertEqual(pic.picture_id, 1986)

        # above
        pic = self.sql_controller.get_previous_time_in_global(self.picture, 9)
        self.assertEqual(pic.picture_id, 1985)

        pic = self.sql_controller.get_previous_time_in_global(self.picture, 834)
        self.assertEqual(pic.picture_id, 1160)

        pic = self.sql_controller.get_previous_time_in_global(self.picture, 1101)
        self.assertEqual(pic.picture_id, 893)

        # wrap around above
        pic = self.sql_controller.get_previous_time_in_global(self.picture, 1102)
        self.assertEqual(pic.picture_id, 892)

        # wrap around below
        pic = self.sql_controller.get_previous_time_in_global(self.picture, 1800)
        self.assertEqual(pic.picture_id, 194)

        # moding above
        pic = self.sql_controller.get_previous_time_in_global(self.picture, 3659)
        self.assertEqual(pic.picture_id, 1993)

        pic = self.sql_controller.get_previous_time_in_global(self.picture, 3668)
        self.assertEqual(pic.picture_id, 1984)

        # moding below
        pic = self.sql_controller.get_previous_time_in_global(self.picture, 7116)
        self.assertEqual(pic.picture_id, 2194)

    def test_get_next_time_skip_in_hikes(self):
        # id	time		hike	index_in_hike	(hike | index) = id
        # 1566	1556389800	3		450			--> (4 | 80) = 3354
        # (451/2158) * 385 = 80.46 (ceiling then subtract 1)
        pic = self.sql_controller.get_picture_with_id(1566)
        pic = self.sql_controller.get_next_time_skip_in_hikes(pic)
        self.assertEqual(pic.picture_id, 3354)

        # wrap around
        # 3354	1556399120	4		80			--> (1 | 187) = 188
        # (81/385) * 892 = 187.66
        pic = self.sql_controller.get_next_time_skip_in_hikes(pic)
        self.assertEqual(pic.picture_id, 188)

        # 188   1556323952  1       187         --> (2 | 46) = 939
        # (188/892) * 223 = 47.0
        pic = self.sql_controller.get_next_time_skip_in_hikes(pic)
        self.assertEqual(pic.picture_id, 939)

        # 939   1556377384  2       46          --> (3 | 454) = 1570
        # (47/223) * 2158 = 454.8
        pic = self.sql_controller.get_next_time_skip_in_hikes(pic)
        self.assertEqual(pic.picture_id, 1570)

        # 3000  1556395536  3       1884        --> (4 | 336) = 3610
        # (1885/2158) * 385 = 336.29
        pic = self.sql_controller.get_picture_with_id(3000)
        pic = self.sql_controller.get_next_time_skip_in_hikes(pic)
        self.assertEqual(pic.picture_id, 3610)

    def test_get_previous_time_skip_in_hikes(self):
        # id	time		hike	index_in_hike   (hike | index) = id
        # 1566	1556389800	3		450	        --> (2 | 46) = 939
        # (451/2158) * 223 = 46.6
        pic = self.sql_controller.get_picture_with_id(1566)
        pic = self.sql_controller.get_previous_time_skip_in_hikes(pic)
        self.assertEqual(pic.picture_id, 939)

        # 939	1556377384	2		46		    --> (1 | 187) = 188
        # (47/223) * 892 = 188.0
        pic = self.sql_controller.get_previous_time_skip_in_hikes(pic)
        self.assertEqual(pic.picture_id, 188)

        # 188	1556323952	1		187		    --> (4 | 81) = 3355
        # (188/892) * 385	= 81.14
        pic = self.sql_controller.get_previous_time_skip_in_hikes(pic)
        self.assertEqual(pic.picture_id, 3355)

        # 3654  1556400320  4       380        --> (3 | 2135) = 3251
        # (381/385) * 2158 = 2135.58
        pic = self.sql_controller.get_picture_with_id(3654)
        pic = self.sql_controller.get_previous_time_skip_in_hikes(pic)
        self.assertEqual(pic.picture_id, 3251)

    def test_get_next_time_skip_in_global(self):
        # id    time        minute      id
        # 1994  1556391512  718 -> 733  2219
        # 2000  1556391536  718	-> 733  2225
        pic = self.sql_controller.get_next_time_skip_in_global(self.picture)
        self.assertEqual(pic.picture_id, 2219)

        pic = self.sql_controller.get_picture_with_id(2000)
        pic = self.sql_controller.get_next_time_skip_in_global(pic)
        self.assertEqual(pic.picture_id, 2225)

        # id    time        minute          id
        # 650   1556325800  1063 -> 1078    875
        # 688   1556325952  1065 -> 1080    906
        # 872   1556326688  1078 -> 493    1090
        # 885   1556326740  1079 -> 494    1103
        pic = self.sql_controller.get_picture_with_id(650)
        pic = self.sql_controller.get_next_time_skip_in_global(pic)
        self.assertEqual(pic.picture_id, 875)

        pic = self.sql_controller.get_picture_with_id(688)
        pic = self.sql_controller.get_next_time_skip_in_global(pic)
        self.assertEqual(pic.picture_id, 906)

        pic = self.sql_controller.get_picture_with_id(872)
        pic = self.sql_controller.get_next_time_skip_in_global(pic)
        self.assertEqual(pic.picture_id, 1090)

        pic = self.sql_controller.get_picture_with_id(885)
        pic = self.sql_controller.get_next_time_skip_in_global(pic)
        self.assertEqual(pic.picture_id, 1103)

    def test_get_previous_time_skip_in_global(self):
        # id    time        minute          id
        # 1994  1556391512  718 -> 703      1769
        # 1769  1556390612  703 -> 688      1544
        pic = self.sql_controller.get_previous_time_skip_in_global(self.picture)
        self.assertEqual(pic.picture_id, 1769)

        pic = self.sql_controller.get_previous_time_skip_in_global(pic)
        self.assertEqual(pic.picture_id, 1544)

        # id    time        minute          id
        # 1135  1556388076  661 -> 481      912
        # 912   1556377276  481 -> 1066     694
        pic = self.sql_controller.get_picture_with_id(1135)
        pic = self.sql_controller.get_previous_time_skip_in_global(pic)
        self.assertEqual(pic.picture_id, 912)

        # wrap arounds
        pic = self.sql_controller.get_previous_time_skip_in_global(pic)
        self.assertEqual(pic.picture_id, 694)

        # 1050  1556377828  490 -> 1075     832
        pic = self.sql_controller.get_picture_with_id(1056)
        pic = self.sql_controller.get_previous_time_skip_in_global(pic)
        self.assertEqual(pic.picture_id, 838)

    # Altitude
    # --------------------------------------------------------------------------
    def test_get_next_altitude_in_hikes(self):
        # forward by 1
        pic = self.sql_controller.get_next_altitude_in_hikes(self.picture, 1)
        self.assertEqual(pic.altrank_global_h, 1971)

        # forward by 94
        pic = self.sql_controller.get_next_altitude_in_hikes(pic, 94)
        self.assertEqual(pic.altrank_global_h, 2065)

        # wrap to top of list
        pic = self.sql_controller.get_picture_with_id(3274)
        pic = self.sql_controller.get_next_altitude_in_hikes(pic, 2)
        self.assertEqual(pic.altrank_global_h, 1)

        # mod to row below
        pic = self.sql_controller.get_next_altitude_in_hikes(self.picture, 6+3658)
        self.assertEqual(pic.picture_id, 1987)

        # mod to row above
        pic = self.sql_controller.get_next_altitude_in_hikes(self.picture, 3600+3658)
        self.assertEqual(pic.picture_id, 1912)

    def test_get_previous_altitude_in_hikes(self):
        # backward by 1
        pic = self.sql_controller.get_previous_altitude_in_hikes(self.picture, 1)
        self.assertEqual(pic.altrank_global_h, 1969)

        # backward by 94
        pic = self.sql_controller.get_previous_altitude_in_hikes(self.picture, 94)
        self.assertEqual(pic.altrank_global_h, 1876)

        # wrap to bottom of list
        pic = self.sql_controller.get_picture_with_id(592)
        pic = self.sql_controller.get_previous_altitude_in_hikes(pic, 6)
        self.assertEqual(pic.picture_id, 3276)

        # mod to row above
        pic = self.sql_controller.get_previous_altitude_in_hikes(self.picture, 10+3658)
        self.assertEqual(pic.altrank_global_h, 1960)

        # mod to row below
        pic = self.sql_controller.get_previous_altitude_in_hikes(self.picture, 2000+3658)
        self.assertEqual(pic.altrank_global_h, 3628)

    def test_get_next_altitude_in_global(self):
        # forward by 1
        pic = self.sql_controller.get_next_altitude_in_global(self.picture, 1)
        self.assertEqual(pic.altrank_global, 2356)

        # forward by 3
        pic = self.sql_controller.get_next_altitude_in_global(self.picture, 3)
        self.assertEqual(pic.altrank_global, 2358)

        # wrap to top of list
        pic = self.sql_controller.get_picture_with_id(2976)
        pic = self.sql_controller.get_next_altitude_in_global(pic, 1)
        self.assertEqual(pic.picture_id, 524)

        # mod to row below
        pic = self.sql_controller.get_next_altitude_in_global(self.picture, 100+3658)
        self.assertEqual(pic.altrank_global, 2455)

        # mod to row above
        pic = self.sql_controller.get_next_altitude_in_global(self.picture, 2000+3658)
        self.assertEqual(pic.altrank_global, 697)

    def test_get_previous_altitude_in_global(self):
        # previous by 1
        pic = self.sql_controller.get_previous_altitude_in_global(self.picture, 1)
        self.assertEqual(pic.altrank_global, 2354)

        # previous by 3
        pic = self.sql_controller.get_previous_altitude_in_global(self.picture, 3)
        self.assertEqual(pic.altrank_global, 2352)

        # wrap to bottom of list
        pic = self.sql_controller.get_picture_with_id(544)
        pic = self.sql_controller.get_previous_altitude_in_global(pic, 3)
        self.assertEqual(pic.picture_id, 3032)

        # mod to row above
        pic = self.sql_controller.get_previous_altitude_in_global(self.picture, 100+3658)
        self.assertEqual(pic.altrank_global, 2255)

        # mod to row below
        pic = self.sql_controller.get_previous_altitude_in_global(self.picture, 2360+3658)
        self.assertEqual(pic.altrank_global, 3653)

    def test_get_next_altitude_skip_in_hikes(self):
        # id	time		hike	alt_rank_hike	id (hike | alt_rank_hike)
        # wrap around
        # 1994	1556391512	3		855				--> 707 (1 | 354)
        # (855/2158) * 892 = 353.41
        pic = self.sql_controller.get_next_altitude_skip_in_hikes(self.picture)
        self.assertEqual(pic.picture_id, 707)

        # 1094	1556378004	2		47				--> 3577 (4 | 82)
        # (47/223) * 385 = 81.14
        pic = self.sql_controller.get_picture_with_id(1094)
        pic = self.sql_controller.get_next_altitude_skip_in_hikes(pic)
        self.assertEqual(pic.picture_id, 3577)

        # 34	1556323336	1		800				--> 938 (2 | 200)
        # (800/892) * 223 = 200.0
        pic = self.sql_controller.get_picture_with_id(34)
        pic = self.sql_controller.get_next_altitude_skip_in_hikes(pic)
        self.assertEqual(pic.picture_id, 938)

        # Testing the lower edge
        # ---------------------------------
        # 524   1556325296  1       1               --> 1048 (2 | 1)
        # (1/892) * 223 = 0.25
        pic = self.sql_controller.get_picture_with_id(524)
        pic = self.sql_controller.get_next_altitude_skip_in_hikes(pic)
        self.assertEqual(pic.picture_id, 1048)

        # 563   1556325452  1       3               --> 1048 (2 | 1)
        # (3/892) * 223 = 0.75
        pic = self.sql_controller.get_picture_with_id(563)
        pic = self.sql_controller.get_next_altitude_skip_in_hikes(pic)
        self.assertEqual(pic.picture_id, 1048)

        # 592   1556325568  1       4               --> 1048 (2 | 1)
        # (4/892) * 223 = 1.0
        pic = self.sql_controller.get_picture_with_id(592)
        pic = self.sql_controller.get_next_altitude_skip_in_hikes(pic)
        self.assertEqual(pic.picture_id, 1048)

        # 594   1556325576  1       5               --> 1078 (2 | 2)
        # (5/892) * 223 = 1.25
        pic = self.sql_controller.get_picture_with_id(594)
        pic = self.sql_controller.get_next_altitude_skip_in_hikes(pic)
        self.assertEqual(pic.picture_id, 1078)

        # 595   1556325580  1       6               --> 1078 (2 | 2)
        # (6/892) * 223 = 1.5
        pic = self.sql_controller.get_picture_with_id(595)
        pic = self.sql_controller.get_next_altitude_skip_in_hikes(pic)
        self.assertEqual(pic.picture_id, 1078)

        # 2    1556323208  1       891             --> 912 (2 | 223)
        # (891/892) * 223 = 222.75
        pic = self.sql_controller.get_picture_with_id(2)
        pic = self.sql_controller.get_next_altitude_skip_in_hikes(pic)
        self.assertEqual(pic.picture_id, 912)

        # 3658  1556400336  4       1               --> 1124 (3 | 6)
        # (1/384) * 2158 = 5.62
        pic = self.sql_controller.get_picture_with_id(3658)
        pic = self.sql_controller.get_next_altitude_skip_in_hikes(pic)
        self.assertEqual(pic.picture_id, 1125)

        # 3274	1556398800	4		384				--> 3033 (3 | 2153)
        # (384/385) * 2158 = 2152.39
        pic = self.sql_controller.get_picture_with_id(3274)
        pic = self.sql_controller.get_next_altitude_skip_in_hikes(pic)
        self.assertEqual(pic.picture_id, 3033)

        # 3275	1556398804	4		385				--> 2976 (3 | 2158)
        # (385/385) * 2158 = 2158.0
        pic = self.sql_controller.get_picture_with_id(3275)
        pic = self.sql_controller.get_next_altitude_skip_in_hikes(pic)
        self.assertEqual(pic.picture_id, 2976)

    def test_get_previous_altitude_skip_in_hikes(self):
        # id	time		hike	alt_rank_hike	id (hike | alt_rank_hike)

        # wrap back to hike 3
        # -------------------
        # 619	1556325676	1		26				--> 1228 (3 | 63)
        # (26/892) * 2158 = 62.9
        pic = self.sql_controller.get_picture_with_id(619)
        pic = self.sql_controller.get_previous_altitude_skip_in_hikes(pic)
        self.assertEqual(pic.picture_id, 1228)

        # 2	    1556323208	1		891				--> 3036 (3 | 2156)
        # (891/892) * 2158 = 2155.58
        pic = self.sql_controller.get_picture_with_id(2)
        pic = self.sql_controller.get_previous_altitude_skip_in_hikes(pic)
        self.assertEqual(pic.picture_id, 3036)

        # -------------------
        # 1017	1556377696	2		210				--> 49 (1 | 840)
        # (210/223) * 892 = 840.0
        pic = self.sql_controller.get_picture_with_id(1017)
        pic = self.sql_controller.get_previous_altitude_skip_in_hikes(pic)
        self.assertEqual(pic.picture_id, 49)

        # 1994	1556391512	3		855				--> 3507 (4 | 153)
        # (855/2158) * 385 = 152.537
        pic = self.sql_controller.get_previous_altitude_skip_in_hikes(self.picture)
        self.assertEqual(pic.picture_id, 3507)

        # 1127	1556388044	3		10				--> 3657 (4 | 2)
        # (10/2158) * 223 = 1.03
        pic = self.sql_controller.get_picture_with_id(1127)
        pic = self.sql_controller.get_previous_altitude_skip_in_hikes(pic)
        self.assertEqual(pic.picture_id, 3657)

    def test_get_next_altitude_skip_in_global(self):
        # 1994  |   2355 + (3658 * .05) = 2537.9
        pic = self.sql_controller.get_next_altitude_skip_in_global(self.picture)
        self.assertEqual(pic.altrank_global, 2538)
        self.assertEqual(pic.picture_id, 2207)

        # 524   |   1 + (3658 * .05) = 183.9
        pic = self.sql_controller.get_picture_with_id(524)
        pic = self.sql_controller.get_next_altitude_skip_in_global(pic)
        self.assertEqual(pic.altrank_global, 184)
        self.assertEqual(pic.picture_id, 514)  # 183

        # 3006  | 3475 + (3658 * .05) = 3657.9
        pic = self.sql_controller.get_picture_with_id(3006)
        pic = self.sql_controller.get_next_altitude_skip_in_global(pic)
        self.assertEqual(pic.altrank_global, 3658)

        # wrap around bottom to the top
        # ------------------------------------
        # 3059  | 3476 + (3658 * .05) = 3658.9
        pic = self.sql_controller.get_picture_with_id(3059)
        pic = self.sql_controller.get_next_altitude_skip_in_global(pic)
        self.assertEqual(pic.altrank_global, 1)

        # 2973  | 3600 + (3658 * .05) = 3782.9
        pic = self.sql_controller.get_picture_with_id(2973)
        pic = self.sql_controller.get_next_altitude_skip_in_global(pic)
        self.assertEqual(pic.altrank_global, 125)
        self.assertEqual(pic.picture_id, 455)

    def test_get_previous_altitude_skip_in_global(self):
        # 1994  |   2355 - (3658 * .05)
        # 2355 - 183 = 2172
        pic = self.sql_controller.get_previous_altitude_skip_in_global(self.picture)
        self.assertEqual(pic.altrank_global, 2172)

        # 3489  | 1800 - (3658 * .05)
        # 1800 - 183 = 1617
        pic = self.sql_controller.get_picture_with_id(3489)
        pic = self.sql_controller.get_previous_altitude_skip_in_global(pic)
        self.assertEqual(pic.altrank_global, 1617)

        # 2976   |   3658 - (3658 * .05)
        # 3658 - 183 = 3475
        pic = self.sql_controller.get_picture_with_id(2976)
        pic = self.sql_controller.get_previous_altitude_skip_in_global(pic)
        self.assertEqual(pic.altrank_global, 3475)
        self.assertEqual(pic.picture_id, 3006)

        # wrap around from top to the bottom
        # ------------------------------------
        # 613   |   20 - (3658 * .05) + 3658
        # 20 - 183 + 3658 = 3495
        pic = self.sql_controller.get_picture_with_id(613)  # 20 rank
        pic = self.sql_controller.get_previous_altitude_skip_in_global(pic)
        self.assertEqual(pic.altrank_global, 3495)
        self.assertEqual(pic.picture_id, 3056)

        # 513   |   183 - (3658 * .05) + 3658
        # 183 - 183 + 3658 = 3658
        pic = self.sql_controller.get_picture_with_id(513)
        pic = self.sql_controller.get_previous_altitude_skip_in_global(pic)
        self.assertEqual(pic.altrank_global, 3658)
        self.assertEqual(pic.picture_id, 2976)

    # Color
    # --------------------------------------------------------------------------
    def test_get_next_color_in_hikes(self):
        # forward by 1
        pic = self.sql_controller.get_next_color_in_hikes(self.picture, 1)
        self.assertEqual(pic.colorrank_global_h, 2892)

        # forward by 2
        pic = self.sql_controller.get_next_color_in_hikes(self.picture, 2)
        self.assertEqual(pic.colorrank_global_h, 2893)

        # wrap to top of list
        pic = self.sql_controller.get_picture_with_id(3369)
        pic = self.sql_controller.get_next_color_in_hikes(pic, 8)
        self.assertEqual(pic.picture_id, 883)

        # mod to row below
        pic = self.sql_controller.get_next_color_in_hikes(self.picture, 9+3658)
        self.assertEqual(pic.colorrank_global_h, 2900)

        # mod to row above
        pic = self.sql_controller.get_next_color_in_hikes(self.picture, 800+3658)
        self.assertEqual(pic.colorrank_global_h, 33)

    def test_get_previous_color_in_hikes(self):
        # backward by 1
        pic = self.sql_controller.get_previous_color_in_hikes(self.picture, 1)
        self.assertEqual(pic.colorrank_global_h, 2890)

        # backward by 5
        pic = self.sql_controller.get_previous_color_in_hikes(self.picture, 5)
        self.assertEqual(pic.colorrank_global_h, 2886)

        # wrap to bottom of list
        pic = self.sql_controller.get_picture_with_id(341)
        pic = self.sql_controller.get_previous_color_in_hikes(pic, 25)
        self.assertEqual(pic.picture_id, 3482)
        self.assertEqual(pic.colorrank_global_h, 3658)

        # mod to row above
        pic = self.sql_controller.get_previous_color_in_hikes(self.picture, 891+3658)
        self.assertEqual(pic.colorrank_global_h, 2000)

        # mod to row below
        pic = self.sql_controller.get_previous_color_in_hikes(self.picture, 2900+3658)
        self.assertEqual(pic.colorrank_global_h, 3649)

    def test_get_next_color_in_global(self):
        # forward by 1
        pic = self.sql_controller.get_next_color_in_global(self.picture, 1)
        self.assertEqual(pic.colorrank_global, 2786)

        # forward by 10
        pic = self.sql_controller.get_next_color_in_global(self.picture, 10)
        self.assertEqual(pic.colorrank_global, 2795)

        # wrap to top of list
        pic = self.sql_controller.get_picture_with_id(3482)
        pic = self.sql_controller.get_next_color_in_global(pic, 4)
        self.assertEqual(pic.picture_id, 518)
        self.assertEqual(pic.colorrank_global, 1)

        # mod to row below
        pic = self.sql_controller.get_next_color_in_global(self.picture, 500+3658)
        self.assertEqual(pic.colorrank_global, 3285)

        # mod to row above
        pic = self.sql_controller.get_next_color_in_global(self.picture, 900+3658)
        self.assertEqual(pic.colorrank_global, 27)

    def test_get_previous_color_in_global(self):
        # backward by 1
        pic = self.sql_controller.get_previous_color_in_global(self.picture, 1)
        self.assertEqual(pic.colorrank_global, 2784)

        # backward by 10
        pic = self.sql_controller.get_previous_color_in_global(self.picture, 10)
        self.assertEqual(pic.colorrank_global, 2775)

        # wrap to bottom of list
        pic = self.sql_controller.get_picture_with_id(882)
        pic = self.sql_controller.get_previous_color_in_global(pic, 2)
        self.assertEqual(pic.picture_id, 873)
        self.assertEqual(pic.colorrank_global, 3658)

        # mod to row above
        pic = self.sql_controller.get_previous_color_in_global(self.picture, 500+3658)
        self.assertEqual(pic.colorrank_global, 2285)

        # mod to row below
        pic = self.sql_controller.get_previous_color_in_global(self.picture, 2800+3658)
        self.assertEqual(pic.colorrank_global, 3643)

    def test_get_next_color_skip_in_hikes(self):
        # id	hike	color_rank_hike 	id (hike | color_rank_hike)
        # wrap around hike 1 to hike 4 (color_rank 4 --> 1)
        # 94    1       772             --> 3508 (4 | 334)
        # (772/892) * 385 = 333.2
        pic = self.sql_controller.get_picture_with_id(94)
        pic = self.sql_controller.get_next_color_skip_in_hikes(pic)
        self.assertEqual(pic.picture_id, 3304)

        # hike 3 to hike 2 (colors_rank 2 --> 3)
        # 1994  3		1776			--> 1084 (2 | 183)
        # (1776/2158) * 223 = 183.53
        pic = self.sql_controller.get_next_color_skip_in_hikes(self.picture)
        self.assertEqual(pic.picture_id, 1087)

        # hike 2 to hike 1 (colors_rank 3 --> 4)
        # 1109  2       26              --> 479 (1 | 104)
        # (26/223) * 892 = 104.0
        pic = self.sql_controller.get_picture_with_id(1109)
        pic = self.sql_controller.get_next_color_skip_in_hikes(pic)
        self.assertEqual(pic.picture_id, 479)

    def test_get_previous_color_skip_in_hikes(self):
        # id	hike	color_rank_hike 	id (hike | color_rank_hike)
        # wrap to hike 4 to hike 1 (color_rank 1 --> 4)
        # 3388  4       2               <-- 883 (1 | 5)
        # (2/385) * 892 = 4.63
        pic = self.sql_controller.get_picture_with_id(3388)
        pic = self.sql_controller.get_previous_color_skip_in_hikes(pic)
        self.assertEqual(pic.picture_id, 883)

        # hike 3 to hike 4 (colors_rank 2 --> 1)
        # 1994  3		1776			<-- 3522 (4 | 317)
        # (1776/2158) * 385 = 316.85
        pic = self.sql_controller.get_previous_color_skip_in_hikes(self.picture)
        self.assertEqual(pic.picture_id, 3522)

        # hike 1 to hike 2 (color_rank 4 --> 3)
        # (1/892) * 223 = 0.25
        pic = self.sql_controller.get_picture_with_id(518)
        pic = self.sql_controller.get_previous_color_skip_in_hikes(pic)
        self.assertEqual(pic.picture_id, 1106)

        # (2/892) * 223 = 0.5
        pic = self.sql_controller.get_picture_with_id(882)
        pic = self.sql_controller.get_previous_color_skip_in_hikes(pic)
        self.assertEqual(pic.picture_id, 1106)

        # (3/892) * 223 = 0.75
        pic = self.sql_controller.get_picture_with_id(878)
        pic = self.sql_controller.get_previous_color_skip_in_hikes(pic)
        self.assertEqual(pic.picture_id, 1106)

        # (4/892) * 223 = 1.0
        pic = self.sql_controller.get_picture_with_id(879)
        pic = self.sql_controller.get_previous_color_skip_in_hikes(pic)
        self.assertEqual(pic.picture_id, 1106)

        # (5/892) * 223 = 1.25
        pic = self.sql_controller.get_picture_with_id(883)
        pic = self.sql_controller.get_previous_color_skip_in_hikes(pic)
        self.assertEqual(pic.picture_id, 1115)

        # (7/892) * 223 = 1.75
        pic = self.sql_controller.get_picture_with_id(308)
        pic = self.sql_controller.get_previous_color_skip_in_hikes(pic)
        self.assertEqual(pic.picture_id, 1115)

        # (8/892) * 223 = 2.0
        pic = self.sql_controller.get_picture_with_id(315)
        pic = self.sql_controller.get_previous_color_skip_in_hikes(pic)
        self.assertEqual(pic.picture_id, 1115)

        # (9/892) * 223 = 2.25
        pic = self.sql_controller.get_picture_with_id(310)
        pic = self.sql_controller.get_previous_color_skip_in_hikes(pic)
        self.assertEqual(pic.picture_id, 1067)

        # (10/892) * 223 = 2.5
        pic = self.sql_controller.get_picture_with_id(312)
        pic = self.sql_controller.get_previous_color_skip_in_hikes(pic)
        self.assertEqual(pic.picture_id, 1067)

        # (11/892) * 223 = 2.75
        pic = self.sql_controller.get_picture_with_id(325)
        pic = self.sql_controller.get_previous_color_skip_in_hikes(pic)
        self.assertEqual(pic.picture_id, 1067)

        # (12/892) * 223 = 3.0
        pic = self.sql_controller.get_picture_with_id(332)
        pic = self.sql_controller.get_previous_color_skip_in_hikes(pic)
        self.assertEqual(pic.picture_id, 1067)

        # End of hike 1
        # (887/892) * 223 = 221.75
        pic = self.sql_controller.get_picture_with_id(373)
        pic = self.sql_controller.get_previous_color_skip_in_hikes(pic)
        self.assertEqual(pic.picture_id, 1024)

        # (888/892) * 223 = 222.0
        pic = self.sql_controller.get_picture_with_id(9)
        pic = self.sql_controller.get_previous_color_skip_in_hikes(pic)
        self.assertEqual(pic.picture_id, 1024)

        # (889/892) * 223 = 222.25
        pic = self.sql_controller.get_picture_with_id(386)
        pic = self.sql_controller.get_previous_color_skip_in_hikes(pic)
        self.assertEqual(pic.picture_id, 1044)

        # (890/892) * 223 = 222.5
        pic = self.sql_controller.get_picture_with_id(1)
        pic = self.sql_controller.get_previous_color_skip_in_hikes(pic)
        self.assertEqual(pic.picture_id, 1044)

        # (891/892) * 223 = 222.75
        pic = self.sql_controller.get_picture_with_id(143)
        pic = self.sql_controller.get_previous_color_skip_in_hikes(pic)
        self.assertEqual(pic.picture_id, 1044)

        # (892/892) * 223 = 223.0
        pic = self.sql_controller.get_picture_with_id(873)
        pic = self.sql_controller.get_previous_color_skip_in_hikes(pic)
        self.assertEqual(pic.picture_id, 1044)

    def test_get_next_color_skip_in_global(self):
        pic = self.sql_controller.get_next_color_skip_in_global(self.picture)
        self.assertEqual(pic.colorrank_global, 2968)

        # bottom
        pic = self.sql_controller.get_picture_with_id(1220)  # 3640
        pic = self.sql_controller.get_next_color_skip_in_global(pic)
        self.assertEqual(pic.colorrank_global, 165)
        self.assertEqual(pic.picture_id, 2594)

    def test_get_previous_color_skip_in_global(self):
        pic = self.sql_controller.get_previous_color_skip_in_global(self.picture)
        self.assertEqual(pic.colorrank_global, 2602)

        # top
        pic = self.sql_controller.get_picture_with_id(310)  # 10
        pic = self.sql_controller.get_previous_color_skip_in_global(pic)
        self.assertEqual(pic.colorrank_global, 3485)
        self.assertEqual(pic.picture_id, 1798)


if __name__ == '__main__':
    print('Results of : projector_database_test.py\n')
    unittest.main()
