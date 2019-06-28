#  Turning off the Raspberry pi
# =================================================
#
import time
import RPi.GPIO as gpio


BUTTON_OFF = 3 #25 # BOARD - 22


gpio.setmode(gpio.BCM)
gpio.setup(BUTTON_OFF, gpio.IN)


while(True):
    gpio.wait_for_edge(BUTTON_OFF, gpio.RISING)
    print("Turning off pi")
