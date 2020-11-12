#!/usr/bin/env python3

# This code is based off of code snippets from the following article
# https://www.alanzucconi.com/2015/09/30/colour-sorting/

import colorsys
import cv2
import math
import numpy as np
import random


# Script to generate a bunch of random colors, then sort, and save to image
def main():
    colors_length = 1000
    colors = []  # (0,1)

    # Generates the colors
    for i in range(0, colors_length):
        colors.append([random.random(), random.random(), random.random()])

    # Sort the colors by hue & luminosity
    repetition = 6
    colors.sort(key=lambda rgbx: sortby_hue_luminosity(*rgbx, repetition))

    print('\n\n\n\n\n\n\n\n')

    for i in range(0, colors_length):
        values = sortby_hue_luminosity(colors[i][0], colors[i][1], colors[i][2], repetition)
        # print(i, values[0], values[1])

    # Compute the sort on every element in the list
    # for i in colors:
    #     result = sortby_hue_luminosity(i[0], i[1], i[2], 8)
    #     print(result)

    # Generates the image
    generatePics(colors, 'hue-luminosity-min-3-042')

def sortby_hue_luminosity(r, g, b, repetitions=1):
    lum = math.sqrt(0.241 * r + 0.691 * g + 0.068 * b)
    h, s, v = colorsys.rgb_to_hsv(r, g, b)

    h2 = int(h * repetitions)
    # h2 = h * repetitions
    lum2 = int(lum * repetitions)
    # lum = int(lum * repetitions)
    v2 = int(v * repetitions)
    # v2 = v * repetitions

    # Connects the blacks and whites between each hue chunk
    # Every other (each even) color hue chunk, the values are flipped so the
    # white values are on the left and the black values are on the right
    if h2 % 2 == 1:
        v2 = repetitions - v2
        lum = repetitions - lum

    print(h2, lum)
    return (h2, lum)


def generatePics(colors_sorted, name: str):
    # Generates the picture
    height = 50
    img = np.zeros((height, len(colors_sorted), 3), np.uint8)  # (0,255)

    for x in range(0, len(colors_sorted)-1):
        c = [colors_sorted[x][0] * 255, colors_sorted[x][1] * 255, colors_sorted[x][2] * 255]
        img[:, x] = c

    cv2.imwrite('{n}.png'.format(n=name), img)
    # cv2.imwrite('sort.png', img)


if __name__ == "__main__":
    main()
