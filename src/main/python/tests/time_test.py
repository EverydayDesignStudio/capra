#!/usr/bin/env python3

import RPi.GPIO as GPIO
import time

while True:
    if round(time.time(), 0) % 2 == 0:
        print('...another 2 seconds')
        time.sleep(1)
