import time  # For time keeping
import picamera  # For interfacting with the PiCamera
import RPi.GPIO as gpio  # For


SEL_1 = 22
SEL_2 = 23
LED_GREEN = 24
LED_BTM = 26
LED_AMBER = 27

# Initialize GPIO pins
gpio.setmode(gpio.BCM)
gpio.setup(SEL_1, gpio.OUT)  # select 1
gpio.setup(SEL_2, gpio.OUT)  # select 2
gpio.setup(LED_GREEN, gpio.OUT)  # status led1
gpio.setup(LED_AMBER, gpio.OUT)  # status led2
gpio.setup(LED_BTM, gpio.OUT)  # status led3

# Turn off LEDs
gpio.output(LED_GREEN, True)
time.sleep(0.1)
gpio.output(LED_AMBER, True)
time.sleep(0.1)
gpio.output(LED_BTM, False)

RESOLUTION = (1280, 720)

def blink(pin, repeat, interval):
    on = False
    off = True
    if pin == LED_BTM:
        on = True
        off = False
    for i in range(repeat):
        gpio.output(pin, on)
        time.sleep(interval)
        gpio.output(pin, off)
        time.sleep(interval)

# For Selecting Cam and taking + saving a picture
def camcapture(_cam, _camno):
    print('selectcam( ', _camno, ' )')
    if _camno < 1 or _camno > 3:
        print('[selectcam] invalid cam number!')
    else:
        if _camno == 1:
            print("select cam 1")
            gpio.output(SEL_1, False)
            gpio.output(SEL_2, False)
        if _camno == 2:
            print("select cam 2")
            gpio.output(SEL_1, True)
            gpio.output(SEL_2, False)
        if _camno == 3:
            print("select cam 3")
            gpio.output(SEL_1, True)
            gpio.output(SEL_2, True)
        time.sleep(0.2)
        dir = '/home/pi/Desktop/cam-test'
        photoname = dir + folder + 'cam' + str(_camno) + '.jpg'
        print(photoname)
        _cam.capture(photoname)
        print('cam', str(_camno), '- picture taken!')

def main():
    # Hello blinks
    blink(LED_GREEN, 2, 0.1)
    blink(LED_AMBER, 2, 0.1)
    blink(LED_BTM, 2, 0.1)

    # Initialize camera object
    print('initializing camera')
    gpio.output(SEL_1, True)
    gpio.output(SEL_2, True)
    time.sleep(0.1)
    cam = picamera.PiCamera()
    cam.resolution = RESOLUTION

    # take three pictures
    camcapture(cam, 1)
    camcapture(cam, 2)
    camcapture(cam, 3)
