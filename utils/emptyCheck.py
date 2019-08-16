import os

for (dirpath, dirnames, files) in os.walk('../empty'):
    if files:
        print (dirpath, 'is not empty')
    else:
        print (dirpath, 'is empty')
