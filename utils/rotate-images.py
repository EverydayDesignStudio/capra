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
            picture = Image.open(img)
            picture = picture.rotate(rotation_amount, expand=True)
            picture.save(img)

            print('rotated image: ' + img)
            count += 1

    print('Finished rotating ' + str(count) + ' pictures.')

# Run the script
for i in range(10, 16):
    DIRECTORY = '/Volumes/Capra/jordan-hike{n}'.format(n=i)
    print(DIRECTORY)
    rotateImages(90, DIRECTORY)
