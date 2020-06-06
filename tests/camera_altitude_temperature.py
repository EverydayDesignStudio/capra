#!/usr/bin/env python3

# https://github.com/adafruit/Adafruit_CircuitPython_MPL3115A2/blob/master/examples/mpl3115a2_simpletest.py
# Simple demo of the MPL3115A2 sensor.
# Will read the pressure and temperature and print them out every second.
# Author: Tony DiCola
import time

import board
import busio

import adafruit_mpl3115a2


# Initialize the I2C bus.
i2c = busio.I2C(board.SCL, board.SDA)

# Initialize the MPL3115A2.
sensor = adafruit_mpl3115a2.MPL3115A2(i2c)
# Alternatively you can specify a different I2C address for the device:
# sensor = adafruit_mpl3115a2.MPL3115A2(i2c, address=0x10)

# You can configure the pressure at sealevel to get better altitude estimates.
# This value has to be looked up from your local weather forecast or meteorlogical
# reports.  It will change day by day and even hour by hour with weather
# changes.  Remember altitude estimation from barometric pressure is not exact!
# Set this to a value in pascals:
sensor.sealevel_pressure = 101000

# Main loop to read the sensor values and print them every second.
while True:
    pressure = sensor.pressure
    print("Pressure: {0:0.3f} pascals".format(pressure))
    altitude = sensor.altitude
    print("Altitude: {0:0.3f} meters".format(altitude))
    temperature = sensor.temperature
    print("Temperature: {0:0.2f} degrees Celsius".format(temperature))
    print("Temperature: {0:0.2f} degrees Fahrenheit".format(temperature * 1.8 + 32))
    print('\n')
    time.sleep(1.0)
