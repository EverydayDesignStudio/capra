#!/usr/bin/env python3

import time
import os
from os import listdir
from PIL import Image

partial_directory = '/Volumes/capra-hd/hike'
partial_directory = '/Users/Jordan/Dropbox/Everyday Design Studio/A Projects/100 Ongoing/Capra/capra-storage/capra-storage-july2020/hike' 
# custom_directory = '/Volumes/capra-hd/CAMERA_2/hike3-yosemite-good'
# custom_directory = '/Volumes/capra-hd/CAMERA_1/hike12-studio'
custom_directory = '/Volumes/capra-hd/CAMERA_1/hike41-last-hike'

def main():
    print('Image Check program\n')

    # for hike_num in range(1, 10):
    for hike_num in (15, 16, 19, 29, 30, 31, 32, 33):
        DIRECTORY = '{d}{h}/'.format(d=partial_directory, h=hike_num)
    # for hike_num in range(1):
        # DIRECTORY = '{d}/'.format(d=custom_directory)

        # print(DIRECTORY)

        count = 0
        for filename in os.listdir(DIRECTORY):
            if filename.endswith(".jpg") and not filename.startswith("."):
                try:
                    im = Image.open(DIRECTORY + filename)
                    im.verify()  # I perform also verify, don't know if he sees other types o defects
                    im.close()  # Reload is necessary in my case
                except:
                    count += 1
                    print(filename)
                    continue

        print('TOTAL CORRUPT IMAGES for HIKE {h}: {i}\n'.format(h=hike_num, i=count))


def helper_function():
    print('hello there')


if __name__ == "__main__":
    main()
