# Import Modules
import os
import csv
import time
import smbus
import picamera
import datetime
import RPi.GPIO as gpio

# Pin configuration
BUTTON_PLAYPAUSE = 4
LED_GREEN = 24
LED_AMBER = 27
LED_BTM = 26
SEL_1 = 22
SEL_2 = 23

# Get I2C bus
bus = smbus.SMBus(1)

# Initialize GPIO pins
gpio.setmode(gpio.BCM)
gpio.setup(SEL_1, gpio.OUT) # select 1
gpio.setup(SEL_2, gpio.OUT) # select 2
gpio.setup(LED_GREEN, gpio.OUT) # status led1
gpio.setup(LED_AMBER, gpio.OUT) # status led2
gpio.setup(LED_BTM, gpio.OUT) # status led3

gpio.output(LED_GREEN, True)
time.sleep(0.1)
gpio.output(LED_AMBER, True)
time.sleep(0.1)
gpio.output(LED_BTM, False)


# Set Variables
dir = '/home/pi/Desktop/pics/'
photono = 0

# Set Definitions
def isLast(itr):
  old = itr.next()
  for new in itr:
    yield False, old
    old = new
  yield True, old


def simplecounthikes():
    print('counthikes() - Counting previous hikes')
    print('======================================')
    number = 1
    for file in os.listdir(dir):
        if file.startswith('hike'):
            print
            number = number + 1
            print(file + 'is instance: ' + str(number))
            print('new hike is number ', number)
    folder = 'hike' + str(number) + '/' # change directory for actual hike record
    os.makedirs(dir + folder)
    gpio.output(LED_AMBER, False)
    time.sleep(0.4)
    gpio.output(LED_AMBER, True)
    time.sleep(0.4)
    gpio.output(LED_AMBER, False)
    time.sleep(0.4)
    gpio.output(LED_AMBER, True)
    return number



def counthikes():
    print('counthikes() - Counting previous hikes')
    print('======================================')
    number = 1
    for file in os.listdir(dir):
        if file.startswith('hike'):
            print
            number = number + 1
            print(file + 'is instance: ' + str(number))
            print('new hike is number ', number)
    return number

def timesincehike(_hikeno):
    csvfile = dir + 'hike' + str(_hikeno) + '/' 'meta.csv'
    with open(csvfile, 'r') as meta:
        reader = csv.reader(meta)
        lasthikephoto = 0
        lasthikedate = 0
        row_count = sum(1 for row in reader)
        print("row count:", str(row_count))
        for row in reader:
            print(row[row_count - 1])
            lasthikedate = float(row[row_count])
            lasthikephoto = int(row[row_count])
            break
        print('last hike ended at: ', str(lasthikedate))
        # check if the last hike started less than half a day ago
        timesince = time.time() - lasthikedate
        print('time since last: ', str(timesince))
        if (timesince < 43200):
            print('continuing last hike:')
            gpio.output(LED_GREEN, False)
            time.sleep(0.4)
            gpio.output(LED_GREEN, True)
            number = number - 1
            print('hike ', str(number))
            photono = lasthikephoto
            print('@', str(photono))
            folder = 'hike' + str(number) + '/' # change directory for actual hike record
        else:
            gpio.output(LED_AMBER, False)
            time.sleep(0.4)
            gpio.output(LED_AMBER, True)
            folder = 'hike' + str(number) + '/' # change directory for actual hike record
            os.makedirs(dir + folder)


# Select Cam Definition
def selectcam(_cam):
    if _cam < 1 or _cam > 3:
        print('[selectcam] invalid cam number!')
    else:
        if _cam == 1:
             gpio.output(SEL_1, False)
             gpio.output(SEL_2, False)

        if _cam == 2:
             gpio.output(SEL_1, True)
             gpio.output(SEL_2, False)

        if _cam == 3:
             gpio.output(SEL_1, True)
             gpio.output(SEL_2, True)
        time.sleep(0.1)
