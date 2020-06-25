#!/usr/bin/env python3

# Plays sound on startup, and listens to OFF button to be held down
# upon OFF being pressed, the LED turns blue and a sound is played
# =================================================

import time
import RPi.GPIO as gpio
import subprocess
from classes.led_player import RGB_LED          # For controlling LED on Buttonboard
from classes.piezo_player import PiezoPlayer    # For controlling piezo
import globals as g
g.init()

gpio.setmode(gpio.BCM)
gpio.setup(g.BUTTON_OFF, gpio.IN)
gpio.setup(g.LED_BLUE, gpio.OUT)
rgb_led = RGB_LED(g.LED_RED, g.LED_GREEN, g.LED_BLUE)  # red, green, blue LED
player = PiezoPlayer(g.PIEZO_PIN)

while True:
    print("Waiting for turnoff...")
    gpio.wait_for_edge(g.BUTTON_OFF, gpio.RISING)

    timer = 0
    duration = 10
    while gpio.input(g.BUTTON_OFF):
        print("Turning off in: ", str(duration - timer))
        timer += 1
        time.sleep(0.2)
        if timer > duration:
            rgb_led.turn_white()
            player.play_power_off_jingle()
            time.sleep(1)
            subprocess.call(['shutdown', '-h', 'now'], shell=False)
