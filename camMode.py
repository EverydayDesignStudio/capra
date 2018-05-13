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

# check recorded hikes currently on card
def counthikes():
    number = 1
    print 'counting hikes in folder ', folder
    for file in os.listdir(folder):
        if file.startswith('Hike'):
            print
            number = number + 1
            print file + 'is instance: ' + str(number)
            print '-_-_-_-_-_-_'
            print 'new hike is number ', number
    return number

def blink(times):
    for i in range(times):
        leds.on()
        time.sleep(0.05)
        leds.off()
        time.sleep(0.05)

blink(10)

hikeno = counthikes()
folder = folder + 'Hike' + str(hikeno) + '/' # change directory for actual hike record
os.makedirs(folder)

cam.capture(folder + 'Hike' + str(hikeno) + '-' + str("%04d" % index) + '.jpg')
with open(folder + 'metatest.csv', 'w') as meta:
    writer = csv.writer(meta)
    altitude = round(weather.altitude() + 90, 2)
    temperature = round(weather.temperature(), 2)
    red = lights.rgb()[0]
    green = lights.rgb()[1]
    blue = lights.rgb()[2]
    newrow = ["{:04}".format(index), altitude, temperature, red, green, blue]
    writer.writerow(newrow)
    print 'photo taken'
    print newrow
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

    #name = folder + 'Hikex' + str("%04d" % index) + '.jpg'
    #photo = cam.takePhoto()
    #photo.save(name)
    priortime = time.time()
    print 'taking photo ...'
    cam.capture(folder + 'Hike' + str(hikeno) + '-' + str("%04d" % index) + '.jpg')
    print 'photo taken!'
    with open(folder + 'metatest.csv', 'a') as meta:
        writer = csv.writer(meta)
        altitude = round(weather.altitude() + 90, 2)
        temperature = round(weather.temperature(), 2)
        red = lights.rgb()[0]
        green = lights.rgb()[1]
        blue = lights.rgb()[2]
        newrow = ["{:04}".format(index), altitude, temperature, red, green, blue]
        writer.writerow(newrow)
        print 'photo taken'
        print [newrow]
        print '========================'
        blink(2)
    index = index + 1

    # Nap time
    nowtime = time.time()
    naptime = period - (nowtime - priortime)
    time.sleep(naptime)
