#  ╔═╗╔═╗╔═╗╦═╗╔═╗       ╔═╗═╗ ╦╔═╗╦  ╔═╗╦═╗╔═╗╦═╗
#  ║  ╠═╣╠═╝╠╦╝╠═╣  ───  ║╣ ╔╩╦╝╠═╝║  ║ ║╠╦╝║╣ ╠╦╝
#  ╚═╝╩ ╩╩  ╩╚═╩ ╩       ╚═╝╩ ╚═╩  ╩═╝╚═╝╩╚═╚═╝╩╚═
# =================================================

# Import Modules
import os
import csv
import time
import smbus
import picamera
import RPi.GPIO as gpio


# Get I2C bus
bus = smbus.SMBus(1)

# Initialize GPIO pins
gpio.setmode(gpio.BCM)
gpio.setup(22, gpio.OUT) # switch 1
gpio.setup(23, gpio.OUT) # switch 2
gpio.setup(26, gpio.OUT) # status led1
gpio.setup(17, gpio.OUT) # status led2


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
    time.sleep(0.1)



selectcam(1)
cam1 = picamera.PiCamera()
cam1.resolution = (1024, 768)






# Loop Starts Here
# = = = = = = = = = = = = =

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
  cam1.capture('/home/pi/Desktop/pics/' + str(name) + '_cam2.jpg')
  selectcam(2)
  cam1.capture('/home/pi/Desktop/pics/' + str(name) + '_cam1.jpg')
  selectcam(3)
  cam1.capture('/home/pi/Desktop/pics/' + str(name) + '_cam3.jpg')


  # MPL3115A2 address, 0x60(96)
  # Read data back from 0x00(00), 6 bytes
  # status, tHeight MSB1, tHeight MSB, tHeight LSB, temp MSB, temp LSB
  data = bus.read_i2c_block_data(0x60, 0x00, 6)

  tHeight = ((data[1] * 65536) + (data[2] * 256) + (data[3] & 0xF0)) / 16
  altitude = tHeight / 16.0
  print "Altitude : %.2f m" %altitude
