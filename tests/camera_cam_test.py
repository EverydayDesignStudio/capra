#!/usr/bin/env python3

import os               # File system
import picamera         # Interfacting with PiCamera
import time             # Time keeping
import RPi.GPIO as gpio # Interfacing with IO
import globals as g
g.init()

# Initialize GPIO pins
gpio.setmode(gpio.BCM)
gpio.setwarnings(False)
gpio.setup(g.SEL_1, gpio.OUT)  # select 1
gpio.setup(g.SEL_2, gpio.OUT)  # select 2


# For Selecting Cam and taking + saving a picture
def camcapture(_cam, _camno):
    print('selectcam( ', _camno, ' )')
    if _camno < 1 or _camno > 3:
        print('[selectcam] invalid cam number!')
    else:
        if _camno == 1:
            print("select cam 1")
            gpio.output(g.SEL_1, True)
            gpio.output(g.SEL_2, False)
        if _camno == 2:
            print("select cam 2")
            gpio.output(g.SEL_1, False)
            gpio.output(g.SEL_2, False)
        if _camno == 3:
            print("select cam 3")
            gpio.output(g.SEL_1, True)
            gpio.output(g.SEL_2, True)
        time.sleep(0.2)
        DIR = '/home/pi/Desktop/cam-tests/'
        if not os.path.exists(DIR):
            print("Creating new directory on Desktop")
            os.mkdir(DIR)
        photoname = DIR + 'cam' + str(_camno) + '.jpg'
        print(photoname)
        _cam.capture(photoname)
        print('✅ cam', str(_camno), '- picture taken!')


def main():
    # Initialize camera object
    print('initializing camera')
    gpio.output(g.SEL_1, False)
    gpio.output(g.SEL_2, False)
    time.sleep(0.1)
    cam = picamera.PiCamera()
    cam.resolution = g.CAM_RESOLUTION

    # Take three pictures
    camcapture(cam, 1)
    camcapture(cam, 2)
    camcapture(cam, 3)
    print('\n🎉 Your cameras are connected properly!')
    print('Check folder ~/Desktop/cam-tests to verify quality of images.')


if __name__ == "__main__":
    main()
