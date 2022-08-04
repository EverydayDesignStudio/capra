#!/usr/bin/env python3

# A collection of tests for Capra camera an projector

import unittest                 # Library for testing

import os                       # For reading from bash script
import time                     # For unix timestamps
import RPi.GPIO as GPIO         # For interfacing with the pins of the Raspberry Pi

from classes.button import Button  # For threading interrupts for button presses
from classes.capra_data_types import Picture, Hike
from classes.sql_controller import SQLController  # For interacting with the DB
from classes.piezo_player import PiezoPlayer  # For playing sounds
from classes.led_player import RedBlueLED  # For controlling LED on Buttonboard


class TestDatabase(unittest.TestCase):
    DB = '/home/pi/capra-storage/capra_camera.db'
    DB_EMPTY = '/home/pi/capra/tests/test_db_camera_empty.db'

    sql_controller = SQLController(database=DB)

    def test_get_last_altitude(self):
        sql_controller = SQLController(database=self.DB_EMPTY)
        alt = sql_controller.get_last_altitude()
        self.assertEqual(alt, 0)


if __name__ == "__main__":
    unittest.main()
