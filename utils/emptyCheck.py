import os

for (dirpath, dirnames, files) in os.walk(directory):
    if files:
        print (dirpath, 'is not empty')
    else:
        print (dirpath, 'is empty')
