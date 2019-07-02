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
            picture = Image.open(img)
            picture = picture.resize(resize_amount, Image.ANTIALIAS)
            picture.save(img)

            print('resized image: ' + img)
            count += 1

    print('Finished resizing the image ' + str(count) + ' pictures.')

# Run the script
for i in range(8, 9):
    DIRECTORY = f'/Volumes/Capra/jordan-hike{i}'
    resizeImages((405, 720), DIRECTORY)
