#!/usr/bin/env python3
#   _______ ____  _______ _
#  / __/ _ `/ _ \/ __/ _ `/
#  \__/\_,_/ .__/_/  \_,_/
#         /_/
# ------------------------------------------------------------------------------
#  Script to run on the camera unit. Takes pictures with
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
import board                 # For I2C reading for MPL3115A2 Altimeter
import busio                 # For interfacing with DS3231 Real Time Clock
import adafruit_ds3231       #
import adafruit_mpl3115a2    # For altimeter
from threading import Thread # For threading
import subprocess            # For calling shutdown
import psutil                # For checking free space of system

# Import custom modules
import shared  # For shared variables between main code and button interrupts
from classes.camera_buttons import PlayPauseButton, TurnOffButton  # For threading interrupts for button presses
from classes.capra_data_types import Picture, Hike
from classes.sql_controller import SQLController  # For interacting with the DB
from classes.piezo_player import PiezoPlayer  # For playing sounds
from classes.led_player import RGB_LED  # For controlling LED on Buttonboard

# PIN and Settings values are stored here
import globals as g
g.init()

# Setup GPIO PINS
gpio.setwarnings(False)             # Turn off GPIO warnings
gpio.setmode(gpio.BCM)              # Broadcom pin numbers
gpio.setup(g.SEL_1, gpio.OUT)       # camera control select 1
gpio.setup(g.SEL_2, gpio.OUT)       # camera control select 2

i2c = busio.I2C(board.SCL, board.SDA)  # Initialize I2C for MPL3115A2 altimeter
altimeter = adafruit_mpl3115a2.MPL3115A2(i2c)
altimeter.sealevel_pressure = g.SEALEVEL_PRESSURE

gpio.setup(g.LDO, gpio.IN, pull_up_down=gpio.PUD_DOWN)  # low dropout (low power detection) from PowerBoost
piezo = PiezoPlayer(g.PIEZO)        # piezo buzzer
rgb_led = RGB_LED(g.LED_RED, g.LED_GREEN, g.LED_BLUE)  # RGB LED
altitude_error_list = []            # empty list for ROWIDs that have junk altitude values


# Helper functions
# ------------------------------------------------------------------------------
def print_and_log(message: str):
    print(message)
    logging.info(message)


# Initialize and return picamera object
def initialize_picamera(resolution: tuple) -> picamera:
    logging.info('Initializing camera objects')
    gpio.output(g.SEL_1, False)
    gpio.output(g.SEL_2, False)
    time.sleep(0.2)
    logging.info('Select pins OK')
    pi_cam = picamera.PiCamera()
    time.sleep(0.2)
    logging.info('Cam init OK')
    pi_cam.resolution = resolution
    logging.info('Resolution OK')
    pi_cam.rotation = 180
    logging.info('Rotation OK')

    return pi_cam


# Start threading interrupts for Play/Pause button & Turn Off button
def initialize_background_play_pause():
    PP_INTERRUPT = PlayPauseButton(g.BUTTON_PLAYPAUSE)  # Create class
    PP_THREAD = Thread(target=PP_INTERRUPT.run)  # Create Thread
    PP_THREAD.start()  # Start Thread


def initialize_background_turn_off():
    PP_INTERRUPT = TurnOffButton(g.BUTTON_OFF, piezo)  # Create class
    PP_THREAD = Thread(target=PP_INTERRUPT.run)  # Create Thread
    PP_THREAD.start()  # Start Thread


# Initialize the logger
def initialize_startup_logger():
    logname = '/home/pi/capra-storage/logs/startup.log'
    logging.basicConfig(filename=logname,
                        level=logging.DEBUG,
                        format='%(name)s @ %(asctime)s (%(levelname)s): %(message)s',
                        datefmt='%m/%d/%Y %I:%M:%S %p')
    logging.debug('\n\n\n--------------------- CAPRA TURNED ON ---------------------')


def switch_to_hike_logger(hike_num: int):
    # Setup hike logger
    logname = '/home/pi/capra-storage/logs/hike{n}.log'.format(n=hike_num)
    fileh = logging.FileHandler(logname, 'a')
    formatter = logging.Formatter(fmt='%(name)s @ %(asctime)s (%(levelname)s): %(message)s',
                                  datefmt='%m/%d/%Y %I:%M:%S %p')
    fileh.setFormatter(formatter)

    # Switch loggers
    log = logging.getLogger()       # root logger
    for hdlr in log.handlers[:]:    # remove all old handlers
        log.removeHandler(hdlr)
    log.addHandler(fileh)           # set the new handler


