import time
import RPi.GPIO as GPIO
from classes.piezo_player import PiezoPlayer    # For controlling piezo

import globals as g
import shared
g.init()        # Initialize global constants
shared.init()   # Initialize shared variables


class PlayPauseButton:
    def __init__(self, BUTTON):
        self._running = True
        self.BUTTON = BUTTON
        GPIO.setup(self.BUTTON, GPIO.IN)

    def terminate(self):
        self._running = False

    def run(self):
        while self._running:
            print("=========Interrupt Start==========")
            GPIO.wait_for_edge(self.BUTTON, GPIO.RISING)
            shared.pause = not shared.pause
            print("Pause Button pressed | shared.pause = ", shared.pause)
            time.sleep(0.5)


class TurnOffButton:
    def __init__(self, BUTTON, piezo):
        self._running = True
        self.BUTTON = BUTTON
        print('following line is the button value:')
        print(BUTTON)
        GPIO.setwarnings(False)
        GPIO.setup(self.BUTTON, GPIO.IN)
        self.piezo = piezo

    def terminate(self):
        self._running = False

    def run(self):
        while self._running:
            print("=========Waiting for Turn Off=========")
            # GPIO.wait_for_edge(self.BUTTON, GPIO.RISING)
            time.sleep(0.5)

            timer = 0
            duration = 10
            while GPIO.input(self.BUTTON):
                print("Turning off in: ", str(duration - timer))
                timer += 1
                time.sleep(0.2)
                if timer > duration:  # Set turn_off to True
                    shared.turn_off = True
                    self.piezo.play_power_off_jingle()
                    time.sleep(2)
