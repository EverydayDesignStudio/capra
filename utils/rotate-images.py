#!/usr/bin/env python3

import PIL, os, sys
from PIL import Image


def rotateImages(rotation_amount, directory):
    # For each image in the specified directory, open and rotate
    os.chdir(directory)
    count = 0
    for img in os.listdir():
        # Exclude hidden image files
        if img.endswith('.jpg') and not img.startswith('._'):
            # TODO - add a try catch for if the image is not actually correct
            try:
                picture = Image.open(img)
            except OSError as error:
                print("\n{err}\nERROR on picture: {n}\n".format(err=error, n=count))

            picture = picture.rotate(rotation_amount, expand=True)

            try:
                picture.save(img)
            except OSError as error:
                print("Couldn't save the image")

            # print('rotated image: ' + img)
            count += 1
            if count % 100 == 0:
                print('{n} rotated'.format(n=count))

    print('Finished rotating ' + str(count) + ' pictures.')


# TODO - before running script choose the range of folders to execute on
hike_list = [16]
# HIKE = int(input('Input Hike Number: '))
partial_directory = '/Users/Jordan/Dropbox/Everyday Design Studio/A Projects/100 Ongoing/Capra/capra-storage/capra-storage-july2020/hike' 
for i in hike_list:
    DIRECTORY = '{d}{h}/'.format(d=partial_directory, h=i)
    print(DIRECTORY)
    # rotateImages(90, DIRECTORY)     # 90 counterclockwise (left)
    # rotateImages(180, DIRECTORY)     # 180 upside down
    rotateImages(270, DIRECTORY)    # 90 clockwise (right)
