#!/usr/bin/env python3
#  Turning off the Raspberry pi
# =================================================
#
import time
import RPi.GPIO as gpio
import subprocess

BUTTON_OFF = 25 # BOARD - 22


gpio.setmode(gpio.BCM)
gpio.setup(BUTTON_OFF, gpio.IN)


while(True):
    print("waiting for turnoff")
    gpio.wait_for_edge(BUTTON_OFF, gpio.RISING)
    timer = 0
    while(gpio.input(BUTTON_OFF)):
        print("turning off in: ", str(20 - 1)
        timer += 1
        if (timer > 20):
            subprocess.call(['shutdown', '-h', 'now'], shell=False)
