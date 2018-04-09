import csv
import random
from math import sin
from math import pi
from os import listdir

index = 0
path = 'Hike4'
with open('metatest.csv', 'wb') as csvfile:
    writer = csv.writer(csvfile)
    
    steep = 0.1
    distance = 0
    for file in listdir(path):
        distance += 1
    alt = []
    calt = random.uniform(0, 100)
    
    for file in listdir(path):
        if (index % int(random.uniform(2, 100)) == 0):
            steep = random.uniform(-3, 10)
        print index
        calt += 0.015 * sin(pi/4 * index / distance) + 0.05 * (steep + random.uniform(-0.1, 0.5))
        alt.append(calt)
        index += 1

    for i in range(distance):
        writer.writerow(["{:04}".format(i), round(alt[i], 1)])
        print(str("{:04}".format(i)) + '\t' + str(round(alt[i], 1)))
        
    print('max: ' + str(max(alt)))
    print('min: ' + str(min(alt)))
