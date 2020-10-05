#!/usr/bin/env python3

import threading
import time
from RPi import GPIO

count = 0

class ThreadingExample(object):
    """ Threading example class
    The run() method will be started and it will run in the background
    until the application exits.
    """

    def __init__(self, interval=1):
        """ Constructor
        :type interval: int
        :param interval: Check interval, in seconds
        """
        # self.interval = interval

        self.clk = 23
        self.cnt = 24

        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.clk, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
        GPIO.setup(self.cnt, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

        self.clkLastState = GPIO.input(self.clk)

        thread = threading.Thread(target=self.run, args=())
        thread.daemon = True                            # Daemonize thread
        thread.start()                                  # Start the execution

    def run(self):
        """ Method that runs forever """
        while True:
            global count

            self.clkState = GPIO.input(self.clk)
            self.cntState = GPIO.input(self.cnt)
            if self.clkState != self.clkLastState:
                if self.cntState != self.clkState:
                    count += 1
                else:
                    count -= 1
                # print(counter)
            self.clkLastState = self.clkState

            # Do something
            # print('Doing something imporant in the background')
            # num = num + 1
            # time.sleep(self.interval)

example = ThreadingExample()
lastCount = 0

# GUI Mainloop
while True:
    if count != lastCount:  # there's a new value
        print(count)
        lastCount = count
    
    time.sleep(4)
    # print(count)
    # time.sleep(0.1)

# time.sleep(3)
# print('Checkpoint')
# global num
# print(num)
# time.sleep(2)
# print('Bye')
