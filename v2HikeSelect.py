#.                            .
#                   .-.      / \        _
#                  /,,.\    /,,.\-_   _/,\
#     _        .--'' '  \__/       \_/    \___
#    / \_    _/      _____              __/   \
#   /    \_/       _/     \            /       \
#  /      \__     /        `-_.-_     /         \__
# /          \  _/         .'    \   /   .'\       \
#         _              '       _      __
#   _  __(_)__ _    _____  ___  (_)__  / /____ ____ TM
#  | |/ / / -_) |/|/ / _ \/ _ \/ / _ \/ __/ -_) __/
#  |___/_/\__/|__,__/ .__/\___/_/_//_/\__/\__/_/
#                  /_/
# ============================================================================
# ============================================================================
# Written By: Tal Amram - tal_amram@sfu.ca
# Everyday Design Studio, SIAT, SFU
# eds.siat.sfu.ca
# For Raspberry Pi Zero W
#
# ASCI art font 'small slant' from http://patorjk.com/software/taag/
"""
 # # # # # # #
 #  Tickets  #
 # # # # # # #
- try out solutions for the voids
- fix 0 < > 360 degree bug
"""
# ============================================================================
#             __
#    ___ ___ / /___ _____
#   (_-</ -_) __/ // / _ \
#  /___/\__/\__/\_,_/ .__/
#                  /_/
# ============================================================================

import math
import time
import pygame
import csv
import sh       # contains global variables
sh.init()

from envirophat import motion
from PIL import Image
from meth import *


select = 0 # variable for choosing hike folder
tolerance = 45 # threshold amount of degrees to turn viewpointer before switching to other hike folder
buffersize = 5
heading = [] # array to store heading values in and calculate average.
overlay = False # for toggling overlay on/off
lowres = False # for toggling lowres mode
photo = True # for toggling photo
for i in range(buffersize):
    heading.append(0)
heady = 0 # index to count location in array 'heading'
headcount = 0
print(heading)

for i in range(buffersize - 1):
    heading[i] = motion.heading()

image = Image.open('../compass/compass-1.jpg')
pygame.init()
pygame.display.init()

screen = pygame.display.set_mode((1280, 720))
sh.width, sh.height = pygame.display.get_surface().get_size()

# prepare semitransparent black screen
photolayer = pygame.Surface((sh.width, sh.height))
bfade = pygame.Surface((sh.width, sh.height))
bfade.fill((0, 0, 0, 3))
bfade.set_alpha(3)
background = pygame.Rect(0, 0, sh.width, sh.height)

font = pygame.font.SysFont("monospace", 15)
largefont = pygame.font.SysFont("monospace", 70)

# Arrange sh.hikes on ring
# =====================
# Count hikes
metaAlt = 0
hikes = 0
for file in listdir('..'):
    print file
    if file.startswith('Hike'):
        print '=============='
        print 'file says hike'
        print '=============='
        hikes += 1
        print hikes
print str(hikes) + ' hikes counted!'
alts = [0] * hikes
progress = [0]*hikes # variable for displaying correct hike photo

sh.hikes = hikes

# determine minimum and maximum altitude in every hike
for hike in range(sh.hikes):
    folder = '../Hike' + str(hike + 1)
    with open(folder + '/metatest.csv', 'r') as imgmeta:
        reader = csv.reader(imgmeta)

        maxt = 0
        mint = 9999 # not most elegant solution
        for row in reader:
            alt = float(row[1])
            maxt = max(maxt, alt)
            mint = min(mint, alt)
        alts[hike] = maxt - mint
        print('alts[' + str(hike) + '] : ' + str(alts[hike]))

#pass alts data to shared
initialisehikes(alts)

# calculate
for hike in range(0, sh.hikes):
    percentage = (alts[hike] - sh.altsmin) / sh.altsdif
    print 'Hike' + str(hike + 1) + ' alt: ' + str(alts[hike]) + ' % ' + str(percentage * 100)

# draw indication of angles corresponding with hikes
indication = pygame.Surface((sh.width, sh.height))

