#!/usr/bin/env python3

# Tests to see whether the PowerBoost module detects
# the batteries as being high or low

import os                       # For reading from bash script
import time                     # For unix timestamps
import RPi.GPIO as GPIO         # For interfacing with the pins of the Raspberry Pi

LDO = 6  # BOARD - 31

GPIO.setwarnings(False)             # Turn off GPIO warnings
GPIO.setmode(GPIO.BCM)              # Broadcom pin numbers
# low dropout (low power detection) from PowerBoost
GPIO.setup(LDO, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)


def main():
    print("Testing the returned value from the camera batteries")

    print('The battery status is: {n}'.format(n=GPIO.input(LDO)))
    if (GPIO.input(LDO) == GPIO.LOW):
        print('IT WOULD NOW POWER OFF 🔴')
    else:
        print('IT WOULD STAY ON 🟢')


if __name__ == "__main__":
    main()
