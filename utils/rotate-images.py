#!/usr/bin/env python3

import PIL, os, sys
from PIL import Image


def rotateImages(rotation_amount, directory):
    # For each image in the specified directory,
    # open and rotate
    os.chdir(directory)
    count = 0
    for img in os.listdir():
        # exclude hidden image files
        if img.endswith('.jpg') and not img.startswith('._'):
            # TODO - add a try catch for if the image is not actually correct
            # try:
            #     picture = Image.open(img)
            # except expression as identifier:
            #     pass
            # picture = Image.open(img)
            picture = picture.rotate(rotation_amount, expand=True)
            picture.save(img)

            print('rotated image: ' + img)
            count += 1

    print('Finished rotating ' + str(count) + ' pictures.')

# TODO - before running script choose the range of folders to execute on
# Run the script
# for i in range(10, 11):
hike_list = [0, 1, 2, 3, 4]
for i in hike_list:
    DIRECTORY = '/Volumes/capra-hd/hike{n}'.format(n=i)
    print(DIRECTORY)
    # rotateImages(90, DIRECTORY)     # 90 counterclockwise (left)
    rotateImages(270, DIRECTORY)    # 90 clockwise (right)
