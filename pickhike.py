"""                           .
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

#from envirophat import motion
from PIL import Image
from meth import *

# General variables
# ========================
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

image = Image.open('../compass/compass-1.jpg') # initialise
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
start = int(raw_input('start? '))
progress = [start] * hikes # variable for displaying correct hike photo

sh.hikes = hikes

initialisehikes(alts)

indication = pygame.Surface((sh.width, sh.height))


# ============================================================================
#     __
#    / /__  ___  ___
#   / / _ \/ _ \/ _ \
#  /_/\___/\___/ .__/
#             /_/
# ============================================================================

while (1):

    if photo:
        if select is not -1:
            print 'select: ' + str(select + 1)
            folder = 'Hike' + str(13) # str(select + 1)
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
