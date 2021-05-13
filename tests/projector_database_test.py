#!/usr/bin/env python3

from typing import Any
from classes.capra_data_types import Picture, Hike
from classes.sql_controller import SQLController
from classes.sql_statements import SQLStatements
from PyQt5.QtGui import QColor
import unittest
import random


class DatabaseTest(unittest.TestCase):
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

    @classmethod
    def tearDownClass(self):
        self.sql_controller = None

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

        self.assertEqual(picture.camera1, 'capra-storage/hike3/878_cam1.jpg')
        self.assertEqual(picture.camera2, 'capra-storage/hike3/878_cam2.jpg')
        self.assertEqual(picture.camera3, 'capra-storage/hike3/878_cam3.jpg')
        self.assertEqual(picture.cameraf, 'capra-storage/hike3/878_cam2f.jpg')
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
        # id	time		hike	index_in_hike	id  (hike | index)
        # 1566	1556389800	3		450			--> 3353(4 | 79)
        # (451/2158) * 385 = 80
        pic = self.sql_controller.get_picture_with_id(1566)
        pic = self.sql_controller.get_next_time_skip_in_hikes(pic)
        self.assertEqual(pic.picture_id, 3353)

        # wrap around
        # 3353	1556399116	4		79			--> 185(1 | 184)
        # (80/385) * 892 = 185
        pic = self.sql_controller.get_next_time_skip_in_hikes(pic)
        self.assertEqual(pic.picture_id, 185)

        # 185   1556323940  1       184         --> 938(2 | 45)
        # (185/892) * 223 = 46
        pic = self.sql_controller.get_next_time_skip_in_hikes(pic)
        self.assertEqual(pic.picture_id, 938)

        # 938   1556377380  2       45          --> 1560(3 | 444)
        # (46/223) * 2158 = 445
        pic = self.sql_controller.get_next_time_skip_in_hikes(pic)
        self.assertEqual(pic.picture_id, 1560)

        # 3000  1556395536  3       1884        --> 3609 (4 | 335)
        # (1885/2158) * 385 = 336
        pic = self.sql_controller.get_picture_with_id(3000)
        pic = self.sql_controller.get_next_time_skip_in_hikes(pic)
        self.assertEqual(pic.picture_id, 3609)

    def test_get_previous_time_skip_in_hikes(self):
        # id	time		hike	index_in_hike	id  (hike | index)
        # 1566	1556389800	3		450	        <-- 938 (2 | 45)
        # (451/2158) * 223 = 46
        pic = self.sql_controller.get_picture_with_id(1566)
        pic = self.sql_controller.get_previous_time_skip_in_hikes(pic)
        self.assertEqual(pic.picture_id, 938)

        # 938	1556377380	2		45		    <-- 184 (1 | 183)
        # (46/223) * 892 = 184
        pic = self.sql_controller.get_previous_time_skip_in_hikes(pic)
        self.assertEqual(pic.picture_id, 184)

        # 184	1556323936	1		183		    <-- 3352 (4 | 77)
        # (184/892) * 385	= 78
        pic = self.sql_controller.get_previous_time_skip_in_hikes(pic)
        self.assertEqual(pic.picture_id, 3352)

        # 3654  1556400320  4       380        <-- 3244 (3 | 2134)
        # (381/385) * 2158 = 2135
        pic = self.sql_controller.get_picture_with_id(3654)
        pic = self.sql_controller.get_previous_time_skip_in_hikes(pic)
        self.assertEqual(pic.picture_id, 3250)

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
        # id	time		hike	color_rank_hike 	id (hike | color_rank_hike)
        # wrap around hike 1 to hike 4 (color_rank 4 --> 1)
        # 94    1556323576  1       772             --> 3508 (4 | 333)
        # (772/892) * 333
        pic = self.sql_controller.get_picture_with_id(94)
        pic = self.sql_controller.get_next_color_skip_in_hikes(pic)
        self.assertEqual(pic.picture_id, 3508)

        # hike 3 to hike 2 (colors_rank 2 --> 3)
        # 1994	1556391512	3		1776			--> 1084 (2 | 183)
        # (1776/2158) * 223
        pic = self.sql_controller.get_next_color_skip_in_hikes(self.picture)
        self.assertEqual(pic.picture_id, 1084)

        # hike 2 to hike 1 (colors_rank 3 --> 4)
        # 1109  1556378064  2       26              --> 479 (1 | 104)
        # (26/223) * 892 = 104
        pic = self.sql_controller.get_picture_with_id(1109)
        pic = self.sql_controller.get_next_color_skip_in_hikes(pic)
        self.assertEqual(pic.picture_id, 479)

    def test_get_previous_color_skip_in_hikes(self):
        # id	time		hike	color_rank_hike 	id (hike | color_rank_hike)
        # wrap to hike 4 to hike 1 (color_rank 1 --> 4)
        # 3388  1556399256  4       2               <-- 879 (1 | 4)
        # (2/385) * 892 = 4
        pic = self.sql_controller.get_picture_with_id(3388)
        pic = self.sql_controller.get_previous_color_skip_in_hikes(pic)
        self.assertEqual(pic.picture_id, 879)

        # hike 3 to hike 4 (colors_rank 2 --> 1)
        # 1994	1556391512	3		1776			<-- 3548 (4 | 316)
        # (1776/2158) * 385 = 316
        pic = self.sql_controller.get_previous_color_skip_in_hikes(self.picture)
        self.assertEqual(pic.picture_id, 3548)

        # hike 1 to hike 2 (color_rank 4 --> 3)
        # 882   1556326728  1       2               <-- x (2 | 0)
        # (2/892) * 223 = 0
        pic = self.sql_controller.get_picture_with_id(882)
        pic = self.sql_controller.get_previous_color_skip_in_hikes(pic)
        self.assertEqual(pic.picture_id, 1106)

        pic = self.sql_controller.get_picture_with_id(518)
        pic = self.sql_controller.get_previous_color_skip_in_hikes(pic)
        self.assertEqual(pic.picture_id, 1106)

        pic = self.sql_controller.get_picture_with_id(878)
        pic = self.sql_controller.get_previous_color_skip_in_hikes(pic)
        self.assertEqual(pic.picture_id, 1106)

        pic = self.sql_controller.get_picture_with_id(879)
        pic = self.sql_controller.get_previous_color_skip_in_hikes(pic)
        self.assertEqual(pic.picture_id, 1106)

        pic = self.sql_controller.get_picture_with_id(883)
        pic = self.sql_controller.get_previous_color_skip_in_hikes(pic)
        self.assertEqual(pic.picture_id, 1106)

        pic = self.sql_controller.get_picture_with_id(308)
        pic = self.sql_controller.get_previous_color_skip_in_hikes(pic)
        self.assertEqual(pic.picture_id, 1106)

        # when do we get to 1115 ?
        pic = self.sql_controller.get_picture_with_id(315)
        pic = self.sql_controller.get_previous_color_skip_in_hikes(pic)
        self.assertEqual(pic.picture_id, 1115)

        pic = self.sql_controller.get_picture_with_id(310)
        pic = self.sql_controller.get_previous_color_skip_in_hikes(pic)
        self.assertEqual(pic.picture_id, 1115)

        pic = self.sql_controller.get_picture_with_id(312)
        pic = self.sql_controller.get_previous_color_skip_in_hikes(pic)
        self.assertEqual(pic.picture_id, 1115)

        pic = self.sql_controller.get_picture_with_id(325)
        pic = self.sql_controller.get_previous_color_skip_in_hikes(pic)
        self.assertEqual(pic.picture_id, 1115)

        # Next
        pic = self.sql_controller.get_picture_with_id(332)
        pic = self.sql_controller.get_previous_color_skip_in_hikes(pic)
        self.assertEqual(pic.picture_id, 1067)

        # End of hike 1 via color that goes to rank 221
        # (887/892) * 223 = 221
        pic = self.sql_controller.get_picture_with_id(373)
        pic = self.sql_controller.get_previous_color_skip_in_hikes(pic)
        self.assertEqual(pic.picture_id, 1023)

        # End of hike 1 via color that goes to rank 222
        # (888/892) * 223 = 222
        pic = self.sql_controller.get_picture_with_id(9)
        pic = self.sql_controller.get_previous_color_skip_in_hikes(pic)
        self.assertEqual(pic.picture_id, 1024)

        pic = self.sql_controller.get_picture_with_id(386)
        pic = self.sql_controller.get_previous_color_skip_in_hikes(pic)
        self.assertEqual(pic.picture_id, 1024)

        pic = self.sql_controller.get_picture_with_id(1)
        pic = self.sql_controller.get_previous_color_skip_in_hikes(pic)
        self.assertEqual(pic.picture_id, 1024)

        pic = self.sql_controller.get_picture_with_id(143)
        pic = self.sql_controller.get_previous_color_skip_in_hikes(pic)
        self.assertEqual(pic.picture_id, 1024)

        # Goes to rank 223
        # (892/892) * 223 = 223
        pic = self.sql_controller.get_picture_with_id(873)
        pic = self.sql_controller.get_previous_color_skip_in_hikes(pic)
        self.assertEqual(pic.picture_id, 1044)

    def test_get_next_color_skip_in_global(self):
        pic = self.sql_controller.get_next_color_skip_in_global(self.picture)
        self.assertEqual(pic.colorrank_global, 2967)

        # bottom
        pic = self.sql_controller.get_picture_with_id(1220)  # 3640
        pic = self.sql_controller.get_next_color_skip_in_global(pic)
        self.assertEqual(pic.colorrank_global, 164)
        self.assertEqual(pic.picture_id, 2592)

    def test_get_previous_color_skip_in_global(self):
        pic = self.sql_controller.get_previous_color_skip_in_global(self.picture)
        self.assertEqual(pic.colorrank_global, 2603)

        # top
        pic = self.sql_controller.get_picture_with_id(310)  # 10
        pic = self.sql_controller.get_previous_color_skip_in_global(pic)
        self.assertEqual(pic.colorrank_global, 3486)
        self.assertEqual(pic.picture_id, 1792)


if __name__ == '__main__':
    print('Results of : projector_database_test.py\n')
    unittest.main()
