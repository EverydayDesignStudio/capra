import RPi.GPIO as gpio
import board
import neopixel

PIXEL_AMOUNT = 11       # The amount of NeoPixels on the strip

pixels = neopixel.NeoPixel(board.D4, PIXEL_AMOUNT)

def indicator1(position: float):
    brights = position - 1
    for p in range(int(brights):
        pixels[p] = (255, 255, 255)
    intensity = 255 * (position - brights)
    pixels[brights + 1](intensity, intensity, intensity)
