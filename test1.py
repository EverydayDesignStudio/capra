from envirophat import light
from envirophat import leds
from envirophat import motion
import picamera
import time
index = 0

cam = picamera.PiCamera()

for i in range(3):
    leds.off()
    time.sleep(1)
    leds.on()
    time.sleep(0.5)

while(1):
    print(light.rgb())
    time.sleep(0.5)

    if(light.rgb()[0] > 130):
        name = str(index) + 'pic.jpg'
        cam.capture(name)
        index = index + 1
    
        
