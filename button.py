import time
import shared
import RPi.GPIO as gpio


shared.init() # initialize shared variables
BUTTON_PLAYPAUSE = 17 # BOARD - 11

gpio.setmode(gpio.BCM)
gpio.setup(BUTTON_PLAYPAUSE, gpio.IN)

class Button:
    def __init__(self, BUTTON):
        self._running = True
        self.BUTTON = BUTTON

    def terminate(self):
        self._running = False

    def run(self):
        while self._running:
            print("waiting")
            gpio.wait_for_edge(self.BUTTON, gpio.RISING)
            global pause
            pause = not pause
            print("=====================")
            # except:
            #     print("~~~~ encountered error")






# def interrupt():
#     while(True):
#         try:
#             print("waiting for edge")
#             gpio.wait_for_edge(BUTTON_PLAYPAUSE, gpio.RISING)
#             shared.pause = not shared.pause
#             print("pause = ", shared.pause)
#             time.wait(0.5)
#
#         except KeyboardInterrupt:
#             print("Interrupted")
