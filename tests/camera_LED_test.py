#!/usr/bin/env python3

import RPi.GPIO as gpio
import time

RED = 13            # BOARD - 33
GREEN = 26          # BOARD - 37
BLUE = 19           # BOARD - 35

gpio.setwarnings(False)     # Turn off GPIO warning
gpio.setmode(gpio.BCM)
gpio.setup(RED, gpio.OUT)
gpio.setup(GREEN, gpio.OUT)
gpio.setup(BLUE, gpio.OUT)

def on_off(pin: int):
    gpio.output(pin, True)
    time.sleep(2)
    gpio.output(pin, False)

def mixer(pin1: int, pin2: int):
    gpio.output(pin1, True)
    gpio.output(pin2, True)
    time.sleep(4)
    gpio.output(pin1, False)
    gpio.output(pin2, False)

# Individuals
on_off(RED)
on_off(GREEN)
on_off(BLUE)

print('BLUE + GREEN')
mixer(BLUE, GREEN)
print('BLUE + RED')
mixer(BLUE, RED)
print('RED + GREEN')
mixer(RED, GREEN)