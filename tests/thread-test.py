
from threading import Thread
import time
import RPi.GPIO as gpio

gpio.setmode(gpio.BCM)
gpio.setup(17, gpio.IN)


global cycle
cycle = 0.0
status = False

class Hello5Program:
    def __init__(self):
        self._running = True

    def terminate(self):
        self._running = False

    def run(self):
        global cycle
        while self._running:
            gpio.wait_for_edge(17, gpio.RISING)
            status = not status
            print("=====================")
            time.wait(2)

class Hello2Program:
    def __init__(self):
        self._running = True

    def terminate(self):
        self._running = False

    def run(self):
        global cycle
        while self._running:
            print(status)

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
