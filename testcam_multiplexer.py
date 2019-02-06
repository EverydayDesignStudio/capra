from time import sleep
import picamera
import RPi.GPIO as gpio

gpio.setmode(gpio.BCM)
gpio.setup(22, gpio.OUT) # FSA switch 1
gpio.setup(23, gpio.OUT) # FSA switch 2
gpio.setup(27, gpio.OUT) # status led

selectcam(1)
cam1 = picamera.PiCamera()
cam1.resolution = (1024, 768)

sleep(2)
gpio.output(27, True)
sleep(1)
gpio.output(27, False)



selectcam(2)
cam2 = picamera.PiCamera()
cam2.resolution = (1024, 768)

#camera.start_preview()
# Camera warm-up time
sleep(2)

for i in range(15):
    gpio.output(27, True)
    sleep(0.25)
    gpio.output(27, False)
    sleep(0.25)

#
# for cam in range(1, 4):
#     selectcam(cam)
#     camera.capture(str(cam) + '.jpg')

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