# Check if camera turn off button has been pressed
def check_button_turn_off():
    if shared.turn_off:
        rgb_led.turn_white()
        # piezo.play_power_off_jingle()  # This is instead being called from the bg thread
        logging.info('--------------------- POWERED OFF ---------------------')
        logging.info('-------------------- Button Pressed -------------------\n')
        subprocess.call(['shutdown', '-h', 'now'], shell=False)


# Check if camera battery is low and turn off camera if it is
def check_low_battery_turn_off():
    status = gpio.input(g.LDO)
    print('The battery status is: {s}'.format(s=status))
    if status == gpio.LOW:
        rgb_led.turn_red()
        piezo.play_low_battery_storage_jingle()
        logging.info('--------------------- POWERED OFF ---------------------')
        logging.info('The battery status is: {s}'.format(s=status))
        logging.info('--------------------- Low Battery -------------------\n')
        time.sleep(2)
        subprocess.call(['shutdown', '-h', 'now'], shell=False)


# Check if camera storage is low and turn off if it is
def check_low_storage_turn_off():
    path = '/home/pi/'
    bytes_available = psutil.disk_usage(path).free
    megs_available = round(bytes_available / 1024 / 1024, 0)
    print('{m} Megabytes Available'.format(m=megs_available))
    if megs_available < 512:
        rgb_led.turn_orange()
        piezo.play_low_battery_storage_jingle()
        logging.info('--------------------- POWERED OFF ---------------------')
        logging.info('Megabytes Available: {m}'.format(m=megs_available))
        logging.info('--------------------- Low Storage -------------------\n')
        time.sleep(2)
        subprocess.call(['shutdown', '-h', 'now'], shell=False)


# Select camera + take a photo + save photo in file system and db
def camcapture(pi_cam: picamera, cam_num: int, hike_num: int, photo_index: int, sql_controller: SQLController):
    print('select cam{n}'.format(n=cam_num))
    # logging.info('select cam{n}'.format(n=cam_num))
    if cam_num < 1 or cam_num > 3:
        raise Exception('{n} is an invalid camera number. It must be 1, 2, or 3.'.format(n=cam_num))
    else:
        if cam_num == 1:
            gpio.output(g.SEL_1, True)
            gpio.output(g.SEL_2, False)
            print("cam 1 selected")
            # logging.info('cam 1 selected')
        if cam_num == 2:
            gpio.output(g.SEL_1, False)
            gpio.output(g.SEL_2, False)
            print("cam 2 selected")
            # logging.info('cam 2 selected')
        if cam_num == 3:
            gpio.output(g.SEL_1, True)
            gpio.output(g.SEL_2, True)
            print("cam 3 selected")
            # logging.info('cam 3 selected')
        time.sleep(0.2)  # it takes some time for the pin selection

        # Build image file path
        image_path = '{d}hike{h}/{p}_cam{c}.jpg'.format(d=g.DIRECTORY, h=hike_num, p=photo_index, c=cam_num)
        print(image_path)
        # logging.info(image_path)

        # Take the picture
        pi_cam.capture(image_path)
        sql_controller.set_image_path(cam_num, image_path, hike_num, photo_index)
        print('cam {c} -- picture taken!'.format(c=cam_num))
        logging.info('cam {c} -- picture taken!'.format(c=cam_num))


# Collect raw data from altimeter and compute altitude
# Error check the value, then return value in **meters**
def query_altimeter(sql_ctrl: SQLController) -> float:
    # Logic taken from:
    # https://github.com/adafruit/Adafruit_CircuitPython_MPL3115A2/blob/master/examples/mpl3115a2_simpletest.py
    altitude = round(altimeter.altitude, 2)

    # Safety check for altitude
    # If altitude is above or below these extremes, there is a value error
    # These are rounded ~values for Mt. Everest & Dead Sea
    if altitude > 10000 or altitude < -1000:
        print_and_log('Altitude ERROR: {a}'.format(a=altitude))

        # Change the value of altitude prior to saving it
        altitude = sql_ctrl.get_last_altitude()

        # Save the rowid, so we can go back and change to a future altitude,
        # ensuring the replacement altitude is from this hike (i.e. altimeter fails on 1st picture)
        last_rowid = sql_ctrl.get_last_rowid()
        # This entry in the database will be the next index, hence the +1
        altitude_error_list.append(last_rowid + 1)
    else:
        # We have received a valid altitude
        print_and_log('Altitude is: {a}'.format(a=altitude))

        # First we need to check to see if there are altitude values to go back and fix
        while len(altitude_error_list) > 0:
            # get last ROWID in the list and change the altitude
            rowid = altitude_error_list.pop()
            sql_ctrl.set_altitude_for_rowid(rowid, altitude)

    # We now have an error checked altitude to return
    return altitude


