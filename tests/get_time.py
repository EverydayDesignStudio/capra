#!/usr/bin/env python3

# Script for checking the set time of DS3231 Real time clock
import time                  # For unix timestamps
import busio                 # For interfacing with DS3231 Real Time Clock
import adafruit_ds3231       # pip install adafruit-circuitpython-ds3231


i2c = busio.I2C(3, 2)
timestamp = get_RTC_time(i2c)
print("TIME SET TO: ")
print(timestamp)


def get_RTC_time(I2C):
    rtc = adafruit_ds3231.DS3231(I2C)
    t = time.mktime(rtc.datetime)
    return(t)
