import os

for folder in os.listdir('.'):
    if folder.startswith('Hike'):
        for image in os.listdir(folder):
            if image.startswith('Hike'):
                oldname = image
                newname = oldname.split('-')[1]
                print oldname
                print newname
                os.rename(folder + '/' + oldname, folder + '/' + newname)
