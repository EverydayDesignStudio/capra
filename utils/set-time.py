
# Script for setting time on the DS3231 Real time clock
import time                  # For unix timestamps
import busio                 # For interfacing with DS3231 Real Time Clock
import adafruit_ds3231       # pip install adafruit-circuitpython-ds3231


I2C = busio.I2C(3, 2)
rtc = adafruit_ds3231.DS3231(I2C)
rtc.datetime = time.struct_time((2019,8,27,11,29,40,0,9,-1))


t = rtc.datetime
print("TIME SET TO:")
print(t)
