
#!/usr/bin/python

# Change channel of TCA9548A
# Example: sudo ./multiplexer_channel.py 0

# import smbus
import time
# import sys
#
# I2C_address = 0x77
# I2C_bus_number = 1
# I2C_ch_0 = 0b00000001
# I2C_ch_1 = 0b00000010
# I2C_ch_2 = 0b00000100
# I2C_ch_3 = 0b00001000
# I2C_ch_4 = 0b00010000
# I2C_ch_5 = 0b00100000
# I2C_ch_6 = 0b01000000
# I2C_ch_7 = 0b10000000
#
# def I2C_setup(i2c_channel_setup):
#     bus = smbus.SMBus(I2C_bus_number)
#     bus.write_byte(I2C_address,i2c_channel_setup)
#     time.sleep(0.1)
#     print "TCA9548A I2C channel status:", bin(bus.read_byte(I2C_address))
#
# I2C_setup(int(sys.argv[1]))




# =============================================================================
# =============================================================================
import picamera
import RPi.GPIO as gpio

gpio.setmode(gpio.BCM)
gpio.setup(22, gpio.OUT) # FSA switch 1
gpio.setup(23, gpio.OUT) # FSA switch 2
gpio.setup(24, gpio.OUT) # TCA9548A switch A0
gpio.setup(25, gpio.OUT) # TCA9548A switch A1
gpio.setup(27, gpio.OUT) # status led

def selectcam(_cam):
    if _cam < 1 or _cam > 3:
        print('[selectcam] invalid cam number!')
    else:
        if _cam == 1:
             gpio.output(22, False)
             gpio.output(23, False)
             gpio.output(24, False)
             gpio.output(25, False)
        if _cam == 2:
             gpio.output(22, True)
             gpio.output(23, False)
             gpio.output(24, True)
             gpio.output(25, False)
        if _cam == 3:
             gpio.output(22, True)
             gpio.output(23, True)
             gpio.output(24, False)
             gpio.output(25, True)






# selectcam(1)
# cam1 = picamera.PiCamera()
# cam1.resolution = (1024, 768)
#
# time.sleep(2)
# gpio.output(27, True)
# time.sleep(1)
# gpio.output(27, False)


select = raw_input(int("cam no: "))
selectcam(select)
time.sleep(0.5)

cam2 = picamera.PiCamera()
cam2.resolution = (1024, 768)

time.sleep(1)
#cam2.capture('/home/pi/Desktop/image.jpg')

cam2.start_preview()
time.sleep(6)
# Camera warm-up time

#
# for i in range(2):
#     gpio.output(27, True)
#     time.sleep(0.25)
#     gpio.output(27, False)
#     time.sleep(0.25)

#
# for cam in range(1, 4):
#     selectcam(cam)
#     camera.capture(str(cam) + '.jpg')
