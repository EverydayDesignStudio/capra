#!/usr/bin/env python3
#  Turning off the Raspberry pi
# =================================================
#
import time
import RPi.GPIO as gpio
import subprocess

BUTTON_OFF = 25 # BOARD - 22
LED_BTM = 26 # BOARD - 37

gpio.setmode(gpio.BCM)
gpio.setup(BUTTON_OFF, gpio.IN)
gpio.setup(LED_BTM, gpio.OUT)

while(True):
    print("waiting for turnoff")
    gpio.wait_for_edge(BUTTON_OFF, gpio.RISING)
    timer = 0
    while(gpio.input(BUTTON_OFF)):
        print("turning off in: ", str(20 - timer))
        timer += 1
        if (timer > 20):
            gpio.output(LED_BTM, True)
            time.wait(2)
            subprocess.call(['shutdown', '-h', 'now'], shell=False)
