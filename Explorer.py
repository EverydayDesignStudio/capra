#!/usr/bin/env python3

#    _________ _____  _________ _
#   / ___/ __ `/ __ \/ ___/ __ `/
#  / /__/ /_/ / /_/ / /  / /_/ /
#  \___/\__,_/ .___/_/   \__,_/
#           /_/
#  Script to run on the Explorer camera unit. Takes pictures with
#  three picameras through the Capra cam multiplexer board
# =================================================

# Import Modules
import os  # For counting folders and creating new folders
import csv  # For saving and reading information in/from CSV files
import time  # For time keeping
import smbus  # For interfacing over I2C with the altimeter
import picamera  # For interfacting with the PiCamera
import datetime  # For translating POSIX timestamp to human readable date/time
import RPi.GPIO as gpio  # For interfacing with the pins of the Raspberry Pi


# Pin configuration
# TODO Will have more added later on to accomodate on/off switch
BUTTON_PLAYPAUSE = 17 # BOARD - 11
BUTTON_OFF = 25 # BOARD - 22
SEL_1 = 22 # BOARD - 15
SEL_2 = 23 # BOARD - 16
LED_GREEN = 24 # BOARD - 18
LED_BTM = 26 # BOARD - 37
LED_AMBER = 27 # BOARD - 13


# Get I2C bus
bus = smbus.SMBus(1)


# Initialize GPIO pins
gpio.setmode(gpio.BCM)
gpio.setup(SEL_1, gpio.OUT)  # select 1
gpio.setup(SEL_2, gpio.OUT)  # select 2
gpio.setup(LED_GREEN, gpio.OUT)  # status led1
gpio.setup(LED_AMBER, gpio.OUT)  # status led2
gpio.setup(LED_BTM, gpio.OUT)  # status led3

# Turn off LEDs
gpio.output(LED_GREEN, True)
time.sleep(0.1)
gpio.output(LED_AMBER, True)
time.sleep(0.1)
gpio.output(LED_BTM, False)

# Set Variables
# TODO : variables are not updated / accesses correctly within main
dir = '/home/pi/Desktop/pics/'
RESOLUTION = (1280, 720)
# RESOLUTION = (720, 405)
photono = 0


# Set Definitions
# For determining whether a row in a CSV is the last row
def isLast(itr):
    old = itr.next()
    for new in itr:
        yield False, old
        old = new
    yield True, old


# For blinking LEDs
def blink(pin, repeat, interval):
    on = False
    off = True
    if pin == LED_BTM:
        on = True
        off = False
    for i in range(repeat):
        gpio.output(pin, on)
        time.sleep(interval)
        gpio.output(pin, off)
        time.sleep(interval)


# Counts previous hikes
def counthikes():
    print('counthikes() - Counting previous hikes')
    print('======================================')
    number = 1
    for file in os.listdir(dir):
        if file.startswith('hike'):
            number = number + 1
            print('{f} is instance {n}'.format(f=file, n=number))
            print('new hike is number: {n}'.format(n=number))
    return number


# For determining the time the most recent hike ended
# TODO: check and fix
def timesincehike(_hikeno):
    print('timesincehike()')
    print('===============')
    csvfile = dir + 'hike' + str(_hikeno) + '/' 'meta.csv'
    print('reading from ', csvfile)
    timesince = 0
    lasthikephoto = 0
    lasthikedate = 0
    with open(csvfile, 'r') as meta:
        reader = csv.reader(meta)
        for row in reversed(list(reader)):
            print("=-=-=-=-=-=-=-=-=-=-")
            print(row)
            break
        lasthikedate = float(row[1])
        lasthikephoto = int(row[0])
        print(lasthikedate, "  =  ", lasthikephoto)
        print('last hike ended at: ', str(lasthikedate))
        # check if the last hike started less than half a day ago
        timesince = time.time() - lasthikedate
    print('time since last: ', str(timesince))
    return timesince, lasthikephoto


