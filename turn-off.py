#!/usr/bin/env python3

# Plays sound on startup, and listens to OFF button to be held down
# upon OFF being pressed, the LED turns blue and a sound is played
# =================================================

import time
import RPi.GPIO as gpio
import subprocess
from classes.led_player import RGB_LED          # For controlling LED on Buttonboard
from classes.piezo_player import PiezoPlayer    # For controlling piezo


BUTTON_OFF = 25         # BOARD - 22
LED_RED = 13            # BOARD - 33
LED_GREEN = 26          # BOARD - 37
LED_BLUE = 14           # BOARD - 8
PIEZO_PIN = 12          # BOARD - 32

gpio.setmode(gpio.BCM)
gpio.setup(BUTTON_OFF, gpio.IN)
gpio.setup(LED_BLUE, gpio.OUT)
rgb_led = RGB_LED(LED_RED, LED_GREEN, LED_BLUE)  # red, green, blue LED
player = PiezoPlayer(PIEZO_PIN)

is_startup = True

while True:
    # Only play the startup jingle on startup
    if is_startup:
        is_startup = False
    print("Waiting for turnoff...")
    gpio.wait_for_edge(BUTTON_OFF, gpio.RISING)

    timer = 0
    duration = 10
    while gpio.input(BUTTON_OFF):
        print("Turning off in: ", str(duration - timer))
        timer += 1
        time.sleep(0.1)
        if timer > duration:
            rgb_led.turn_white()
            player.play_power_off_jingle()
            time.sleep(1)
            subprocess.call(['shutdown', '-h', 'now'], shell=False)
