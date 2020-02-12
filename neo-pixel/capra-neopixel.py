#!/usr/bin/env python3

import board
import neopixel
import time
import math

NEOPIXEL_LENGTH = 23

pixels = neopixel.NeoPixel(board.D18, NEOPIXEL_LENGTH)
print(board.D18)


def main():
    # pixels[0] = (0, 0, 0)
    print('We are pixeling')
    pixels.fill((100, 100, 100))

    # Won't be able to use any sleeps in the actual code
    time.sleep(1.0)
    pixels.fill((0, 0, 0))
    # pixels[10] = (255, 60, 200)

    # time.sleep(2.0)

    setStripPercentage(.80)


def setStripPercentage(percent: float):
    print('set the strip')
    pixels_to_lite = int(NEOPIXEL_LENGTH * percent)

    for i in range(pixels_to_lite):
        pixels[i] = (50, 50, 50)


if __name__ == "__main__":
    main()
