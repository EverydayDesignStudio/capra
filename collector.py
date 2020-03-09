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
import busio                 # For interfacing with DS3231 Real Time Clock
import adafruit_ds3231       #
from threading import Thread # For threading
import subprocess            # For calling shutdown


# Import custom modules
import shared  # For shared variables between main code and button interrupts
from classes.button import Button  # For threading interrupts for button presses
from classes.capra_data_types import Picture, Hike
from classes.sql_controller import SQLController  # For interacting with the DB
from classes.piezo_player import PiezoPlayer  # For playing sounds
from classes.led_player import RedBlueLED  # For controlling LED on Buttonboard


DB = '/home/pi/capra-storage/capra_camera.db'
DIRECTORY = '/home/pi/capra-storage/'

# Pin configurations
BUTTON_PLAYPAUSE = 17   # BOARD - 11
SEL_1 = 22              # BOARD - 15
SEL_2 = 23              # BOARD - 16
LED_BLUE = 26           # BOARD - 33
LED_RED = 13            # BOARD - 37
PIEZO = 12              # BOARD - 32
LDO = 6                 # BOARD - 31

# Hike specifics
RESOLUTION = (1280, 720)
# NEW_HIKE_TIME = 43200   # 12 hours
# NEW_HIKE_TIME = 21600   # 6 hours
# NEW_HIKE_TIME = 16200   # 4.5 hours
# NEW_HIKE_TIME = 10800   # 3 hours
NEW_HIKE_TIME = 9000      # 2.5 hours

gpio.setwarnings(False)             # Turn off GPIO warnings
gpio.setmode(gpio.BCM)              # Broadcom pin numbers
gpio.setup(SEL_1, gpio.OUT)         # select 1
gpio.setup(SEL_2, gpio.OUT)         # select 2
gpio.setup(LDO, gpio.IN, pull_up_down=gpio.PUD_DOWN)  # low dropout (low power detection) from PowerBoost
piezo = PiezoPlayer(PIEZO)          # piezo buzzer
red_blue_led = RedBlueLED(LED_RED, LED_BLUE)  # red and blue LED
altitude_error_list = []            # empty list for ROWIDs for altitudes taken from previous record


# Helper functions
# ------------------------------------------------------------------------------
def print_and_log(message: str):
    print(message)
    logging.info(message)


# Set the system time from the DS3231 Real Time Clock
def set_system_time_from_RTC():
    print_and_log('Getting time from hardware clock')

    # Get the hardware clock time
    stream = os.popen('sudo hwclock -r')
    hwclock = stream.read()
    print_and_log("Hardware clock is:")
    print_and_log(hwclock)

    # Set date from hardware clock time
    os.popen('sudo date --set="{hwc}"'.format(hwc=hwclock))

    stream = os.popen('date')
    date = stream.read()
    print_and_log("Date is now:")
    print_and_log(date)


# Get the time from the DS3231 Real Time Clock
def get_RTC_time(I2C):
    rtc = adafruit_ds3231.DS3231(I2C)
    logging.info('Time from RTC(DS3231) is: {t}'.format(t=rtc.datetime))
    logging.info('Time from RTC(DS3231) is: {t}'.format(t=time.mktime(rtc.datetime)))
    time.mktime(rtc.datetime)
    logging.info('Time from Raspberry Pi clock: {t}'.format(t=time.time()))
    # return(t)


# Initialize and return picamera object
def initialize_picamera(resolution: tuple) -> picamera:
    logging.info('Initializing camera objects')
    gpio.output(SEL_1, False)
    gpio.output(SEL_2, False)
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


# Start threading interrupt for Play/pause button
def initialize_background_play_pause():
    PP_INTERRUPT = Button(BUTTON_PLAYPAUSE)  # Create class
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


# Check if camera battery is low and turn off camera if it is
def check_low_battery_turn_off():
    print('The battery status is: {n}'.format(n=gpio.input(LDO)))
    logging.info('The battery status is: {n}'.format(n=gpio.input(LDO)))
    if (gpio.input(LDO) == gpio.LOW):
        red_blue_led.turn_blue()
        piezo.play_stop_recording_jingle()
        time.sleep(10)
        subprocess.call(['shutdown', '-h', 'now'], shell=False)


