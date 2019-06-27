#!/usr/bin/env python3

#  Script to run on the Explorer camera unit. Takes pictures with
#  three picameras through the Capra cam multiplexer board
# ------------------------------------------------------------------------------

# Import Modules
import os  # used for counting folders and creating new folders
import time  # for time keeping
import datetime
from capra_data_types import Picture, Hike
from sql_controller import SQLController
import smbus  # For interfacing over I2C with the altimeter
import picamera  # For interfacting with the PiCamera
import RPi.GPIO as gpio

is_RPi = True
if is_RPi:
    DB = '/home/pi/capra-storage/capra_explorer.db'
    DIRECTORY = '/home/pi/capra-storage/'
else:
    DB = '/Volumes/Capra/capra-storage/capra_explorer.db'
    DIRECTORY = '/Volumes/Capra/capra-storage/'

# Pin configuration
# Will have more added later on to accomodate on/off switch
BUTTON_PLAYPAUSE = 4
SEL_1 = 22
SEL_2 = 23
LED_GREEN = 24
LED_BTM = 26
LED_AMBER = 27

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
RESOLUTION = (1280, 720)
# RESOLUTION = (720, 405)

# NEW_HIKE_TIME = 43200  # 12 hours
NEW_HIKE_TIME = 21600  # 6 hours
# NEW_HIKE_TIME = 10800  # 3 hours


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


# Blink status lights on the camera
def hello_blinks():
    blink(LED_GREEN, 2, 0.1)
    blink(LED_AMBER, 2, 0.1)
    blink(LED_BTM, 2, 0.1)


# Initialize and return picamera object
def initialize_picamera() -> picamera:
    print('Initialize camera object')
    gpio.output(SEL_1, True)
    gpio.output(SEL_2, True)
    time.sleep(0.1)
    pi_cam = picamera.PiCamera()
    pi_cam.resolution = (1280, 720)

    return pi_cam


# Determine whether to create new hike or continue the last hike
def create_or_continue_hike():
    sql_controller = SQLController(database=DB)
    time_since_last_hike = sql_controller.get_time_since_last_hike()

    # Create a new hike; -1 indicates this is the first hike in db
    if time_since_last_hike > NEW_HIKE_TIME or time_since_last_hike == -1:
        print('Creating new hike:')
        sql_controller.create_new_hike()

        # Create folder in harddrive to save photos
        hike_num = sql_controller.get_last_hike_id()
        folder = 'hike{n}/'.format(n=hike_num)
        os.makedirs(DIRECTORY + folder)

        blink(LED_GREEN, 2, 0.2)
    else:
        print('Continuing last hike:')
        blink(LED_AMBER, 2, 0.2)


# Select camera + take a photo + save photo in file system and db
def camcapture(pi_cam: picamera, cam_num: int, hike_num: int, photo_index: int, sql_ctrl: SQLController):
    print('select cam{n}'.format(n=cam_num))
    if cam_num < 1 or cam_num > 3:
        raise Exception('{n} is an invalid camera number. It must be 1, 2, or 3.'.format(n=cam_num))
    else:
        if cam_num == 1:
            gpio.output(SEL_1, False)
            gpio.output(SEL_2, False)
            print("cam 1 selected")
        if cam_num == 2:
            gpio.output(SEL_1, True)
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
        sql_ctrl.set_image_path(cam_num, image_path, hike_num, photo_index)
        print('cam {c} -- picture taken!'.format(c=cam_num))


def main():
    hello_blinks()
    pi_cam = initialize_picamera()
    create_or_continue_hike()

    # Get values for hike
    sql_controller = SQLController(database=DB)
    hike_num = sql_controller.get_last_hike_id()
    photo_index = sql_controller.get_last_photo_index_of_hike(hike_num)

    # Start the time lapse
    # --------------------------------------------------------------------------
    while(True):
        photo_index += 1  # new picture, so increment photo index
        timestamp = time.time()
        sql_controller.create_new_picture(timestamp, hike_num, photo_index)

        # Query Altimeter first (takes a while)
        # MPL3115A2 address, 0x60(96) - Select control register, 0x26(38)
        # 0xB9(185)	Active mode, OSR = 128(0x80), Altimeter mode
        bus.write_byte_data(0x60, 0x26, 0xB9)

        # Take pictures
        camcapture(pi_cam, 1, hike_num, photo_index, sql_controller)
        camcapture(pi_cam, 2, hike_num, photo_index, sql_controller)
        camcapture(pi_cam, 3, hike_num, photo_index, sql_controller)

        # MPL3115A2 address, 0x60(96)
        # Read data back from 0x00(00), 6 bytes
        # status, tHeight MSB1, tHeight MSB, tHeight LSB, temp MSB, temp LSB
        data = bus.read_i2c_block_data(0x60, 0x00, 6)
        tHeight = ((data[1] * 65536) + (data[2] * 256) + (data[3] & 0xF0)) / 16
        altitude = round(tHeight / 16.0, 2)
        # Update the time
        timestamp = time.time()

        # Update the database with metadata for picture & hike
        sql_controller.set_picture_time_altitude(timestamp, altitude, hike_num, photo_index)
        sql_controller.set_hike_endtime_picture_count(timestamp, photo_index, hike_num)

        # Prepare for next picture
        photo_index += 1

        # Blink on every fourth picture
        if (photo_index % 4 == 0):
            blink(LED_GREEN, 1, 0.1)
            blink(LED_AMBER, 1, 0.1)

        # Wait until 2.5 seconds have passed since last picture
        while(time.time() < timestamp + 2.5):
            pass


if __name__ == "__main__":
    main()
