#!/usr/bin/env python3
# https://www.sunfounder.com/learn/Super_Kit_V2_for_RaspberryPi/lesson-8-rotary-encoder-super-kit-for-raspberrypi.html

import RPi.GPIO as GPIO
import time
import globals as g
g.init()

# BCM PINS
RoAPin = g.ENC1_A
RoBPin = g.ENC1_B
RoButPin = g.BUTT_ENC1

globalCounter = 0

flag = 0
Last_RoB_Status = 0
Current_RoB_Status = 0


def setup():
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(RoAPin, GPIO.IN)    # input mode
    GPIO.setup(RoBPin, GPIO.IN)
    GPIO.setup(RoButPin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.add_event_detect(RoButPin, GPIO.FALLING, callback=button_pressed)  # wait for falling


def rotary_turn():
    global flag
    global Last_RoB_Status
    global Current_RoB_Status
    global globalCounter
    Last_RoB_Status = GPIO.input(RoBPin)

    while(not GPIO.input(RoAPin)):
        Current_RoB_Status = GPIO.input(RoBPin)
        flag = 1
    if flag == 1:
        flag = 0
        if (Last_RoB_Status == 0) and (Current_RoB_Status == 1):
            globalCounter = globalCounter - 1
            print('Encoder counter = {g}'.format(g=globalCounter))
        if (Last_RoB_Status == 1) and (Current_RoB_Status == 0):
            globalCounter = globalCounter + 1
            print('Encoder counter = {g}'.format(g=globalCounter))


def button_pressed(ev=None):
    global globalCounter
    globalCounter = 0
    print('Button pressed & encoder counter reset')
    time.sleep(1)


def loop():
    print('-------- Test Rotary Encoder (single step) --------')
    print('Option: Press encoder button to reset counter')
    print('Note: There may be some (network) lag via SSH/VNC\n')

    while True:
        rotary_turn()


def destroy():
    GPIO.cleanup()             # Release resource


if __name__ == '__main__':     # Program start from here
    setup()
    try:
        loop()
    except KeyboardInterrupt:  # When 'Ctrl+C' is pressed, the child program destroy() will be  executed.
        destroy()
