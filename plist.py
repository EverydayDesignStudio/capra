#
#    _________ _____  _________ _
#   / ___/ __ `/ __ \/ ___/ __ `/
#  / /__/ /_/ / /_/ / /  / /_/ /
#  \___/\__,_/ .___/_/   \__,_/
#           /_/
# ===============================
# Script for using Haishoku to detect dominant colour and palette from pictures
# and writing them to a csv.
# ===============================

# Load modules
import sys
import os
import csv
sys.path.insert(0, "..")
from haishoku.haishoku import Haishoku


folder = "/Users/talamram/Downloads/thike/"


# Count files in selected repository
counter = 0
for file in os.listdir('..'):
    counter += 1

# Iterate through images in folder and extract dominant colour and palette
# and write them to a csv

path = "/Users/talamram/Documents/haishoku/demo/demo_01.png"

# getPalette api
palette = Haishoku.getPalette(path)

# getDominant api
dominant = Haishoku.getDominant(path)







# Haishoku object
h = Haishoku.loadHaishoku(path)
print('= showpalette =')
print(h.palette)
print('= dominant =')
print(h.dominant)
