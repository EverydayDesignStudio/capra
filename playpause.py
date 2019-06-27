import time
import shared
import RPi.GPIO as gpio

shared.init() # initialize shared variables
BUTTON_PLAYPAUSE = 17 # BOARD - 11

gpio.setmode(gpio.BCM)
gpio.setup(BUTTON_PLAYPAUSE, gpio.IN)

while(True):
    try:
        print("waiting for edge")
        gpio.wait_for_edge(BUTTON_PLAYPAUSE, gpio.RISING)
        shared.pause = not shared.pause
        print("pause = ", shared.pause)

    except KeyboardInterrupt:
        print("Interrupted")
