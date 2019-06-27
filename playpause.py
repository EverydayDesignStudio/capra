import time
import shared
import RPi.GPIO as gpio
from threading import Thread

shared.init() # initialize shared variables
BUTTON_PLAYPAUSE = 17 # BOARD - 11

gpio.setmode(gpio.BCM)
gpio.setup(BUTTON_PLAYPAUSE, gpio.IN)

class Playpause:
    def __init__(self):
        self._running = True

    def terminate(self):
        self._running = False

    def run(self):
        global pause
        while self._running:
            try:
                print("waiting")
                gpio.wait_for_edge(BUTTON_PLAYPAUSE, gpio.RISING)
                status = not status
                print("=====================")
                time.sleep(2)
            except:
                pass

#Create Class
PP_INTERRUPT = Playpause()
#Create Thread
PP_THREAD = Thread(target=PP_INTERRUPT.run)
#Start Thread
PP_THREAD.start()




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
