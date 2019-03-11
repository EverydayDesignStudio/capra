
#!/usr/bin/python

import time
import picamera
import RPi.GPIO as gpio

folder = ""


# =============================================================================
# =============================================================================


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
             # gpio.output(24, False)
             # gpio.output(25, False)
        if _cam == 2:
             gpio.output(22, True)
             gpio.output(23, False)
             # gpio.output(24, False)
             # gpio.output(25, True)
        if _cam == 3:
             gpio.output(22, True)
             gpio.output(23, True)
             # gpio.output(24, True)
             # gpio.output(25, False)
    time.sleep(0.1)





# selectcam(1)
# cam1 = picamera.PiCamera()
# cam1.resolution = (1024, 768)
#
# time.sleep(2)
# gpio.output(27, True)
# time.sleep(1)
# gpio.output(27, False)

print("======[]")
print("=={O}===")
print("========")
# select = raw_input("cam no: ")
# selectcam(int(select))



selectcam(1)
cam1 = picamera.PiCamera()
cam1.resolution = (1024, 768)

# selectcam(3)
# cam3 = picamera.PiCamera()
# cam3.resolution = (1024, 768)

name = 0

while(1):
    time.sleep(1)
    selectcam(1)
    cam1.capture('/home/pi/Desktop/pics/cam2_' + str(name) + '.jpg')
    time.sleep(0.2)
    selectcam(2)
    cam1.capture('/home/pi/Desktop/pics/cam1_' + str(name) + '.jpg')
    time.sleep(0.2)
    selectcam(3)
    cam1.capture('/home/pi/Desktop/pics/cam3_' + str(name) + '.jpg')
    time.sleep(0.2)
    name += 1
    time.sleep(2.5)


# selectcam(3)
# cam1.capture('/home/pi/Desktop/cam3.jpg')


# cam2.start_preview()

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