# For Selecting Cam and taking + saving a picture
def camcapture(_cam, _camno):
    print('camcapture( ', _camno, ' )')
    if _camno < 1 or _camno > 3:
        print('[camcapture] invalid cam number!')
    else:
        if _camno == 1:
            print("select cam 1")
            gpio.output(SEL_1, False)
            gpio.output(SEL_2, False)
        if _camno == 2:
            print("select cam 2")
            gpio.output(SEL_1, True)
            gpio.output(SEL_2, False)
        if _camno == 3:
            print("select cam 3")
            gpio.output(SEL_1, True)
            gpio.output(SEL_2, True)
        time.sleep(0.2) # moment for hardware to catch up
        global photono
        photoname = dir + str(photono) + '_cam' + str(_camno) + '.jpg'
        print("SAVE TO: " + str(photoname)),
        _cam.capture(photoname)
        print('  cam', str(_camno), '- picture taken!')


# Write a row to csv file
def writedata(index, timestamp, altitude):
    with open(dir + 'meta.csv', 'a') as meta:
        writer = csv.writer(meta)
        newrow = [index, timestamp, altitude]
        print(newrow)
        writer.writerow(newrow)


def main():
    # Hello blinks
    blink(LED_GREEN, 2, 0.1)
    blink(LED_AMBER, 2, 0.1)
    blink(LED_BTM, 2, 0.1)


    # Initialize camera object
    print('initializing camera')
    gpio.output(SEL_1, True)
    gpio.output(SEL_2, True)
    time.sleep(0.1)
    cam = picamera.PiCamera()
    cam.resolution = (1280, 720)

    global photono
    photono = 0 # TODO: Should be removed later; was inserted to get program running
    global hikeno
    hikeno = counthikes()  # Count existing hikes
    sincelast = 43201  # Forced in order to bypass timesincehike
    # sincelast = timesincehike(hikeno - 1)[0] # check time since last hike
    if(sincelast > 43200):  # determine whether to create new hike entry or continue on last hike
        # create new hike folder
        print('creating new hike:')
        folder = 'hike' + str(hikeno) + '/'  # change directory for actual hike record
        global dir
        dir = dir + folder
        os.makedirs(dir)

        #create meta csv file
        csvfile = dir + 'meta.csv'
        with open(csvfile, 'a') as meta:
            writer = csv.writer(meta)
            newrow = ["index", "time", "altitude"]
            print("HEADER ", newrow)
            writer.writerow(newrow)
        blink(LED_GREEN, 2, 0.2)
    else:
        # append to last hike
        print('continuing last hike:')
        # retrieve last photo number
        hikeno -= 1
        photono = timesincehike(hikeno)[1] + 1  # TODO: fix
        blink(LED_AMBER, 2, 0.2)

    # folder = 'hike' + str(hikeno) + '/'  # change directory for actual hike record
    # global dir

    # Loop Starts Here
    # =================================================
    while(True):
        # Query Altimeter first (takes a while)
        # MPL3115A2 address, 0x60(96) - Select control register, 0x26(38)
        # 0xB9(185)	Active mode, OSR = 128(0x80), Altimeter mode
        bus.write_byte_data(0x60, 0x26, 0xB9)

        # Take pictures
        # -------------------------------------
        camcapture(cam, 1)
        camcapture(cam, 2)
        camcapture(cam, 3)

        # MPL3115A2 address, 0x60(96)
        # Read data back from 0x00(00), 6 bytes
        # status, tHeight MSB1, tHeight MSB, tHeight LSB, temp MSB, temp LSB
        data = bus.read_i2c_block_data(0x60, 0x00, 6)

        tHeight = ((data[1] * 65536) + (data[2] * 256) + (data[3] & 0xF0)) / 16
        altitude = tHeight / 16.0
        timestamp = time.time()
        writedata(photono, timestamp, altitude) # Write Metadata

        # Increase increment
        global photono
        photono += 1

        # Blink on every fourth picture
        if (photono % 4 == 0):
            blink(LED_GREEN, 1, 0.1)
            blink(LED_AMBER, 1, 0.1)

        # Wait until 2.5 seconds have passed since last picture
        while(time.time() < timestamp + 2.5):
            pass


if __name__ == "__main__":
    main()
