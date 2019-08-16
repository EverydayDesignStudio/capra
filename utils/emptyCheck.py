import os

HIKEFOLDER = '.'

for (dirpath, dirnames, files) in os.walk(HIKEFOLDER):
    if files:
        print (dirpath, 'is not empty')
    else:
        print (dirpath, 'is empty')
