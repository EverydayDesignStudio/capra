#!/usr/bin/env python3

from typing import Any
from classes.capra_data_types import Picture, Hike
from classes.sql_controller import SQLController
from classes.sql_statements import SQLStatements
import unittest
import random


class DatabaseTest(unittest.TestCase):
    DB = 'capra-storage/capra_projector_jan2021_min_test.db'  # no / infront makes the path relative
    sql_controller = None
    sql_statements = None
    picture = None

    @classmethod
    def setUpClass(self):
        # NOTE - if the database or id is changed, all the tests will break
        # They are dependent upon that
        self.sql_controller = SQLController(database=self.DB)
        self.picture = self.sql_controller.get_picture_with_id(1994)

        # For testing directly on the sql statements
        self.sql_statements = SQLStatements()

    @classmethod
    def tearDownClass(self):
        self.sql_controller = None

    # --------------------------------------------------------------------------

    def test_get_picture_with_id(self):
        self.assertEqual(self.picture.picture_id, 1994)
        self.assertEqual(self.picture.altitude, 936.62)

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

        # moding
        pic = self.sql_controller.get_next_time_in_global(self.picture, 3659)
        self.assertEqual(pic.picture_id, 1995)

        pic = self.sql_controller.get_next_time_in_global(self.picture, 3668)
        self.assertEqual(pic.picture_id, 2004)

        pic = self.sql_controller.get_next_time_in_global(self.picture, 6216)
        self.assertEqual(pic.picture_id, 894)

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

        # wrap around
        pic = self.sql_controller.get_previous_time_in_global(self.picture, 1102)
        self.assertEqual(pic.picture_id, 892)

        pic = self.sql_controller.get_previous_time_in_global(self.picture, 1800)
        self.assertEqual(pic.picture_id, 194)

        # moding
        pic = self.sql_controller.get_previous_time_in_global(self.picture, 3659)
        self.assertEqual(pic.picture_id, 1993)

        pic = self.sql_controller.get_previous_time_in_global(self.picture, 3668)
        self.assertEqual(pic.picture_id, 1984)

    def test_get_next_time_skip_in_hikes(self):
        pass

    def test_get_next_time_skip_in_global(self):
        # id    time        minute  id
        # 1994  1556391512  718 ->  2219
        # 2000  1556391536  718	->  2225
        pic = self.sql_controller.get_next_time_skip_in_global(self.picture)
        self.assertEqual(pic.picture_id, 2219)

        pic = self.sql_controller.get_picture_with_id(2000)
        pic = self.sql_controller.get_next_time_skip_in_global(pic)
        self.assertEqual(pic.picture_id, 2225)

        # id    time        minute  id
        # 650   1556325800  1063 -> 875
        # 688   1556325952  1065 -> 906
        # 872   1556326688  1078 -> 1090
        pic = self.sql_controller.get_picture_with_id(650)
        pic = self.sql_controller.get_next_time_skip_in_global(pic)
        self.assertEqual(pic.picture_id, 875)

        pic = self.sql_controller.get_picture_with_id(688)
        pic = self.sql_controller.get_next_time_skip_in_global(pic)
        self.assertEqual(pic.picture_id, 906)

        pic = self.sql_controller.get_picture_with_id(872)
        pic = self.sql_controller.get_next_time_skip_in_global(pic)
        self.assertEqual(pic.picture_id, 1090)

    # ✅ test_get_next_time_in_hikes
    # ✅ test_get_previous_time_in_hikes
    # ✅ test_get_next_time_in_global
    # ✅ test_get_previous_time_in_global
    # test_get_next_time_skip_in_hikes
    # test_get_previous_time_skip_in_hikes
    # ✅ test_get_next_time_skip_in_global
    # ⭕ test_get_previous_time_skip_in_global


if __name__ == '__main__':
    print('Results of : projector_database_test.py\n')
    unittest.main()