# Main Loop
# ------------------------------------------------------------------------------
def main():
    # Initialize logger that is used while device starts up
    # Once a hike is started the logger switches to a hike specific log
    initialize_startup_logger()

    # Initialize and setup hardware
    rgb_led.turn_off()
    rgb_led.turn_pink()
    piezo.play_power_on_jingle()

    pi_cam = initialize_picamera(g.CAM_RESOLUTION)  # Setup the camera
    initialize_background_turn_off()           # Setup the Off button
    initialize_background_play_pause()              # Setup Play/Pause button
    prev_pause = True

    print('--------------------- POWERED ON ---------------------')
    logging.info('--------------------- POWERED ON ---------------------')
    # As long as initially paused, do not create new hike yet
    while shared.pause:
        # Check for turn off button, LOW battery, or LOW storage
        check_button_turn_off()
        check_low_battery_turn_off()
        check_low_storage_turn_off()

        if round(time.time(), 0) % 60 == 0:
            logging.info('>>>>>Another minute initially PAUSED!')
            print('>>>>>Another minute initially PAUSED!')
        time.sleep(1)
    print('>>>>>Pause button pressed --> FIRST UNPAUSE!')
    logging.info('>>>>>Pause button pressed --> FIRST UNPAUSE!')
    rgb_led.turn_off()

    # Create SQL controller and update hike information
    sql_controller = SQLController(database=g.DB)
    created = sql_controller.will_create_new_hike(g.NEW_HIKE_TIME, g.DIRECTORY)
    if created:     # new hike created: blink teal
        rgb_led.blink_teal_new_hike()
    else:           # continue last hike: blink green
        rgb_led.blink_green_continue_hike()
    time.sleep(1)
    hike_num = sql_controller.get_last_hike_id()
    photo_index = sql_controller.get_last_photo_index_of_hike(hike_num)

    # Switch to the hike specific logfile
    switch_to_hike_logger(hike_num)
    logging.info('--------------------- NEW RECORDING SESSION STARTED ---------------------')

    # Start the time lapse
    # --------------------------------------------------------------------------
    while(True):
        # Check for turn off button, LOW battery, or LOW storage
        check_button_turn_off()
        check_low_battery_turn_off()
        check_low_storage_turn_off()

        # Pause the program if applicable
        while shared.pause:
            if not prev_pause:
                logging.info('>PAUSED!<')
                prev_pause = True
                rgb_led.turn_pink()
                piezo.play_paused_jingle()
            time.sleep(1)
        # Unpause program
        if prev_pause:
            logging.info('>UNPAUSED!<')
            prev_pause = False
            rgb_led.turn_off()
            piezo.play_start_recording_jingle()

        # Read the time as UNIX timestamp
        timestamp = round(time.time(), 0)

        # New picture: increment photo index & add row to database
        photo_index += 1

        # Get altitude before a new entry is added to the database
        altitude = query_altimeter(sql_controller)

        sql_controller.create_new_picture(hike_num, photo_index, timestamp)

        # Take pictures
        camcapture(pi_cam, 1, hike_num, photo_index, sql_controller)
        camcapture(pi_cam, 2, hike_num, photo_index, sql_controller)
        camcapture(pi_cam, 3, hike_num, photo_index, sql_controller)

        # Update the database with metadata for picture & hike
        sql_controller.set_picture_altitude(altitude, hike_num, photo_index)
        sql_controller.set_hike_endtime_picture_count(timestamp, photo_index, hike_num)

        # Blink to notify that the timelapse is still going
        rgb_led.blink_green_new_picture()

        # Log on every 5th picture
        if photo_index % 5 == 0:
            logging.info('Cameras still alive (5 pictures taken)')

        # Wait until 5 seconds have passed since starting to take the pictures
        while time.time() < timestamp + g.CAM_INTERVAL:
            pass


if __name__ == "__main__":
    try:
        main()
    except Exception as error:
        logging.exception('===== Error ===== ')
        logging.exception(error)
        rgb_led.blink_red_quick()
        piezo.play_mario()
