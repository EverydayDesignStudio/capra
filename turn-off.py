#!/usr/bin/env python3

# Plays sound on startup, and listens to OFF button to be held down
# upon OFF being pressed, the LED turns blue and a sound is played
# =================================================

import time
import RPi.GPIO as gpio
import subprocess
from classes.piezo_player import PiezoPlayer

BUTTON_OFF = 25     # BOARD - 22
LED_BTM = 26        # BOARD - 37
PIEZO_PIN = 12      # BOARD - 32

gpio.setmode(gpio.BCM)
gpio.setup(BUTTON_OFF, gpio.IN)
gpio.setup(LED_BTM, gpio.OUT)
player = PiezoPlayer(PIEZO_PIN)

is_startup = True

while(True):
    # Only play the startup jingle on startup
    if is_startup:
        player.play_power_on_jingle()
        is_startup = False
    print("Waiting for turnoff...")
    gpio.wait_for_edge(BUTTON_OFF, gpio.RISING)

    timer = 0
    duration = 10
    while(gpio.input(BUTTON_OFF)):
        print("Turning off in: ", str(duration - timer))
        timer += 1
        time.sleep(0.1)
        if (timer > duration):
            gpio.output(LED_BTM, True)
            player.play_stop_recording_jingle()
            time.sleep(1)
            subprocess.call(['shutdown', '-h', 'now'], shell=False)
