#!/usr/bin/env python3

#  Script to run on the Explorer camera unit. Takes pictures with
#  three picameras through the Capra cam multiplexer board
# ------------------------------------------------------------------------------

# Import system modules
import datetime              # For translating POSIX timestamp to human readable date/time
import logging               # For creating a log
import os                    # For creating new folders
import picamera              # For interfacting with the PiCamera
import RPi.GPIO as gpio      # For interfacing with the pins of the Raspberry Pi
import smbus                 # For interfacing over I2C with the altimeter
import time                  # For unix timestamps
from threading import Thread #

# Import custom modules
import shared  # For shared variables between main code and button interrupts
from classes.button import Button  # For threading interrupts for button presses
from classes.capra_data_types import Picture, Hike
from classes.sql_controller import SQLController  # For interacting with the DB


DB = '/home/pi/capra-storage/capra_camera.db'
DIRECTORY = '/home/pi/capra-storage/'

# Pin configurations
BUTTON_PLAYPAUSE = 17   # BOARD - 11
SEL_1 = 22              # BOARD - 15
SEL_2 = 23              # BOARD - 16
LED_GREEN = 24          # BOARD - 18
LED_BTM = 26            # BOARD - 37
LED_AMBER = 27          # BOARD - 13

# Set file wide shared variables
RESOLUTION = (1280, 720)
# RESOLUTION = (720, 405)
# NEW_HIKE_TIME = 43200  # 12 hours
NEW_HIKE_TIME = 21600  # 6 hours
# NEW_HIKE_TIME = 10800  # 3 hours

gpio.setwarnings(False)
gpio.setmode(gpio.BCM)
gpio.setup(SEL_1, gpio.OUT)         # select 1
gpio.setup(SEL_2, gpio.OUT)         # select 2
gpio.setup(LED_GREEN, gpio.OUT)     # status led1
gpio.setup(LED_AMBER, gpio.OUT)     # status led2
gpio.setup(LED_BTM, gpio.OUT)       # status led3

# Initialize GPIO pins
# def initialize_GPIOs():
#     gpio.setwarnings(False)
#     gpio.setmode(gpio.BCM)
#     gpio.setup(SEL_1, gpio.OUT)         # select 1
#     gpio.setup(SEL_2, gpio.OUT)         # select 2
#     gpio.setup(LED_GREEN, gpio.OUT)     # status led1
#     gpio.setup(LED_AMBER, gpio.OUT)     # status led2
#     gpio.setup(LED_BTM, gpio.OUT)       # status led3


# Turn off LEDs
def turn_off_leds():
    gpio.output(LED_GREEN, True)
    time.sleep(0.1)
    gpio.output(LED_AMBER, True)
    time.sleep(0.1)
    gpio.output(LED_BTM, False)


# Blink LEDs
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


# Blink status LEDs on camera
def hello_blinks():
    blink(LED_GREEN, 2, 0.1)
    blink(LED_AMBER, 2, 0.1)
    blink(LED_BTM, 2, 0.1)


# Initialize and return picamera object
def initialize_picamera(resolution: tuple) -> picamera:
    print('Initializing camera object')
    gpio.output(SEL_1, True)
    gpio.output(SEL_2, True)
    time.sleep(0.2)
    print('Select pins OK')
    pi_cam = picamera.PiCamera()
    time.sleep(0.2)
    print('Cam init OK')
    pi_cam.resolution = resolution
    print('Resolution OK')

    return pi_cam


# Start threading interrupt for Play/pause button
def initialize_background_play_pause():
    PP_INTERRUPT = Button(BUTTON_PLAYPAUSE)  # Create class
    PP_THREAD = Thread(target=PP_INTERRUPT.run)  # Create Thread
    PP_THREAD.start()  # Start Thread


# Initialize the logger
def initialize_logger(hike_num: int):
    # logname = 'log-hike' + str(hike_num) + '.log'
    logname = '/home/pi/capra-storage/logs/hike{n}.log'.format(n=hike_num)
    logging.basicConfig(filename=logname, level=logging.DEBUG, format='%(asctime)s %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p')
    logging.info('START')


