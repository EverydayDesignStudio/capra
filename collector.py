#!/usr/bin/env python3
#   _______ ____  _______ _
#  / __/ _ `/ _ \/ __/ _ `/
#  \__/\_,_/ .__/_/  \_,_/
#         /_/
# ------------------------------------------------------------------------------
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
from threading import Thread # For threading

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
PIEZO = 18              # BOARD - 12

# TODO enable these values when switching to manufactured Buttonboard
# LED_GREEN = 26         # BOARD - 37
# LED_AMBER = 12         # BOARD - 33


# Set file wide shared variables
RESOLUTION = (1280, 720)
# RESOLUTION = (720, 405)
# NEW_HIKE_TIME = 43200     # 12 hours
# NEW_HIKE_TIME = 21600     # 6 hours
# NEW_HIKE_TIME = 10800     # 3 hours
NEW_HIKE_TIME = 5400        # 1 1/2 hours
# NEW_HIKE_TIME = 1800      # 1/2 hour



# Initialize GPIO pins
def initialize_GPIOs():
    gpio.setwarnings(False)
    gpio.setmode(gpio.BCM)
    gpio.setup(SEL_1, gpio.OUT)         # select 1
    gpio.setup(SEL_2, gpio.OUT)         # select 2
    gpio.setup(LED_GREEN, gpio.OUT)     # status led1
    gpio.setup(LED_AMBER, gpio.OUT)     # status led2
    gpio.setup(LED_BTM, gpio.OUT)       # status led3
    gpio.setup(PIEZO, gpio.OUT)         # PIEZO


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


# Blink status LEDs on camera - TODO Remove instances of nonexistent LEDS
def hello_blinks():
    blink(LED_GREEN, 2, 0.1)
    blink(LED_AMBER, 2, 0.1)
    blink(LED_BTM, 2, 0.1)


def blink_after_crash():
    blink_time = 0
    while (blink_time < 10):
        blink(LED_BTM, 4, 0.1)
        time.sleep(0.5)
        blink_time += 1


# Sound a beep from the piezo element
def beep(tone, duration, repeat):
    pzo = gpio.pwm(PIEZO, 0) # initialize piezo object
    for r in range(repeat):
        pzo.start(100)
        pzo.ChangeFrequency(tone)
        time.sleep(duration)
        pzo.stop()
        time.sleep(0.1)


# Initialize and return picamera object
def initialize_picamera(resolution: tuple) -> picamera:
    print('Initializing camera object')
    logging.info('Initializing camera object')
    gpio.output(SEL_1, False)
    gpio.output(SEL_2, False)
    time.sleep(0.2)
    logging.info('Select pins OK')
    pi_cam = picamera.PiCamera()
    time.sleep(0.2)
    logging.info('Cam init OK')
    pi_cam.resolution = resolution
    logging.info('Resolution OK')
    print('Resolution OK')
    pi_cam.rotation = 180
    print('Rotation OK')

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
            logging.info('cam 1 selected')
        if cam_num == 2:
            gpio.output(SEL_1, False)
            gpio.output(SEL_2, False)
            logging.info('cam 2 selected')
        if cam_num == 3:
            gpio.output(SEL_1, True)
            gpio.output(SEL_2, True)
            logging.info('cam 3 selected')
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
    # Initialize PINs, LEDs, and GPIO logger
    initialize_GPIOs()                              # Define the GPIO pin modes
    hello_blinks()                                  # Say hello through LEDs
    turn_off_leds()                                 # TODO - why do we need to
    i2c_bus = smbus.SMBus(1)                        # Setup I2C bus
    initialize_background_play_pause()              # Setup play/pause button
    prev_pause = True
    initialize_picamera(RESOLUTION) # Setup the camera

    # TODO Integrate this into sql_controller to overwrite any existing database data
    # and use the previous folder if it is empty.
    # ALTERNATIVELY, move folder creation to after pause is taken out.
    # FOLDER = '{d}hike{h}/'.format(d=DIRECTORY, h=hike_num)
    # for dirpath, dirnames, files in os.walk(FOLDER):
    #     if files:
    #         print(dirpath, 'has files')
    #     if not files:
    #         print(dirpath, 'is empty')


    # Create SQL controller and update hike information
    sql_controller = SQLController(database=DB)
    created = sql_controller.will_create_new_hike(NEW_HIKE_TIME, DIRECTORY)
    # <<<<<<< HEAD
    #     if created:     # new hike created: blink green
    #         blink(LED_GREEN, 2, 0.2)
    #     else:           # continuing last hike: blink orange
    #         blink(LED_AMBER, 2, 0.2)
    # =======
    if created:     # new hike created; blink four times
        blink(LED_BTM, 4, 0.2)
        os.chmod(DIRECTORY, 777)  # set permissions to be read and written to when run manually
        os.chmod(DB, 777)
    else:           # continuing last hike; blink two times
        blink(LED_BTM, 2, 0.2)
    time.sleep(1)
    hike_num = sql_controller.get_last_hike_id()
    print('HIKENO: ', hike_num, " =======")
    photo_index = sql_controller.get_last_photo_index_of_hike(hike_num)

    # Initialize the logger for this specific hike
    initialize_logger(hike_num)
    os.chmod(logname, 777)  # Make logfile accessible to writing by both root and user
    # Initialize camera and buttons
    pi_cam = initialize_picamera(RESOLUTION)        # Setup the camera
    initialize_background_play_pause()              # Setup play/pause button
    prev_pause = True

    # Start the time lapse
    # --------------------------------------------------------------------------
    while(True):
        # Pause the program if applicable
        while(shared.pause):
            if(not prev_pause):
                logging.info('Paused')
                prev_pause = True
            print(">>PAUSED!<<")
            blink(LED_BTM, 1, 0.3)
            time.sleep(1)
        # If applicable, log 'unpaused'
        if(prev_pause):
            logging.info('Unpaused')
            prev_pause = False

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
            logging.info('Cameras OK')

        # Wait until 2.5 seconds have passed since last picture
        while(time.time() < timestamp + 2.5):
            pass


if __name__ == "__main__":
    try:
        main()
    except Exception as error:
        logging.exception('===== Error ===== ')
        logging.exception(error)
        blink_after_crash()
