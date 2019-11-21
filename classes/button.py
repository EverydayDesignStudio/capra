import time
import shared
import RPi.GPIO as gpio


shared.init()  # Initialize shared variables
# BUTTON_PLAYPAUSE = 17  # BOARD - 11
# gpio.setmode(gpio.BCM)


class Button:
    def __init__(self, BUTTON):
        self._running = True
        self.BUTTON = BUTTON
        gpio.setup(self.BUTTON, gpio.IN)

    def terminate(self):
        self._running = False

    def run(self):
        while self._running:
            print("=========Interrupt Start==========")
            gpio.wait_for_edge(self.BUTTON, gpio.RISING)
            shared.pause = not shared.pause
            print("PRESSED! >>>>>>>> Pause = ", shared.pause)
            time.sleep(0.5)
