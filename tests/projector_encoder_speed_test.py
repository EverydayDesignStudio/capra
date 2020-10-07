#!/usr/bin/env python3
# https://www.sunfounder.com/learn/Super_Kit_V2_for_RaspberryPi/lesson-8-rotary-encoder-super-kit-for-raspberrypi.html

import RPi.GPIO as GPIO
import time
from datetime import datetime
import globals as g
g.init()
# import queue

PERIOD = 500
MAXQUEUE = 5

# BOARD PINS
RoAPin = g.ENC1_A
RoBPin = g.ENC1_B
RoButPin = g.BUTT_ENC1

globalCounter = 0

lst = list()
# clkLastState = GPIO.input(clk)
last_time = datetime.now().timestamp()
speedText = ""
average = 0
dt = 0
multFactor = 1

flag = 0
Last_RoB_Status = 0
Current_RoB_Status = 0
Last_Direction = 0      # 0 for backward, 1 for forward
Current_Direction = 0   # 0 for backward, 1 for forward


def setup():
    GPIO.setmode(GPIO.BCM)  # Numbers GPIOs by BCM location
    GPIO.setup(RoAPin, GPIO.IN)    # input mode
    GPIO.setup(RoBPin, GPIO.IN)
    GPIO.setup(RoButPin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.add_event_detect(RoButPin, GPIO.FALLING, callback=clear)  # wait for falling


def calculate_speed():
    global last_time, dt
    dt = round(datetime.now().timestamp() - last_time, 5)
    # data sanitation: clean up random stray values that are extremely low
    if dt < .001:
        dt = .1

    if len(lst) > MAXQUEUE:
        lst.pop()
    lst.insert(0, dt)
    average = sum(lst) / len(lst)

    last_time = datetime.now().timestamp()

    #   .3   .07   .02
    if average >= .3:
        speedText = "slow"
    elif average >= .07 and average < .3:
        speedText = "medium"
    elif average >= .02 and average < .07:
        speedText = "fast"
    else:
        speedText = "super-duper fast"

    return average, speedText, dt


def rotaryDeal():
    global flag
    global Last_RoB_Status, Current_RoB_Status
    global Current_Direction, Last_Direction
    global globalCounter
    global last_time, average, dt, multFactor

    Last_RoB_Status = GPIO.input(RoBPin)

    while(not GPIO.input(RoAPin)):
        Current_RoB_Status = GPIO.input(RoBPin)
        flag = 1
    if flag == 1:
        flag = 0

        if (Last_RoB_Status == 0) and (Current_RoB_Status == 1):
            Current_Direction = 1
        if (Last_RoB_Status == 1) and (Current_RoB_Status == 0):
            Current_Direction = 0

        if (Current_Direction != Last_Direction):
            lst.clear()

        average, speedText, dt = calculate_speed()

        speed = 1 / dt
        multFactor = int(1 / average)
        if (multFactor < 1 or Current_Direction != Last_Direction):
            multFactor = 1
        # elif (multFactor):

        if (Current_Direction == 1):
            globalCounter = globalCounter - 1 * multFactor
        else:
            globalCounter = globalCounter + 1 * multFactor

        Last_Direction = Current_Direction
        print('Encoder counter: {g}, diff_time: {d:.4f}, speed: {s:.2f}, MultFactor: {a:.2f} ({st})'.format(g=globalCounter, d=dt, s=speed, a=multFactor, st=speedText))


def clear(ev=None):
    global globalCounter
    globalCounter = 0
    print('Encoder counter: = {g}'.format(g=globalCounter))
    time.sleep(1)


def loop():
    print('-------- Test Rotary Encoder (speed detection) --------')
    print('Option: Press encoder button to reset counter')
    print('Note: There may be some (network) lag via SSH/VNC\n')
    global globalCounter
    while True:
        rotaryDeal()


def destroy():
    GPIO.cleanup()             # Release resource


if __name__ == '__main__':     # Program start from here
    setup()
    try:
        loop()
    except KeyboardInterrupt:  # When 'Ctrl+C' is pressed, the child program destroy() will be  executed.
        destroy()
