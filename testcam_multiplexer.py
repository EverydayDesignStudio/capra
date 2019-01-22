from time import sleep
import picamera
import RPi.GPIO as gpio

gpio.setmode(gpio.BCM)
gpio.setup(22, gpio.OUT)
gpio.setup(23, gpio.OUT)

camera = picamera.PiCamera()
camera.resolution = (1024, 768)
#camera.start_preview()
# Camera warm-up time
sleep(2)

for cam in range 4:
    selectcam(cam)
    camera.capture(str(cam) + '.jpg')

def selectcam(_cam):
    if _cam < 1 or _cam > 3:
        print '[selectcam] invalid cam number!'
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
