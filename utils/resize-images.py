#!/usr/bin/env python3

import PIL
import os
import sys
from PIL import Image


def resizeImages(resize_amount, directory):
    # For each image in the specified directory,
    # open and rotate
    os.chdir(directory)
    count = 0
    for img in os.listdir():
        # exclude hidden image files
        if img.endswith('.jpg') and not img.startswith('._'):
            try:
                picture = Image.open(img)
            except OSError as error:
                print("\n{err}\nERROR on picture: {n}\n".format(err=error, n=count))

            picture = picture.resize(resize_amount, Image.ANTIALIAS)

            try:
                picture.save(img)
            except OSError as error:
                print("Couldn't save the image")

            # print('resized image: ' + img)
            count += 1

            if count % 100 == 0:
                print('{n} resized'.format(n=count))
                # print('{n}/{total}'.format(n=count, total=os.listdir))

    print('Finished resizing the image ' + str(count) + ' pictures.')


# Run the script
partial_directory = '/Users/Jordan/Dropbox/Everyday Design Studio/A Projects/100 Ongoing/Capra/capra-storage/capra-storage-july2020/hike' 
hike_list = [3, 4, 5, 6, 7, 8]
# hike_list = [2]
for i in hike_list:
    DIRECTORY = '{d}{h}/'.format(d=partial_directory, h=i)
    resizeImages((1280, 720), DIRECTORY)
