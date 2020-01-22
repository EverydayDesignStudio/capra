#!/usr/bin/env python3

# Sets time on the DS3231 Real Time Clock
# This has to be done upon setup of every new camera

import time                     # For unix timestamps
from datetime import datetime   # For printing readable time
from typing import Tuple        # For cleaner code
import busio                    # For interfacing with DS3231 Real Time Clock
import adafruit_ds3231          # pip install adafruit-circuitpython-ds3231


def main():
    i2c = busio.I2C(3, 2)
    rtc = adafruit_ds3231.DS3231(i2c)

    rtc.datetime = time.struct_time((2017,1,20, 15,6,0, 0,20,0))

    print_rtc_time(rtc)


def print_rtc_time(rtc):
    print("DS3231 TIME WAS SET TO: ")
    timestamp = rtc.datetime
    print(timestamp)

    unix_ts = time.mktime(rtc.datetime)
    print(datetime.utcfromtimestamp(unix_ts).strftime('%Y-%m-%d %H:%M:%S'))


if __name__ == "__main__":
    main()
