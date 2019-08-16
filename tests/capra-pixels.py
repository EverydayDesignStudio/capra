import RPi.GPIO as gpio
import board
import neopixel

PIXEL_AMOUNT = 11       # The amount of NeoPixels on the strip

gpio.setup(board.D18, gpio.OUT)

gpio.output(board.D18, True)

#
# pixels = neopixel.NeoPixel(board.D18, PIXEL_AMOUNT)
# pixels.fill((0, 255, 0))
#
# def indicator1(position: float):
#     brights = position - 1
#     for p in range(int(brights):
#         pixels[p] = (255, 255, 255)
#     intensity = 255 * (position - brights)
#     pixels[brights + 1](intensity, intensity, intensity)
