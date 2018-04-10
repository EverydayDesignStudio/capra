# ============================================================================
#             __
#    ___ ___ / /___ _____
#   (_-</ -_) __/ // / _ \
#  /___/\__/\__/\_,_/ .__/
#                  /_/
# ============================================================================

import picamera
import time
import os
import csv
from envirophat import light
from envirophat import leds
from envirophat import motion
from envirophat import weather

index = 0
hikeno = 1

cam = picamera.PiCamera()
cam.resolution(720, 405)

# check recorded hikes currently on card
for file in listdir('.'):
    if os.path.isdir(file) and file.startswith('Hike'):
        hikeno + 1
        print str(hikeno)

folder = 'Hike' + hikeno + '/' # change directory for actual hike record

for i in range(3):
    leds.off()
    time.sleep(1)
    leds.on()
    time.sleep(0.5)

# ============================================================================
#     __
#    / /__  ___  ___
#   / / _ \/ _ \/ _ \
#  /_/\___/\___/ .__/
#             /_/
# ============================================================================
while(True):




    name = folder + 'Hikex' + str("%04d" % index) + '.jpg'
    photo = cam.takePhoto()
    photo.save(name)
    #cam.capture(name)
    with open(folder + 'metatest.csv', 'a') as meta:
        writer = csv.writer(meta)
        altitude = weather.altitude() + 90
        writer.writerow("{:04}".format(index), round(altitude, 2))


    index = index + 1

    # Nap time
    time.sleep(2)
