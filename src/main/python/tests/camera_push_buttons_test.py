#!/usr/bin/env python3

import RPi.GPIO as GPIO
import time
import sys
import globals as g
g.init()

GPIO.setmode(GPIO.BCM)
GPIO.setup(g.BUTTON_PLAYPAUSE, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(g.BUTTON_OFF, GPIO.IN, pull_up_down=GPIO.PUD_UP)


def write(line):
    sys.stdout.write(line)
    sys.stdout.flush()


write("--- Push Button Values ---")

while True:
    input_play_pause = GPIO.input(g.BUTTON_PLAYPAUSE)
    if input_play_pause == 1:
        status_pp = 'Button is pressed'
    else:
        status_pp = 'Button is not pressed'

    input_off = GPIO.input(g.BUTTON_OFF)
    if input_off == 1:
        status_off = 'Button is pressed'
    else:
        status_off = 'Button is not pressed'

    time.sleep(0.05)

    output = """
Play/Pause Button: {pp}
Off Button: {off}
""".format(pp=status_pp, off=status_off)

    output = output.replace("\n", "\n\033[K")
    write(output)
    lines = len(output.split("\n"))
    write("\033[{}A".format(lines - 1))
