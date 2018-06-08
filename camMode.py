#! /usr/bin/env python
"""
# ============================================================================
#             __                       _[]_/['']\__n_
#    ___ ___ / /___ _____             |_____.--.__()_|
#   (_-</ -_) __/ // / _ \            |LI  //# \\    |
#  /___/\__/\__/\_,_/ .__/            |    \\__//    |
#                  /_/                '--------------'
# ============================================================================
# > make LEDs flash when taking a picture
# > enable boot into cammode / with button?
# >
"""

import os
import csv
import time
import picamera
from envirophat import light
from envirophat import leds
from envirophat import motion
from envirophat import weather

period = 2.5 # take a picture every 2.5 seconds
index = 0
cam = picamera.PiCamera()
folder = '/home/pi/capra/'

# create csv file and write header
with open(folder + 'meta.csv', 'w') as meta:
    writer = csv.writer(meta)
    newrow = ["index", "time", "altitude", "temperature", "red", "green", "blue", "compass", "acc_x", "acc_y", "acc_z"]
    writer.writerow(newrow)

# check recorded hikes currently on card
def counthikes():
    number = 1
    print 'counting hikes in folder ', folder
    for file in os.listdir(folder):
        if file.startswith('hike'):
            print
            number = number + 1
            print file + 'is instance: ' + str(number)
            print 'new hike is number ', number
    return number

def blink(times):
    for i in range(times):
        leds.on()
        time.sleep(0.05)
        leds.off()
        time.sleep(0.05)

blink(10)

def writedata():
    with open(folder + 'meta.csv', 'a') as meta:
        writer = csv.writer(meta)
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime())
        altitude = round(weather.altitude() + 90, 2)
        temperature = round(weather.temperature(), 2)
        heading = motion.heading()
        accx = round(motion.accelerometer()[0], 2)
        accy = round(motion.accelerometer()[1], 2)
        accz = round(motion.accelerometer()[2], 2)
        red = light.rgb()[0]
        green = light.rgb()[1]
        blue = light.rgb()[2]
        newrow = ["{:04}".format(index), timestamp, altitude, temperature, red, green, blue, heading, accx, accy, accz]
        print newrow
        writer.writerow(newrow)


hikeno = counthikes()
folder = folder + 'hike' + str(hikeno) + '/' # change directory for actual hike record
os.makedirs(folder)

cam.capture(folder + str("%04d" % index) + '.jpg')
writedata()
print 'photo taken'
print '========================'
index = index + 1
time.sleep(2)
# ============================================================================
#     __
#    /'/__  ,__  ,__
#   /'/ _ \/ _ \/ _ \
#  /_/\___/\___/ .__/
#             /_/
# ============================================================================
while(True):
    priortime = time.time()
    print 'taking photo ...'
    cam.capture(folder + str("%04d" % index) + '.jpg')
    print 'photo taken!'
    writedata()
    index = index + 1
    blink(2)
    # Nap time
    nowtime = time.time()
    naptime = period - (nowtime - priortime)
    time.sleep(naptime)
