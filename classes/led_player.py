#!/usr/bin/env python3

# ---------------------------------------------------
# A collection of functions for RED and BLUE LEDs
# ---------------------------------------------------

import RPi.GPIO as GPIO
import time


class WHITE_LEDS:
    '''Used for the Projector'''
    def __init__(self, PIN1: int, PIN2: int, PIN3: int):
        self._timeLED = PIN1
        self._colorLED = PIN2
        self._altitudeLED = PIN3

        GPIO.setup(self._timeLED, GPIO.OUT)
        GPIO.setup(self._colorLED, GPIO.OUT)
        GPIO.setup(self._altitudeLED, GPIO.OUT)

    def turn_off(self):
        GPIO.output(self._timeLED, False)
        GPIO.output(self._colorLED, False)
        GPIO.output(self._altitudeLED, False)

    def set_time_mode(self):
        GPIO.output(self._timeLED, True)
        GPIO.output(self._colorLED, False)
        GPIO.output(self._altitudeLED, False)

    def set_color_mode(self):
        GPIO.output(self._timeLED, False)
        GPIO.output(self._colorLED, True)
        GPIO.output(self._altitudeLED, False)

    def set_altitude_mode(self):
        GPIO.output(self._timeLED, False)
        GPIO.output(self._colorLED, False)
        GPIO.output(self._altitudeLED, True)


class RGB_LED:
    '''Used for the Camera and Projector'''
    def __init__(self, red_pin: int, green_pin: int, blue_pin: int):
        self.LED_RED = red_pin
        self.LED_GREEN = green_pin
        self.LED_BLUE = blue_pin
        print('RGBLEDPlayer object created for RED pin: {r}, GREEN pin: {g}, & BLUE pin: {b}'
              .format(r=red_pin, g=green_pin, b=blue_pin))
        GPIO.setup(red_pin, GPIO.OUT)       # Red LED
        GPIO.setup(green_pin, GPIO.OUT)     # Green LED
        GPIO.setup(blue_pin, GPIO.OUT)      # BLUE LED

    # Functions
    # --------------------------------------------------------------------------
    def turn_off(self):
        GPIO.output(self.LED_RED, False)
        GPIO.output(self.LED_GREEN, False)
        GPIO.output(self.LED_BLUE, False)

    def sleep_off(self):
        time.sleep(2)
        self.turn_off()

    def turn_red(self):
        GPIO.output(self.LED_RED, True)

    def turn_green(self):
        GPIO.output(self.LED_GREEN, True)

    def turn_blue(self):
        GPIO.output(self.LED_BLUE, True)

    def turn_pink(self):
        GPIO.output(self.LED_RED, True)
        GPIO.output(self.LED_BLUE, True)

    def turn_teal(self):
        GPIO.output(self.LED_GREEN, True)
        GPIO.output(self.LED_BLUE, True)

    def turn_orange(self):
        GPIO.output(self.LED_RED, True)
        GPIO.output(self.LED_GREEN, True)

    def turn_white(self):
        GPIO.output(self.LED_RED, True)
        GPIO.output(self.LED_GREEN, True)
        GPIO.output(self.LED_BLUE, True)

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
        self.blink(self.LED_RED, 15, 0.1)

    def blink_teal_new_hike(self):
        for i in range(6):
            self.turn_teal()
            time.sleep(.15)
            self.turn_off()
            time.sleep(.15)

    def blink_green_continue_hike(self):
        for i in range(6):
            self.turn_green()
            time.sleep(.15)
            self.turn_off()
            time.sleep(.15)

    def blink_green_new_picture(self):
        self.blink(self.LED_GREEN, 2, 0.15)