for h in range(sh.hikes):
    hangle = calcAngle(alts, alts[h])
    r = sh.height/3
    print 'Hike [' + str(h) + '] @ angle : ' + str(hangle)

    xh, yh = polar(hangle, r)
    pygame.draw.line(indication, (0, 20 + h * 20, 0), (sh.width/2, sh.height/2), (xh, yh), 10)
    for i in range(2):
        xh, yh = polar( hangle + (1 - 2*i) * 10, r)
        pygame.draw.line(indication, (0, 20 + h * 20, 0), (sh.width/2, sh.height/2), (xh, yh), 3)

    xh, yh = polar(360 - hangle, r)
    pygame.draw.line(indication, (0, 20 + h * 20, 0), (sh.width/2, sh.height/2), (xh, yh), 10)
    for i in range(2):
        xh, yh = polar(360 - (hangle + (1 - 2*i) * 10), r)
        pygame.draw.line(indication, (0, 20 + h * 20, 0), (sh.width/2, sh.height/2), (xh, yh), 3)

    label = largefont.render(str(h), 1, (0, 255, 0))
    indication.blit(label, polar(hangle, r*1.2))

indication.set_alpha(75)

# ============================================================================
#     __
#    / /__  ___  ___
#   / / _ \/ _ \/ _ \
#  /_/\___/\___/ .__/
#             /_/
# ============================================================================

while (1):
    # Read Compass
    # ===============================================
    heady = heady + 1
    if heady > len(heading) - 1:
        heady = 0

    heading[heady] = motion.heading()
    headcount = average(heading) #calculate average of all values in heading
    headingdiff = headcount - (45 + ((select-1) * 90))

    #if (headingdiff < tolerance and headingdiff > -tolerance):
     #   pass
    #else:
    if (select is not calcHike(alts, headcount)):
            select = calcHike(alts, headcount)


    # Progress and show Hike

    #draw image ===========
    if select is not -1:
        print 'select: ' + str(select + 1)
        folder = 'Hike' + str(select + 1)
        file = folder +'-' + "{:04}".format(progress[select]) +'.jpg'
        if lowres:
            folder = folder + '/405/'
        folder = '../' + folder
        image = pygame.image.load(folder + '/' + file)
        #image = pygame.transform.scale(image, (1280, 720))
        fadeimagein(image, photolayer)
        progress[select] = progress[select] + 1
        if (progress[select] > len(listdir(folder)) - 1):
            print '+- RESET HIKE -+'
            print folder + ' contains ' + str(len(listdir(folder))) + 'files,'
            print 'progress[' + str(select) + '] @ ' + str(progress[select])
            progress[select] = 0
    else:
        photolayer.blit(bfade, (0,0))
    screen.blit(photolayer, (0,0))
    if overlay:
        loc = (sh.width/2, sh. height/2)
        rot_indication = pygame.transform.rotate(indication, headcount)
        rot_indication.get_rect.center = loc
        screen.blit(rot_indication, (0,0))
        # !Placeholder: draw line instead of show hike
        label = largefont.render(str(select), 1, (255, 255, 255))
        screen.blit(label, (sh.width/2, sh.height/2))
        r = sh.height/2
        x1 = sh.width/2
        y1 = sh.height/2
        x2, y2 = polar(headcount, r)
        x3, y3 = polar(motion.heading(), r)
        pygame.draw.line(screen, (255, 0, 0), (x1, y1), (x2, y2), 10)
        pygame.draw.line(screen, (0, 0, 255), (x1, y1), (x3, y3), 10)

    # print program info to screen
    """
    #rectangle = pygame.Rect(80, 80, 200, 100)
    pygame.draw.rect(screen, (0, 0, 0), rectangle)
    label = font.render('compass: ' + str(motion.heading()), 1, (255, 255, 255))
    screen.blit(label, (100, 100))
    label = font.render('headingdiff: ' + str(headingdiff), 1, (255, 255, 255))
    screen.blit(label, (100, 120))
    label = font.render('folder: ' + str(select), 1, (255, 255, 255))
    screen.blit(label, (100, 140))
    label = font.render('photo: ' + str(progress), 1, (255, 255, 255))
    screen.blit(label, (100, 160))
    """

    pygame.display.flip() # update screen
# ============================================================================
#     __            __                    __                                 =
#    / /_____ __ __/ /  ___  ___ ________/ /                                 =
#   /  '_/ -_) // / _ \/ _ \/ _ `/ __/ _  /                                  =
#  /_/\_\\__/\_, /_.__/\___/\_,_/_/  \_,_/                                   =
#           /___/                                                            =
# ============================================================================
    for event in pygame.event.get():
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_w:
                pygame.display.set_mode(1280, 720)
            elif event.key == pygame.K_f:
                pygame.display.toggle_fullscreen()
            elif event.key == pygame.K_o:
                overlay = not overlay
            elif event.key == pygame.K_i:
                photo = not photo
            elif event.key == pygame.K_l:
                lowres = not lowres
