#
#    _________ _____  _________ _
#   / ___/ __ `/ __ \/ ___/ __ `/
#  / /__/ /_/ / /_/ / /  / /_/ /
#  \___/\__,_/ .___/_/   \__,_/
#           /_/
# Script to run on the Explorer camera unit. Takes pictures with
# three picameras through the Capra cam multiplexer board
# ===============================

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
SEL_1 = 22
SEL_2 = 23
LED_GREEN = 24
LED_BTM = 26
LED_AMBER = 27

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

def blink(pin, repeat, interval):
    on = False
    off = True
    if pin = LED_BTM:
        on = True
        off = False
    for i in range(repeat):
        gpio.output(pin, on)
        time.sleep(interval)
        gpio.output(pin, off)
        time.sleep(interval)

def simplecounthikes():
    print('simplecounthikes() - Counting previous hikes')
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
    print('timesincehike()')
    print('===============')
    csvfile = dir + 'hike' + str(_hikeno) + '/' 'meta.csv'
    print('reading from ', csvfile)
    timesince = 0
    lasthikephoto = 0
    lasthikedate = 0
    with open(csvfile, 'r') as meta:
        reader = csv.reader(meta)
        for row in reader: # iterate over rows in meta.csv
            try:
                print(row)
                lasthikedate = float(row[1])
                lasthikephoto = int(row[0])
            except():
                pass # empty rows
        print('last hike ended at: ', str(lasthikedate))
        # check if the last hike started less than half a day ago
        timesince = time.time() - lasthikedate
    print('time since last: ', str(timesince))
    return timesince, lasthikephoto

# Select Cam Definition
def selectcam(_cam):
    print('selectcam( ', _cam, ' )')
    print('===============')
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

def writedata(index, timestamp, altitude):
    with open(dir + folder + 'meta.csv', 'a') as meta:
        writer = csv.writer(meta)
        newrow = [index, timestamp, altitude]
        print newrow
        writer.writerow(newrow)

blink(LED_GREEN, 2, 0.25) #computer says hello
blink(LED_AMBER, 2, 0.25) #computer says hello

# Initialize camera object
selectcam(3)
cam = picamera.PiCamera()
cam.resolution = (1280, 720)

hikeno = simplecounthikes() # Count existing hikes
# > check time since last hike
sincelast = timesincehike(hikeno - 1)[0]
# > determine whether to create new hike entry or continue on last hike
if(sincelast > 43200):
    # create new hike folder
    print('creating new hike:')
    folder = 'hike' + str(hikeno - 1) + '/' # change directory for actual hike record
    os.makedirs(dir + folder)
    blink(LED_GREEN, 2, 0.4)
else:
    # append to last hike
    print('continuing last hike:')
    # retrieve last photo number
    hikeno -= 1
    photono = timesincehike(hikeno)[1]
    blink(LED_AMBER, 2, 0.4)

folder = 'hike' + str(hikeno) + '/' # change directory for actual hike record

# Create csv file and write header
csvfile = dir + folder + 'meta.csv'
with open(csvfile, 'w') as meta:
    writer = csv.writer(meta)
    newrow = ["index", "time", "altitude"]
    print "HEADER ", newrow
    writer.writerow(newrow)

# Loop Starts Here
# =================================================
while(1):
    # Query Altimeter first (takes a while)
    # -------------------------------------
    # MPL3115A2 address, 0x60(96) - Select control register, 0x26(38)
 # 0xB9(185)	Active mode, OSR = 128(0x80), Altimeter mode
    bus.write_byte_data(0x60, 0x26, 0xB9)

    # Take pictures
    # -------------------------------------
    selectcam(1)
    cam.capture(dir + folder + str(photono) + '_cam1.jpg')
    print("cam1 - picture taken!")
    selectcam(2)
    cam.capture(dir + folder + str(photono) + '_cam2.jpg')
    print("cam2 - picture taken!")
    selectcam(3)
    cam.capture(dir + folder + str(photono) + '_cam3.jpg')
    print("cam3 - picture taken!")

    # MPL3115A2 address, 0x60(96)
    # Read data back from 0x00(00), 6 bytes
    # status, tHeight MSB1, tHeight MSB, tHeight LSB, temp MSB, temp LSB
    # -------------------------------------
    data = bus.read_i2c_block_data(0x60, 0x00, 6)

    tHeight = ((data[1] * 65536) + (data[2] * 256) + (data[3] & 0xF0)) / 16
    altitude = tHeight / 16.0
    print "Altitude : %.2f m" %altitude

    # Write Metadata
    # -------------------------------------
    timestamp = time.time()
    writedata(photono, timestamp, altitude)

    # Increase increment
    # -------------------------------------
    photono += 1

    # Blink on every fourth picture
    # -------------------------------------
    if (photono % 4):
        blink(LED_GREEN, 1, 0.2)

    # wait until 2.5 seconds have passed since last picture
    # -------------------------------------
    while(time.time() < timestamp + 2.5):
        pass
