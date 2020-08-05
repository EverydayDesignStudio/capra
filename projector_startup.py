#!/usr/bin/env python3

# Turns off the UART 14 pin as soon as possible
# to prevent the AXAA projector from restarting

# This needs to be set as a service by running the Make command for it
# =================================================

import time
import RPi.GPIO as GPIO
import subprocess
import globals as g
g.init()

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
GPIO.setup(g.PROJ_UART, GPIO.OUT)

# BCM 14 is set HIGH on startup from /boot/config.txt
# time.sleep(15)
GPIO.output(g.PROJ_UART, False)
print('Set to LOW')
