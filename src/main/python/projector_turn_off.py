#!/usr/bin/env python3

# Listens to OFF button to be held down
# upon OFF being pressed, LED turn on
# =================================================

import time
import RPi.GPIO as GPIO
import subprocess
import globals as g
g.init()

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
GPIO.setup(g.BUTT_OFF, GPIO.IN)

GPIO.setup(g.WHITE_LED1, GPIO.OUT)
GPIO.setup(g.WHITE_LED2, GPIO.OUT)
GPIO.setup(g.WHITE_LED3, GPIO.OUT)
GPIO.setup(g.RGB1_RED, GPIO.OUT)
GPIO.setup(g.RGB1_GREEN, GPIO.OUT)


def LED_on():
    GPIO.output(g.RGB1_RED, True)
    GPIO.output(g.RGB1_GREEN, True)

    GPIO.output(g.WHITE_LED1, True)
    GPIO.output(g.WHITE_LED2, True)
    GPIO.output(g.WHITE_LED3, True)


while True:
    print("Waiting for turnoff...")
    GPIO.wait_for_edge(g.BUTT_OFF, GPIO.RISING)

    timer = 0
    duration = 5
    while GPIO.input(g.BUTT_OFF):
        print("Turning off in: ", str(duration - timer))
        timer += 1
        time.sleep(0.2)
        if timer > duration:
            LED_on()
            time.sleep(1)
            print('SHUTDOWN')
            subprocess.call(['shutdown', '-h', 'now'], shell=False)
