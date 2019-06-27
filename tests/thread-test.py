
from threading import Thread
import time
import RPi.GPIO as gpio

BUTTON_PLAYPAUSE = 17 # BOARD - 11

gpio.setmode(gpio.BCM)
gpio.setup(BUTTON_PLAYPAUSE, gpio.IN)


global cycle
cycle = 0.0
global status
status = False

class Hello5Program:
    def __init__(self):
        self._running = True

    def terminate(self):
        self._running = False

    def run(self):
        global cycle
        while self._running:
            try:
                print("waiting")
                gpio.wait_for_edge(BUTTON_PLAYPAUSE, gpio.RISING)
                status = not status
                print("=====================")
                time.sleep(2)
            except:
                pass

class Hello2Program:
    def __init__(self):
        self._running = True

    def terminate(self):
        self._running = False

    def run(self):
        global cycle
        while self._running:
            print(status)
            time.sleep(1)

#Create Class
FiveSecond = Hello5Program()
#Create Thread
FiveSecondThread = Thread(target=FiveSecond.run)
#Start Thread
FiveSecondThread.start()

#Create Class
TwoSecond = Hello2Program()
#Create Thread
TwoSecondThread = Thread(target=TwoSecond.run)
#Start Thread
TwoSecondThread.start()


Exit = False #Exit flag
while Exit==False:
 cycle = cycle + 0.1
 print("Main Program increases cycle+0.1 - ", cycle)
 time.sleep(1) #One second delay
 if (cycle > 5): Exit = True #Exit Program

TwoSecond.terminate()
FiveSecond.terminate()
print("Goodbye :)")
