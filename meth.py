#               __  __
#    __ _  ___ / /_/ /
#   /  ' \/ -_) __/ _ \
#  /_/_/_/\__/\__/_//_/
# =====================

from os import listdir
import os
import csv
import operator
import pygame
import math
import sh
from time import sleep



def printblub():
    print('blub!')
    return

def sorthikes():
    """
    hikelist = []
    with open('meta.csv', 'rb') as meta:
        reader = csv.reader(meta)
        reader.next()
        sortedmeta = sorted(reader, key=lambda column:column[2], reverse=True
        with open('metasort.csv', 'w') as metasort:
            for row in sortedmeta:
                print row
    """

# =========================
# with minimum altitude and maximum altitude known, return hike corresponding
# with currect compass angle
def polar(ang, r):
    x2 = sh.width/2 + r * math.sin(2 * math.pi *  ang / 360)
    y2 = sh.height/2 + r * math.cos(2 * math.pi *  ang / 360)
    return x2, y2

def calcHike(alts, angle):
    tol = 10
    print '======'
    print 'CALCHIKE'
    print 'len(alts): ' + str(sh.hikes)
    if angle > 180:
        angle = 360 - angle

    for h in range(0, sh.hikes):
        hangle = calcAngle(alts, alts[h])

        #print 'calculd angle: ' + str(hangle)
        #print '==================='
        if abs(hangle - angle) < tol:
            return h
    return -1

def calcAngle(alts, alt):
    perc = (alt - sh.altsmin) / sh.altsdif
    angle = perc * 180
    return angle

def initialisehikes(alts):
    print 'meth - initiase hikes'
    sh.altsmin = min(alts)
    sh.altsmax = max(alts)
    print str(sh.altsmin) + str(sh.altsmax)
    sh.altsdif = sh.altsmax - sh.altsmin

def average(values):
    summ = 0
    amount = len(values)
    for i in range(amount):
        summ = summ + values[i]
    #calculate average of sum heading
    average = summ / amount
    return average

def orientToHike(degrees):
    number = int(degrees/90)

    return number

def fadeimagein(image, screen):
    for alpha in range(5):
        image.set_alpha(47)
        wid, hei = image.get_rect().size
        screen.blit(image, (sh.width/2 - wid/2, sh.height/2 - hei/2) )
        pygame.display.flip()
        #sleep(0.05)
        #print('fade: ' + str(alpha))

#sorthikes()