# Select camera + take a photo + save photo in file system and db
def camcapture(pi_cam: picamera, cam_num: int, hike_num: int, photo_index: int, sql_controller: SQLController):
    print('select cam{n}'.format(n=cam_num))
    if cam_num < 1 or cam_num > 3:
        raise Exception('{n} is an invalid camera number. It must be 1, 2, or 3.'.format(n=cam_num))
    else:
        if cam_num == 1:
            gpio.output(SEL_1, True)
            gpio.output(SEL_2, False)
            print("cam 1 selected")
        if cam_num == 2:
            gpio.output(SEL_1, False)
            gpio.output(SEL_2, False)
            print("cam 2 selected")
        if cam_num == 3:
            gpio.output(SEL_1, True)
            gpio.output(SEL_2, True)
            print("cam 3 selected")
        time.sleep(0.2)  # it takes some time for the pin selection

        # Build image file path
        image_path = '{d}hike{h}/{p}_cam{c}.jpg'.format(d=DIRECTORY, h=hike_num, p=photo_index, c=cam_num)
        print(image_path)

        # Take the picture
        pi_cam.capture(image_path)
        sql_controller.set_image_path(cam_num, image_path, hike_num, photo_index)
        print('cam {c} -- picture taken!'.format(c=cam_num))


# Tell altimeter to collect data; this process (takes a while)
# TODO - define "a while"
def query_altimeter(bus: smbus):
    # MPL3115A2 address, 0x60(96) - Select control register, 0x26(38)
    # 0xB9(185)	Active mode, OSR = 128(0x80), Altimeter mode
    bus.write_byte_data(0x60, 0x26, 0xB9)


# Read currently collected altimeter data
def read_altimeter(bus: smbus) -> float:
    # MPL3115A2 address, 0x60(96)
    # Read data back from 0x00(00), 6 bytes
    # status, tHeight MSB1, tHeight MSB, tHeight LSB, temp MSB, temp LSB
    data = bus.read_i2c_block_data(0x60, 0x00, 6)
    tHeight = ((data[1] * 65536) + (data[2] * 256) + (data[3] & 0xF0)) / 16
    altitude = round(tHeight / 16.0, 2)

    return altitude


def main():
    # Initialize and setup hardware
    #initialize_GPIOs()                              # Define the GPIO pin modes
    i2c_bus = smbus.SMBus(1)                        # Setup I2C bus
    turn_off_leds()                                 # TODO - why do we need to
    hello_blinks()                                  # Say hello through LEDs
    #pi_cam = initialize_picamera(RESOLUTION)        # Setup the camera
    initialize_background_play_pause()              # Setup play/pause button


    print('Initializing camera object')
    gpio.output(SEL_1, True)
    gpio.output(SEL_2, True)
    time.sleep(0.2)
    print('Select pins OK')
    pi_cam = picamera.PiCamera()
    time.sleep(0.2)
    print('Cam init OK')
    pi_cam.resolution = resolution
    print('Resolution OK')


    # Create SQL controller and update hike information
    sql_controller = SQLController(database=DB)

    created = sql_controller.will_create_new_hike(NEW_HIKE_TIME, DIRECTORY)
    if created:     # new hike created; blink green
        blink(LED_GREEN, 2, 0.2)
    else:           # continuing last hike; blink orange
        blink(LED_AMBER, 2, 0.2)

    hike_num = sql_controller.get_last_hike_id()
    photo_index = sql_controller.get_last_photo_index_of_hike(hike_num)

    # Initialize logger
    initialize_logger(hike_num)

    # Start the time lapse
    # --------------------------------------------------------------------------
    while(True):
        # TODO - explanation of what is happening here
        prev_pause = False
        while(shared.pause):
            if(not prev_pause):
                logging.info('Paused')
                prev_pause = True
            print(">>PAUSED!<<")
            blink(LED_BTM, 1, 0.3)
            time.sleep(1)

        if(prev_pause):
            logging.info('Unpaused')

        # New picture: increment photo index & add row to database
        photo_index += 1
        sql_controller.create_new_picture(hike_num, photo_index)

        query_altimeter(i2c_bus)  # Query Altimeter first (takes a while)

        # Take pictures
        camcapture(pi_cam, 1, hike_num, photo_index, sql_controller)
        camcapture(pi_cam, 2, hike_num, photo_index, sql_controller)
        camcapture(pi_cam, 3, hike_num, photo_index, sql_controller)

        # Update the database with metadata for picture & hike
        altitude = read_altimeter(i2c_bus)
        sql_controller.set_picture_time_altitude(altitude, hike_num, photo_index)
        sql_controller.set_hike_endtime_picture_count(photo_index, hike_num)

        timestamp = time.time()

        # Blink on every fourth picture
        if (photo_index % 4 == 0):
            blink(LED_GREEN, 1, 0.1)
            blink(LED_AMBER, 1, 0.1)
            logging.info('cameras still alive')

        # Wait until 2.5 seconds have passed since last picture
        while(time.time() < timestamp + 2.5):
            pass


if __name__ == "__main__":
    main()