# Select camera + take a photo + save photo in file system and db
def camcapture(pi_cam: picamera, cam_num: int, hike_num: int, photo_index: int, sql_controller: SQLController):
    print('select cam{n}'.format(n=cam_num))
    logging.info('select cam{n}'.format(n=cam_num))
    if cam_num < 1 or cam_num > 3:
        raise Exception('{n} is an invalid camera number. It must be 1, 2, or 3.'.format(n=cam_num))
    else:
        if cam_num == 1:
            gpio.output(SEL_1, True)
            gpio.output(SEL_2, False)
            print("cam 1 selected")
            logging.info('cam 1 selected')
        if cam_num == 2:
            gpio.output(SEL_1, False)
            gpio.output(SEL_2, False)
            print("cam 2 selected")
            logging.info('cam 2 selected')
        if cam_num == 3:
            gpio.output(SEL_1, True)
            gpio.output(SEL_2, True)
            print("cam 3 selected")
            logging.info('cam 3 selected')
        time.sleep(0.2)  # it takes some time for the pin selection

        # Build image file path
        image_path = '{d}hike{h}/{p}_cam{c}.jpg'.format(d=DIRECTORY, h=hike_num, p=photo_index, c=cam_num)
        print(image_path)
        logging.info(image_path)

        # Take the picture
        pi_cam.capture(image_path)
        sql_controller.set_image_path(cam_num, image_path, hike_num, photo_index)
        print('cam {c} -- picture taken!'.format(c=cam_num))
        logging.info('cam {c} -- picture taken!'.format(c=cam_num))


# Collect raw data from altimeter and compute altitude
# Error check the value, then return. Return value in meters
def query_altimeter(bus: smbus, sql_ctrl: SQLController) -> float:
    # Logic taken from:
    # https://www.instructables.com/id/Raspberry-Pi-MPL3115A2-Precision-Altimeter-Sensor--1/

    # MPL3115A2 address, 0x60(96) - Select control register, 0x26(38)
    # 0xB9(185)	Active mode, OSR = 128(0x80), Altimeter mode
    bus.write_byte_data(0x60, 0x26, 0xB9)

    # MPL3115A2 address, 0x60(96)
    # Read data back from 0x00(00), 6 bytes
    # status, tHeight MSB1, tHeight MSB, tHeight LSB, temp MSB, temp LSB
    data = bus.read_i2c_block_data(0x60, 0x00, 6)
    tHeight = ((data[1] * 65536) + (data[2] * 256) + (data[3] & 0xF0)) / 16
    altitude = round(tHeight / 16.0, 2)

    # Safety check for altitude
    # If altitude is above or below these extremes, there is an error value
    # These are chosen instead of Mt. Everest & Dead Sea due to the issue that
    # the altimeter is acting more as a relative input, the specific amount doesn't
    # matter as much as showing higher or lower than another location
    if altitude > 600000 or altitude < -60000:
        print_and_log('Altitude ERROR: {a}'.format(a=altitude))

        # Change the value of altitude prior to saving it
        altitude = sql_ctrl.get_last_altitude()

        # Save the rowid, so we can go back and change to a future altitude,
        # ensuring the altitude was from this hike (i.e. altimeter fails on 1st picture)
        last_error_rowid = sql_ctrl.get_last_rowid()
        altitude_error_list.append(last_error_rowid)
    else:
        # We have received a valid altitude
        print_and_log('Altitude is: {a}'.format(a=altitude))

        # First we need to check to see if there are altitude values to go back and fix
        while (len(altitude_error_list) > 0):
            # get last ROWID in the list and change the altitude
            rowid = altitude_error_list.pop()
            sql_ctrl.set_altitude_for_rowid(rowid, altitude)

    # We now have an error checked altitude to return
    return altitude


