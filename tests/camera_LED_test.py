#!/usr/bin/env python3

import RPi.GPIO as GPIO
import time
from classes.led_player import RGB_LED

LED_RED = 13                # BOARD - 33
LED_GREEN = 26              # BOARD - 37
LED_BLUE = 14               # BOARD - 8
GPIO.setwarnings(False)     # Turn off GPIO warnings
GPIO.setmode(GPIO.BCM)      # Broadcom pin numbers

led = RGB_LED(LED_RED, LED_GREEN, LED_BLUE)  # RGB LED


def sleep_off():
    time.sleep(1)
    led.turn_off()


led.turn_off()

print('Turn red')
led.turn_red()
sleep_off()
print('Turn green')
led.turn_green()
sleep_off()
print('Turn blue')
led.turn_blue()
sleep_off()
print('Turn pink')
led.turn_pink()
sleep_off()
print('Turn teal')
led.turn_teal()
sleep_off()
print('Turn orange')
led.turn_orange()
sleep_off()
print('Turn white')
led.turn_white()
sleep_off()
print('Turn off')
