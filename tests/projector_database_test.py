#!/usr/bin/env python3

from typing import Any
from classes.capra_data_types import Picture, Hike
from classes.sql_controller import SQLController
import unittest
import random


class DatabaseTest(unittest.TestCase):
    DB = 'capra-storage/capra_projector_jan2021_min_test.db'  # no / infront makes the path relative
    sql_controller = None
    picture = None

    @classmethod
    def setUpClass(self):
        self.sql_controller = SQLController(database=self.DB)
        self.picture = self.sql_controller.get_picture_with_id(1994)

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

        # offset is more than total list size, but is below the list
        pic = self.sql_controller.get_next_time_in_hikes(self.picture, 27+3658)
        self.assertEqual(pic.time, 1556391620.0)
        self.assertEqual(pic.picture_id, 2021)

        # offset is more than total list size, but is above in the list
        pic = self.sql_controller.get_next_time_in_hikes(self.picture, 1675+3658)
        self.assertEqual(pic.time, 1556323244.0)
        self.assertEqual(pic.picture_id, 11)

    # ✅ test_get_next_time_in_hikes
    # test_get_previous_time_in_hikes
    # test_get_next_time_in_global
    # test_get_previous_time_in_global
    # test_get_next_time_skip_in_hikes
    # test_get_previous_time_skip_in_hikes
    # test_get_next_time_skip_in_global
    # test_get_previous_time_skip_in_global


if __name__ == '__main__':
    print('Results of : projector_database_test.py\n')
    unittest.main()
