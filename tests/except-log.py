# import RPi.GPIO as gpio      # For interfacing with the pins of the Raspberry Pi
import logging


def initialize_logger():
    # logname = 'log-hike' + str(hike_num) + '.log'
    logname = '/home/pi/Desktop/except-log-test.log'
    logging.basicConfig(filename=logname, level=logging.DEBUG, format='%(asctime)s %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p')
    logging.info('==== START')


initialize_logger

try:
    gpio.setup(1, gpio.OUT)
except Exception as error:
    logging.exception('message')
    logging.exception(error)
