#!/usr/bin/env python3

# ---------------------------------------------------
# A collection of functions for RED and BLUE LEDs
# ---------------------------------------------------

import RPi.GPIO as GPIO
import time


class RedBlueLED:
    def __init__(self, red_pin: int, blue_pin: int):
        self.LED_RED = red_pin
        self.LED_BLUE = blue_pin
        print('RedBlueLEDPlayer object created for RED pin: {r} & BLUE pin: {b}'
              .format(r=red_pin, b=blue_pin))
        GPIO.setup(red_pin, GPIO.OUT)       # Red LED
        GPIO.setup(blue_pin, GPIO.OUT)      # BLUE LED

    # Functions
    # --------------------------------------------------------------------------
    def turn_off(self):
        GPIO.output(self.LED_BLUE, False)
        GPIO.output(self.LED_RED, False)

    def turn_blue(self):
        GPIO.output(self.LED_BLUE, True)

    def turn_red(self):
        GPIO.output(self.LED_RED, True)

    def turn_purple(self):
        GPIO.output(self.LED_BLUE, True)
        GPIO.output(self.LED_RED, True)

    # Helper function for blinking
    def blink(self, pin: int, repeat: int, interval: float) -> None:
        for i in range(repeat):
            GPIO.output(pin, True)
            time.sleep(interval)
            GPIO.output(pin, False)
            time.sleep(interval)

    def blink_red_blue(self):
        self.blink(self.LED_RED, 4, 0.3)
        self.blink(self.LED_BLUE, 4, 0.3)

    def blink_red_quick(self):
        self.blink(self.LED_RED, 10, 0.1)
