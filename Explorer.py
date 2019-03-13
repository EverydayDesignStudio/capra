#   __ _  _  _  _           __\ / _     _  _  __ _
#  /  |_||_)|_)|_|   ---   |_  X |_)|  / \|_)|_ |_)
#  \__| ||  | \| |         |__/ \|  |__\_/| \|__| \
# =================================================

# Import Modules
import os
import csv
import time
import smbus
import picamera
import datetime
import RPi.GPIO as gpio

# this is not a test

# Get I2C bus
bus = smbus.SMBus(1)

# Initialize GPIO pins
gpio.setmode(gpio.BCM)
gpio.setup(22, gpio.OUT) # switch 1
gpio.setup(23, gpio.OUT) # switch 2
gpio.setup(26, gpio.OUT) # status led1
gpio.setup(17, gpio.OUT) # status led2

# Set Variables
dir = '/home/pi/Desktop/pics/'
photono = 0

# Set Definitions
def counthikes():
    number = 1
    for file in os.listdir(dir):
        if file.startswith('hike'):
            print
            number = number + 1
            print file + 'is instance: ' + str(number)
            print 'new hike is number ', number
    return number

# Select Cam Definition
def selectcam(_cam):
    if _cam < 1 or _cam > 3:
        print('[selectcam] invalid cam number!')
    else:
        if _cam == 1:
             gpio.output(22, False)
             gpio.output(23, False)

        if _cam == 2:
             gpio.output(22, True)
             gpio.output(23, False)

        if _cam == 3:
             gpio.output(22, True)
             gpio.output(23, True)
    chronos.sleep(0.1)


def writedata(index, time, altitude):
    with open(dir + folder + 'meta.csv', 'a') as meta:
        writer = csv.writer(meta)
        newrow = [index, time, altitude]
        print newrow
        writer.writerow(newrow)


# Initialize camera object
selectcam(1)
cam1 = picamera.PiCamera()
cam1.resolution = (1024, 768)

# Create new folder
hikeno = counthikes()
folder = 'hike' + str(hikeno) + '/' # change directory for actual hike record
os.makedirs(dir + folder)

# Create csv file and write header
csvfile = dir + folder + 'meta.csv'
with open(csvfile, 'w') as meta:
    writer = csv.writer(meta)
    newrow = ["index", "time", "altitude", "tbd"]
    print "HEADER ", newrow
    writer.writerow(newrow)



# Loop Starts Here
# =================================================

while(1):
  # Query Altimeter first (takes a while)
  # -------------------------------------
  # MPL3115A2 address, 0x60(96)
  # Select control register, 0x26(38)
  #		0xB9(185)	Active mode, OSR = 128, Altimeter mode
  bus.write_byte_data(0x60, 0x26, 0xB9)

  # Take pictures
  # -------------------------------------
  selectcam(1)
  cam1.capture(dir + folder + str(photono) + '_cam2.jpg')
  selectcam(2)
  cam1.capture(dir + folder + str(photono) + '_cam1.jpg')
  selectcam(3)
  cam1.capture(dir + folder + str(photono) + '_cam3.jpg')



  # MPL3115A2 address, 0x60(96)
  # Read data back from 0x00(00), 6 bytes
  # status, tHeight MSB1, tHeight MSB, tHeight LSB, temp MSB, temp LSB
  data = bus.read_i2c_block_data(0x60, 0x00, 6)

  tHeight = ((data[1] * 65536) + (data[2] * 256) + (data[3] & 0xF0)) / 16
  altitude = tHeight / 16.0
  print "Altitude : %.2f m" %altitude

  # Write Metadata
  # -------------------------------------
  time = time.time()
  writedata(photono, time, altitude)

  # Increase increment
  # -------------------------------------
  photono += 1
