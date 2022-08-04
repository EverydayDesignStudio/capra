#!/usr/bin/env python3

# Sets time on the DS3231 Real Time Clock
# This has to be done upon setup of every new camera

import os                       # For reading from bash script
import time                     # For unix timestamps
from datetime import datetime   # For printing readable time
from typing import Tuple        # For cleaner code
import busio                    # For interfacing with DS3231 Real Time Clock
import adafruit_ds3231          # pip install adafruit-circuitpython-ds3231


def main():
    print("Getting time from hardware clock")

    # Get the hardware clock time
    stream = os.popen('sudo hwclock -r')
    hwclock = stream.read()
    print("Hardware clock is:")
    print(hwclock)

    # Set date from hardware clock time
    os.popen('sudo date --set="{hwc}"'.format(hwc=hwclock))

    stream = os.popen('date')
    date = stream.read()
    print("Date is now:")
    print(date)

    print("--- End program ---")


if __name__ == "__main__":
    main()