# Main Loop
# ------------------------------------------------------------------------------
def main():
    # Initialize logger that is used while startup up device
    # Once a hike is started the logger switches to a hike specific log
    initialize_startup_logger()

    # Set the system time to the DS3231 real time clock
    set_system_time_from_RTC()

    # Initialize and setup hardware
    i2c_bus = smbus.SMBus(1)                        # Setup I2C bus
    # i2c = busio.I2C(3, 2)                         # Setup I2C for DS3231
    # get_RTC_time(i2c)                             # Update system time from RTC
    red_blue_led.turn_off()
    red_blue_led.turn_red()
    piezo.play_power_on_jingle()

    pi_cam = initialize_picamera(RESOLUTION)  # Setup the camera
    initialize_background_play_pause()              # Setup play/pause button
    prev_pause = True

    # As long as initially paused, do not create new hike yet
    print("Waiting for initial unpause...")
    logging.info("Waiting for initial unpause...")
    while(shared.pause):
        # Check if battery is LOW and turn off the RPi if LOW
        check_low_battery_turn_off()
        if(not prev_pause):
            logging.info('Pause button pressed --> PAUSED!')
            prev_pause = True
        logging.info('>>>>>PAUSED!<<<<<')
        print('>>>>>PAUSED!<<<<<')
        time.sleep(1)
    print("Initial unpause!")
    logging.info('Pause button pressed --> UNPAUSE!')
    red_blue_led.turn_off()

    # Create SQL controller and update hike information
    sql_controller = SQLController(database=DB)
    created = sql_controller.will_create_new_hike(NEW_HIKE_TIME, DIRECTORY)
    if created:     # new hike created; blink 6 times in purple
        red_blue_led.blink_purple_new_hike()
        # os.chmod(DIRECTORY, 766) # set permissions to be read and written to when run manually
        # os.chmod(DB, 766)
    else:           # continue last hike; blink 6 times in red
        red_blue_led.blink_red_continue_hike()
    time.sleep(1)
    hike_num = sql_controller.get_last_hike_id()
    photo_index = sql_controller.get_last_photo_index_of_hike(hike_num)

    # Switch to the hike specific logfile
    switch_to_hike_logger(hike_num)
    logging.info('--------------------- NEW RECORDING SESSION STARTED ---------------------')

    # Start the time lapse
    # --------------------------------------------------------------------------
    while(True):
        # Check if battery is LOW and turn off the RPi if LOW
        check_low_battery_turn_off()

        # Pause the program if applicable
        while(shared.pause):
            if(not prev_pause):
                logging.info('Paused')
                prev_pause = True
                red_blue_led.turn_red()
                piezo.play_paused_jingle()
            print(">PAUSED!<")
            logging.info(">PAUSED!<")
            time.sleep(1)
        # Unpause program
        if(prev_pause):
            logging.info('Unpaused')
            prev_pause = False
            red_blue_led.turn_off()
            piezo.play_start_recording_jingle()

        # Read the time as UNIX timestamp
        # current_time = get_RTC_time(i2c)
        current_time = time.time()

        # New picture: increment photo index & add row to database
        photo_index += 1

        # Get altitude before a new entry is added to the database
        altitude = query_altimeter(i2c_bus, sql_controller)

        sql_controller.create_new_picture(hike_num, photo_index, current_time)

        # Take pictures
        camcapture(pi_cam, 1, hike_num, photo_index, sql_controller)
        camcapture(pi_cam, 2, hike_num, photo_index, sql_controller)
        camcapture(pi_cam, 3, hike_num, photo_index, sql_controller)

        # Update the database with metadata for picture & hike
        sql_controller.set_picture_time_altitude(altitude, hike_num, photo_index)
        sql_controller.set_hike_endtime_picture_count(photo_index, hike_num)

        timestamp = time.time()  # OLD: this takes the time from the RPi, not the DS3221
        # timestamp = get_RTC_time(i2c)

        # Blink to notify that the timelapse is still going
        red_blue_led.blink_blue_new_picture()

        # Log on every 5th picture
        if (photo_index % 5 == 0):
            # piezo.play_still_recording_jingle()
            logging.info('Cameras still alive (5 pictures taken)')

        # Wait until 2.5 seconds have passed since last picture
        # while(get_RTC_time(i2c) < timestamp + 2.5):
        while(time.time() < timestamp + 2.5):
            pass


if __name__ == "__main__":
    try:
        main()
    except Exception as error:
        logging.exception('===== Error ===== ')
        logging.exception(error)
        red_blue_led.blink_red_quick()
        piezo.play_mario()
