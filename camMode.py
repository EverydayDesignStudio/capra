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
#cam.resolution(720, 405)

# check recorded hikes currently on card
def counthikes():
    number = 1
    for file in os.listdir('..'):
        if file.startswith('Hike'):
            print
            number = number + 1
            print file + 'is instance: ' + str(number)
    return number

def blink(times):
    for i in range(times):
        leds.on()
        time.sleep(0.05)
        leds.off()
        time.sleep(0.05)


hikeno = counthikes()

folder = '../Hike' + str(hikeno) + '/' # change directory for actual hike record
os.makedirs(folder)

# for i in range(3):
#     leds.off()
#     time.sleep(1)
#     leds.on()
#     time.sleep(0.5)

cam.capture(folder + 'Hike' + str(hikeno) + '-' + str("%04d" % index) + '.jpg')
with open(folder + 'metatest.csv', 'w') as meta:
    writer = csv.writer(meta)
    altitude = weather.altitude() + 90
    writer.writerow(["{:04}".format(index), round(altitude, 2)])
    print 'photo taken'
    print ["{:04}".format(index), round(altitude, 2)]
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
        altitude = weather.altitude() + 90
        temperature = weather.temperature()
        newrow = ["{:04}".format(index), round(altitude, 2), round(temperature, 2)]
        writer.writerow(newrow)

        print 'wrote ' + str(newrow)
        print '========================'
        blink(3)

    index = index + 1

    # Nap time
    nowtime = time.time()
    naptime = period - (nowtime - priortime)
    time.sleep(naptime)
