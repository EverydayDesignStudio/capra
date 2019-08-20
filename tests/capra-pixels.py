import RPi.GPIO as gpio
import board
import neopixel
import time

PIXEL_AMOUNT = 11       # The amount of NeoPixels on the strip
ORDER = neopixel.RGB
PIXEL_PIN = board.D18

pixels = neopixel.NeoPixel(PIXEL_PIN, PIXEL_AMOUNT, brightness=0.2, auto_write=False, pixel_order=ORDER)
pos = 0

def indicator1(position: float):
    brights = position - 1
    for p in range(int(brights):
        pixels[p] = (255, 255, 255)
    intensity = 255 * (position - brights)
    pixels[brights + 1](intensity, intensity, intensity)


while(1):
    pos += 0.01
    indicator(pos)
    time.sleep(0.1)
