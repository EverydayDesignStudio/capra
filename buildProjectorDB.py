## python version 3.9.7
from sklearn.cluster import KMeans  # pip install -U scikit-learn
from collections import Counter
import cv2  # pip install opencv-python : for resizing image
import random
import time
import os
import glob
import sys
import sqlite3
import datetime
from operator import itemgetter
from colormath.color_objects import HSVColor, LabColor
from colormath.color_conversions import convert_color
from colormath.color_diff import delta_e_cie2000

# image & color processing
from PIL import ImageTk, Image      # Pillow image functions
import math
import colorsys
import numpy as np

# custom modules
from classes.capra_data_types import Picture, Hike
from classes.sql_controller import SQLController
from classes.sql_statements import SQLStatements
from classes.kmeans import get_dominant_color_1D

# transfer animation
import platform
from sqlite3.dbapi2 import connect
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
# from PyQt5.QtWidgets import QFileDialog
from PyQt5.QtCore import *
from classes.ui_components import *
from projector_slideshow import *

global globalPicture

####################################################

TRANSFER_DONE = False
TWO_CAM = False         # special variable to transfer hikes with only two cameras (for Jordan's 9 early hikes)

currHike = -1
globalCounter_h = 0
dummyGlobalColorRank = -1
dummyGlobalAltRank = -1
dummyGlobalCounter = 0

DROPBOX = "/Users/myoo/Dropbox/"
DBTYPE = 'camera'   # 'camera' or 'projector'

# need this indexes hardcoded for the python helper function
# *** These are indexes at the destDB (projector), so the srcDB type doesn't matter
ALTITUDE_INDEX = 10
COLOR_INDEX_HSV = 14
INDEX_IN_HIKE_INDEX = 8

BASEPATH_SRC = None
BASEPATH_DEST = None
src_db_name = None
dest_db_name = None

# ### TODO: Add this later
# def setupDB():
#     '''Initializes the database connection.\n
#     If on Mac/Windows give dialog box to select database,
#     otherwise it will use the global defined location for the database'''
#
#     # Mac/Windows: select the location
#     if platform.system() == 'Darwin' or platform.system() == 'Windows':
#         filename = QFileDialog.getOpenFileName(self, 'Open file', '', 'Database (*.db)')
#         self.database = filename[0]
#         self.directory = os.path.dirname(self.database)
#     else:  # Raspberry Pi: preset location
#         self.database = g.DATAPATH_PROJECTOR + g.DBNAME_MASTER
#         self.directory = g.DATAPATH_PROJECTOR
#
#     print(self.database)
#     print(self.directory)
#     self.sql_controller = SQLController(database=self.database, directory=self.directory)
#
#     if (self.sql_controller.get_picture_id_count(self._saved_picture_id)):
#         self.picture = self.sql_controller.get_picture_with_id(self._saved_picture_id)
#     else:
#         self.picture = self.sql_controller.get_first_time_picture()
#
#     ### TODO: TESTING - comment out to speed up program load time
#     self.uiData = self.sql_controller.preload_ui_data()
#     self.preload = True


if (DBTYPE == 'projector'):
    # BASEPATH_SRC = "Everyday Design Studio/A Projects/100 Ongoing/Capra/capra-storage/capra-storage-july/"
    # src_db_name = "capra_projector_jan2021_min_AllHikes.db"

    # BASEPATH_SRC = "Everyday Design Studio/A Projects/100 Ongoing/Capra/capra-storage/capra-storage-jordan-camera-originals/capra-storage1/"
    # src_db_name = "capra_projector_jan2021_min_AllHikes.db"

    BASEPATH_SRC = "Everyday Design Studio/A Projects/100 Ongoing/Capra/capra-storage/capra-storage-jordan-camera/capra-storage2/"
    src_db_name = "capra_projector_jun2021_min_test2.db"

    BASEPATH_DEST = "Everyday Design Studio/A Projects/100 Ongoing/Capra/capra-storage/capra-storage-jordan-projector/"
    dest_db_name = "capra_projector_jun2021_min_test_0708.db"

else:
    # BASEPATH_SRC = "Everyday Design Studio/A Projects/100 Ongoing/Capra/capra-storage/capra-storage-jordan2/"
    # src_db_name = "capra_camera.db"
    #
    # BASEPATH_DEST = "Everyday Design Studio/A Projects/100 Ongoing/Capra/capra-storage/capra-storage-min-transfer-2/"
    # dest_db_name = "capra_projector_apr2021_min_camera_full.db"

    BASEPATH_SRC = "Everyday Design Studio/A Projects/100 Ongoing/Capra/capra-storage/capra-storage-min-pi-test-1/"
    src_db_name = "capra_camera.db"

    BASEPATH_DEST = "Everyday Design Studio/A Projects/100 Ongoing/Capra/capra-storage/capra-storage-test/"
    dest_db_name = "capra_projector_test.db"


####################################################

WHITE_IMAGE = DROPBOX + BASEPATH_DEST + "white.jpg"

srcPath = ""
destPath = ""
SRCDBPATH = DROPBOX + BASEPATH_SRC + src_db_name
DESTDBPATH = DROPBOX + BASEPATH_DEST + dest_db_name

dbSRCController = None
dbDESTController = None

COLOR_HSV_INDEX = -1    # used in the sortColor helper function

CLUSTERS = 5        # assumes X number of dominant colors in a pictures
REPETITION = 8

FILENAME = "[!\.]*_cam[1-3].jpg"
FILENAME_FULLSIZE = "[!\.]*_cam2f.jpg"
# sample dimensions: (100, 60), (160, 95), (320, 189), (720, 427)
DIMX = 100
DIMY = 60
TOTAL = DIMX * DIMY

res_red = []
res_green = []
res_blue = []


def timenow():
    return str(datetime.datetime.now()).split('.')[0]


# make db connections
def getDBControllers():
    global dbSRCController, dbDESTController

    dbSRCController = SQLController(database=SRCDBPATH)

    # TODO: if dest does not exist, create a new DB by copying the skeleton file
    dbDESTController = SQLController(database=DESTDBPATH)


def count_files_in_directory(path, pattern):
    if (not os.path.exists(path)):
        return 0
    else:
        return len(glob.glob(path + pattern))


def build_hike_path(path, hikeID, makeNew=False):
    res = path + 'hike' + str(hikeID) + '/'
    if makeNew and not os.path.exists(res):
        os.makedirs(res, mode=0o755)
    return res


# (h [0-180], s[1-255], v[1-255])
# returns a list: [r, b, g]
def hsvToRgb(h, s, v):
    color_rgb = colorsys.hsv_to_rgb(h/180., s/255., v/255.)
    ret = list(map(lambda a : round(a*255), list(color_rgb)))
    return ret


def formatColors(colors):
    res = ""
    for color in colors:
        res += ",".join(map(str, color)) + "|"
    return res[:-1]


def roundToInt(lst):
    for i in range(len(lst)):
        lst[i] = round(float(lst[i]), 0)
    return lst


def generatePics(colors_sorted, name: str, path: str):
    # Generates the picture
    height = 50
    img = np.zeros((height, len(colors_sorted), 3), np.uint8)  # (0,255)

    for x in range(0, len(colors_sorted)-1):
        tmp = colors_sorted[x][0]
        c = [float(tmp.split(",")[0]), float(tmp.split(",")[1]), float(tmp.split(",")[2])]
        img[:, x] = c

    cv2.imwrite(path + '{n}.png'.format(n=name), img)


def sortby_hue_luminosity(r, g, b, repetitions=1):
    lum = math.sqrt(0.241 * r + 0.691 * g + 0.068 * b)
    h, s, v = colorsys.rgb_to_hsv(r, g, b)

    h2 = int(h * repetitions)
    # h2 = h * repetitions
    # lum2 = int(lum * repetitions)
    # lum = int(lum * repetitions)
    v2 = int(v * repetitions)
    # v2 = v * repetitions

    # Connects the blacks and whites between each hue chunk
    # Every other (each even) color hue chunk, the values are flipped so the
    # white values are on the left and the black values are on the right
    if h2 % 2 == 1:
        v2 = repetitions - v2
        lum = repetitions - lum

    return (h2, lum)


def sort_by_alts(data, alt_index, index_in_hike):
    data.sort(key=itemgetter(alt_index, 0))  # 10 - altitude

    rankList = {}
    for i in range(len(data)):
        rankList[itemgetter(index_in_hike)(data[i])] = i+1   # 8 - index_in_hike

    return rankList


def splitColor(item):
    tmp = itemgetter(COLOR_HSV_INDEX)(item)      # 14 - color_hsv
    return sortby_hue_luminosity(float(tmp.split(",")[0]), float(tmp.split(",")[1]), float(tmp.split(",")[2]), REPETITION)


def sort_by_colors(data, color_index_hsv, index_in_hike):
    global COLOR_HSV_INDEX
    # key function for sort() only accepts 1 argument, so need to explicitly set additional variable as global
    COLOR_HSV_INDEX = color_index_hsv

    # Sort the colors by hue & luminosity
    data.sort(key=splitColor)

    rankList = {}
    for i in range(len(data)):
        rankList[itemgetter(index_in_hike)(data[i])] = i+1   # 8 - index_in_hike

    return rankList


def compute_checksum(path, currHike):
    checkSum_transferred = count_files_in_directory(path, FILENAME)
    checkSum_rotated = count_files_in_directory(path, FILENAME_FULLSIZE)
    return checkSum_transferred, checkSum_rotated, checkSum_transferred + checkSum_rotated


def check_hike_postprocessing(currHike):
    hikeColor = dbDESTController.get_hike_average_color(currHike)
    return hikeColor is not None and hikeColor and not (hikeColor[0] < 0.001 and hikeColor[1] < 0.001 and hikeColor[2] < 0.001)


def dominantColorWrapper(currHike, validRowCount, row_src, image1, image2, image3=None, image_processing_size=None):
    global dummyGlobalCounter

    color_size, colors_hsv, colors_rgb, confidences = get_multiple_dominant_colors(image1=image1, image2=image2, image3=image3, image_processing_size=(DIMX, DIMY))
    picDatetime = datetime.datetime.fromtimestamp(row_src['time'])

    #     TIME,
    #     year, month, day, minute, dayofweek,
    #     hike, index_in_hike, TIME_RANK_GLOBAL,
    #     altitude, altrank_hike, ALTRANK_GLOBAL, ALTRANK_GLOBAL_H,
    #     color_hsv, color_rgb, color_rank_value, color_rank_hike, COLOR_RANK_GLOBAL, COLOR_RANK_GLOBAL_H,
    #     colors_count, colors_rgb, colors_conf,
    #     camera1, camera2, camera3, camera_landscape
    #
    # ** ALLCAP columns are UNIQUE

    # ** 0 is monday in dayofweek
    # ** camera_landscape points to the path to cam2

    h = row_src['hike']
    camera2 = row_src['camera2']
    last_bit = camera2.split('/')[-1]

    idx = None
    if (last_bit == ""):
        idx = row_src['index_in_hike']
    else:
        idx = last_bit.split('_')[0]

    camera1 = "/hike{}/{}_cam1.jpg".format(h, idx)
    camera2 = "/hike{}/{}_cam2.jpg".format(h, idx)
    camera3 = "/hike{}/{}_cam3.jpg".format(h, idx)
    camera2f = "/hike{}/{}_cam2f.jpg".format(h, idx)

    # print("pic {} -> {}".format(row_src['index_in_hike'], validRowCount))

    commit = [round(row_src['time'], 0),
                picDatetime.year, picDatetime.month, picDatetime.day, picDatetime.hour * 60 + picDatetime.minute, picDatetime.weekday(),
                currHike, validRowCount, dummyGlobalCounter,
                round(row_src['altitude'], 2), -1, -1, dummyGlobalCounter,
                ",".join(map(str, colors_hsv[0])), ",".join(map(str, colors_rgb[0])), -1, -1, -1, dummyGlobalCounter,
                color_size, formatColors(colors_rgb), ",".join(map(str, confidences)),
                camera1, camera2, camera3, camera2f, row_src['created_date_time']]

    return commit, colors_hsv[0]


def get_multiple_dominant_colors(image1, image2, image3=None, image_processing_size=None):
    global res_red, res_green, res_blue

    """
    takes an image as input
    returns FOUR values
        i) number of colors
        ii) X number of dominant colors in HSV (int values)
        iii) X number of dominant colors in RGB (int values)
        iv) list of confidence values of the same size (2 decimal places)

    dominant colors are found by running k-means algorithm on the pixels of an image
    & returning the centroid of the largest cluster(s)

    processing time is sped up by working with a smaller image;
    this resizing can be done with the image_processing_size param
    which takes a tuple of image dims as input

    >>> get_multiple_dominant_colors(my_image, k, image_processing_size = (25, 25))
    4                                                               # 4 colors
    [[20, 79, 72], [33, 182, 38], [4, 5, 241], [139, 17, 178]]      # dominant colors in HSV
    [[72, 65, 50], [35, 38, 11], [241, 237, 236], [174, 166, 178]]  # dominant colors in RGB
    [268.7, 103.0, 73.79, 15.32]                                    # confidence values

    """

    k = CLUSTERS
    image = None

    # read in image of interest
    bgr_image1 = cv2.imread(image1)
    bgr_image2 = cv2.imread(image2)
    # convert to HSV; this is a better representation of how we see color
    hsv_image1 = cv2.cvtColor(bgr_image1, cv2.COLOR_BGR2HSV)
    hsv_image2 = cv2.cvtColor(bgr_image2, cv2.COLOR_BGR2HSV)

    image1 = cv2.resize(hsv_image1, image_processing_size, interpolation=cv2.INTER_AREA)
    image2 = cv2.resize(hsv_image2, image_processing_size, interpolation=cv2.INTER_AREA)

    # reshape the image to be a list of pixels
    image1 = image1.reshape((image1.shape[0] * image1.shape[1], 3))
    image2 = image2.reshape((image2.shape[0] * image2.shape[1], 3))

    if (image3 is not None):
        bgr_image3 = cv2.imread(image3)
        hsv_image3 = cv2.cvtColor(bgr_image3, cv2.COLOR_BGR2HSV)
        image3 = cv2.resize(hsv_image3, image_processing_size, interpolation=cv2.INTER_AREA)
        image3 = image3.reshape((image3.shape[0] * image3.shape[1], 3))

    if (image3 is None):
        image = np.concatenate((image1, image2))
    else:
        image = np.concatenate((image1, image2, image3))

    # else:
    #     # read in image of interest
    #     bgr_image1 = cv2.imread(image1)
    #     # convert to HSV; this is a better representation of how we see color
    #     hsv_image1 = cv2.cvtColor(bgr_image1, cv2.COLOR_BGR2HSV)
    #
    #     image1 = cv2.resize(hsv_image1, image_processing_size, interpolation=cv2.INTER_AREA)
    #
    #     # reshape the image to be a list of pixels
    #     image = image1.reshape((image1.shape[0] * image1.shape[1], 3))

    # cluster and assign labels to the pixels
    clt = KMeans(n_clusters=k)
    labels = clt.fit_predict(image)

    # count labels to find most popular
    label_counts = Counter(labels)

    # subset out k popular centroids
    topK = label_counts.most_common(k)
    dominant_colors_hsv = []
    confidences = []

    for label in topK:
        tmp = [ int(e) for e in clt.cluster_centers_[label[0]].tolist() ]
        dominant_colors_hsv.append(tmp)
        base = TOTAL*3
        confidences.append(round(label[1]/base, 2))

    index_to_remove = set()
    confidence_value_threshold = 0.1
    if (len(dominant_colors_hsv) >= k):
        # exclude colors that are similar to existing ones and with < 0.1 confidence value
        for i in range(k):
            color_i = dominant_colors_hsv[i]
            color_i_hsv = HSVColor(color_i[0], color_i[1], color_i[2])
            color_i_lab = convert_color(color_i_hsv, LabColor)

            color_i_delta = []

            for j in range(i+1, k):
                color_j = dominant_colors_hsv[j]
                color_j_hsv = HSVColor(color_j[0], color_j[1], color_j[2])
                color_j_lab = convert_color(color_j_hsv, LabColor)

                delta_e = delta_e_cie2000(color_i_lab, color_j_lab);

                color_i_delta.append(delta_e)

            for j in range(len(color_i_delta)):
                if (confidences[i+j+1] < confidence_value_threshold and color_i_delta[j] < 40):
                    index_to_remove.add(i+j+1)
    else:
        # if the # of domcol is less than k, trim colors that are < 0.1 confidence value only
        for i in range(len(dominant_colors_hsv)):
            if (confidences[i] < confidence_value_threshold):
                index_to_remove.add(i)

    itr = list(index_to_remove)
    itr.sort(reverse = True)

    # trim insignificant colors
    for i in range(len(itr)):
        dominant_colors_hsv.pop(itr[i])
        confidences.pop(itr[i])

    # convert HSV to get RGB colors
    dominant_colors_rgb = []
    for color_hsv in dominant_colors_hsv:
        ret = hsvToRgb(color_hsv[0], color_hsv[1], color_hsv[2])
        dominant_colors_rgb.append(ret)

    res_red.append(str(dominant_colors_rgb[0][0]))
    res_green.append(str(dominant_colors_rgb[0][1]))
    res_blue.append(str(dominant_colors_rgb[0][2]))

    return len(confidences), dominant_colors_hsv, dominant_colors_rgb, confidences


# ### This function is removed and added as a condition within buildHike()
# def filterZeroBytePicturesFromSrc():
#     global dbSRCController
#
#     print("[{}] Checking 0 byte pictures in the source directory before start transferring..".format(timenow()))
#
#     latest_src_hikeID = dbSRCController.get_last_hike_id()
#     latest_dest_hikeID = dbDESTController.get_last_hike_id()
#     print("[{}] ## hikes from Source: {}".format(timenow(), str(latest_src_hikeID)))
#     print("[{}] ## hikes at Dest: {}".format(timenow(), str(latest_dest_hikeID)))
#
#     currHike = 1
#     delCount = 0
#
#     while currHike <= latest_src_hikeID:
#         print("[{}] ### Checking hike {}".format(timenow(), currHike))
#         srcPath = build_hike_path(DROPBOX + BASEPATH_SRC, currHike)
#
#         totalCountHike = dbSRCController.get_pictures_count_of_selected_hike(currHike)
#         print("[{}] ### Hike {} originally has {} rows".format(timenow(), currHike, totalCountHike))
#
#         if (not os.path.isdir(srcPath)):
#             currHike += 1
#             continue
#
#         allRows = dbSRCController.get_pictures_of_selected_hike(currHike)
#
#         for row in allRows:
#             picPathCam1_src = srcPath + "{}_cam1.jpg".format(row['index_in_hike'])
#             picPathCam2_src = srcPath + "{}_cam2.jpg".format(row['index_in_hike'])
#             picPathCam3_src = srcPath + "{}_cam3.jpg".format(row['index_in_hike'])
#
#             if (os.path.exists(picPathCam1_src) and os.stat(picPathCam1_src).st_size == 0 or
#                 os.path.exists(picPathCam2_src) and os.stat(picPathCam2_src).st_size == 0 or
#                 os.path.exists(picPathCam3_src) and os.stat(picPathCam3_src).st_size == 0):
#
#                 # ### (For testing) select the row but don't delete it yet
#                 # srcConnection = dbSRCController.connection
#                 # srcCursor = srcConnection.cursor()
#                 # statement = 'select * from pictures where time = {}'.format(row['time'])
#                 # srcCursor.execute(statement)
#                 # res = srcCursor.fetchall()
#                 # print (res)
#
#                 print("[{}] \t Row {} has an empty picture. Deleting a row..".format(timenow(), row['index_in_hike']))
#
#                 dbSRCController.delete_picture_of_given_timestamp(row['time'], True) # delay commit to prevent concurrency issues
#                 delCount += 1
#
#         totalCountHike = dbSRCController.get_pictures_count_of_selected_hike(currHike)
#
#         if (delCount > 0):
#             print("[{}] {} rows deleted".format(timenow(), delCount))
#             print("[{}] Hike {} now has {} rows".format(timenow(), currHike, totalCountHike))
#
#             dbSRCController.update_hikes_total_picture_count_of_given_hike(totalCountHike, currHike, True)
#
#         # commit changes only when a given hike is fully scanned
#         dbSRCController.connection.commit()
#         currHike += 1


def buildHike(currHike):
    global dbSRCController, dbDESTController
    global srcPath, destPath
    global res_red, res_green, res_blue
    global dummyGlobalColorRank, dummyGlobalAltRank, dummyGlobalCounter, globalCounter_h
    global COLOR_HSV_INDEX

    # Write to file
    # orig_stdout = sys.stdout
    # f = open(DATAPATH + "{}-{}x{}".format(FOLDERNAME, DIMX, DIMY) + '_output_list_RGB.txt', 'w')
    # sys.stdout = f

    avgAlt = 0
    startTime = 9999999999
    endTime = -1
    domColorsHike_hsv = []
    pics = {}
    commits = {}

    validRowCount = 0           ### This is the 'corrected' numValidRows (may 14)
    index_in_hike = 0
    validRows = dbSRCController.get_valid_photos_in_given_hike(currHike)
    numValidRows = len(validRows)
    maxRows = dbSRCController.get_last_photo_index_of_hike(currHike)

    deleteCount = 0             ### to track rows that contain 0 byte pictures in the remote database
    deleteTimestamps = []       ### timestamps of rows to delete

    print("[{}] Last index in Hike {}: {}".format(timenow(), str(currHike), str(maxRows)))
    print("[{}] Expected valid row count: {}".format(timenow(), str(numValidRows)))

    while (index_in_hike <= maxRows + 2):   # allow a loose upper bound (max + 2) to handle the last index
        row_src = dbSRCController.get_hikerow_by_index(currHike, index_in_hike)

        picPathCam1_src = srcPath + "{}_cam1.jpg".format(index_in_hike)
        picPathCam2_src = srcPath + "{}_cam2.jpg".format(index_in_hike)
        picPathCam2f_src = srcPath + "{}_cam2f.jpg".format(index_in_hike)
        picPathCam3_src = srcPath + "{}_cam3.jpg".format(index_in_hike)

        picPathCam1_dest = destPath + "{}_cam1.jpg".format(index_in_hike)
        picPathCam2_dest = destPath + "{}_cam2.jpg".format(index_in_hike)
        picPathCam2f_dest = destPath + "{}_cam2f.jpg".format(index_in_hike)
        picPathCam3_dest = destPath + "{}_cam3.jpg".format(index_in_hike)

        if (row_src is None):
            index_in_hike += 1
            continue

        if (index_in_hike <= maxRows and index_in_hike % 200 == 0):
            print("[{}] ### Checkpoint at {}".format(timenow(), str(index_in_hike)))


        # Transfer, resize and rotate pictures from remote only if there is no local copy.
        # To ensure having a local copy can be done by checking if cam2f exists.
        if (not os.path.exists(picPathCam2f_dest)):

            if (not os.path.exists(picPathCam1_src) or not os.path.exists(picPathCam2_src)):
                index_in_hike += 1
                continue

            # check for 0 byte pictures
            #   if spotted, increase deleteCounter and delete those rows
            #   from the remote camera db and the local camera db before proceeding to the next hike
            if (os.path.exists(picPathCam1_src) and os.stat(picPathCam1_src).st_size == 0 or
                os.path.exists(picPathCam2_src) and os.stat(picPathCam2_src).st_size == 0 or
                (not TWO_CAM and os.path.exists(picPathCam3_src) and os.stat(picPathCam3_src).st_size == 0)):
                print("[{}] \t Row {} has a missing picture. Deleting a row..".format(timenow(), index_in_hike))
                deleteCount += 1
                deleteTimestamps.append(row_src['time'])
                index_in_hike += 1
                continue

            # rotate and resize, copy those to the dest folder
            img = None
            img_res = None
            # resize and rotate for newly added pictures
            try:
                #    1. make a copy of pic2 as pic2'f'
                if (not os.path.exists(picPathCam2f_dest)):
                    img = Image.open(picPathCam2_src)
                    img_res = img.copy()
                    img_res.save(picPathCam2f_dest)

                #    2. resize to 427x720 and rotate 90 deg
                if (not os.path.exists(picPathCam1_dest)):
                    img = Image.open(picPathCam1_src)
                    img_res = img.resize((720, 427), Image.ANTIALIAS).rotate(270, expand=True)
                    img_res.save(picPathCam1_dest)

                if (not os.path.exists(picPathCam2_dest)):
                    img = Image.open(picPathCam2_src)
                    img_res = img.resize((720, 427), Image.ANTIALIAS).rotate(270, expand=True)
                    img_res.save(picPathCam2_dest)

                if (not os.path.exists(picPathCam3_dest)):
                    if (not TWO_CAM):
                        img = Image.open(picPathCam3_src)
                        img_res = img.resize((720, 427), Image.ANTIALIAS).rotate(270, expand=True)
                        img_res.save(picPathCam3_dest)
                    else:
                        img = Image.open(WHITE_IMAGE)
                        img_res = img.copy().rotate(90, expand=True)
                        img_res.save(picPathCam3_dest)
            except:
                print("!! Hike {} @ row {} has truncated pictures, could not rotate. Skipping a row..".format(currHike, index_in_hike))
                deleteCount += 1
                deleteTimestamps.append(row_src['time'])

                # remove corrupted pictures
                if os.path.isfile(picPathCam1_dest):
                    os.remove(picPathCam1_dest)
                if os.path.isfile(picPathCam2_dest):
                    os.remove(picPathCam1_dest)
                if os.path.isfile(picPathCam2f_dest):
                    os.remove(picPathCam1_dest)
                if os.path.isfile(picPathCam3_dest):
                    os.remove(picPathCam1_dest)

                index_in_hike += 1
                continue

        # increment the validRowCounter since we have successfully trasferred the pictures for this row
        validRowCount += 1

        # update timestamps
        if (row_src['time'] < startTime):
            startTime = row_src['time']
        if (row_src['time'] > endTime):
            endTime = row_src['time']

        avgAlt += int(row_src['altitude'])

        if (TWO_CAM):
            picPathCam3_dest = None

        # If a row is found in DB, load it, rather than running the color algorithm again
        if (dbDESTController.get_picture_count_at_timestamp(row_src['time']) > 0):
            commit = dbDESTController.get_picture_at_timestamp(row_src['time'])
            fileName = "{}_camN".format(commit[7])  # index_in_hike
            commits[fileName] = commit

            domCol_hsv = [int(i) for i in commit[13].split(',')]  # color_hsv

        else:
            commit, domCol_hsv = dominantColorWrapper(currHike, validRowCount, row_src, picPathCam1_dest, picPathCam2_dest, image3=picPathCam3_dest, image_processing_size=(DIMX, DIMY))
            fileName = "{}_camN".format(validRowCount)

        commits[fileName] = commit
        domColorsHike_hsv.append(domCol_hsv)

        dummyGlobalCounter += 1
        index_in_hike += 1

    ### Post-processing
    # attach color ranking within the current hike
    # then, upsert rows
    colRankList = sort_by_colors(list(commits.copy().values()), color_index_hsv=COLOR_INDEX_HSV-1, index_in_hike=INDEX_IN_HIKE_INDEX-1)
    altRankList = sort_by_alts(list(commits.copy().values()), alt_index=ALTITUDE_INDEX-1, index_in_hike=INDEX_IN_HIKE_INDEX-1)

    for i in range(maxRows+2):
        fileName = "{}_camN".format(i)

        if i not in altRankList or i not in colRankList:
            continue

        altrank = altRankList[i]
        commits[fileName][10] = altrank
        commits[fileName][11] = dummyGlobalAltRank
        commits[fileName][12] = globalCounter_h + altrank

        colrank = colRankList[i]
        commits[fileName][16] = colrank
        commits[fileName][17] = dummyGlobalColorRank
        commits[fileName][18] = globalCounter_h + colrank

#        print("[{}] altRank: {}, altRankG: {}, altRankG_h: {}, tcolRank: {}, colRankG: {}, colRankG_h: {}".format(i, altrank, dummyGlobalAltRank, str(globalCounter_h + altrank), colrank, dummyGlobalColorRank, str(globalCounter_h + colrank)))

        dummyGlobalColorRank -= 1
        dummyGlobalAltRank -= 1

        # print(commits[fileName])

        commit = tuple(commits[fileName])
        dbDESTController.upsert_picture(*commit)

    print("[{}] ### Generating metadata for Hike {}...".format(timenow(), currHike))
    # make a row for the hike table with postprocessed values
    avgAlt /= validRowCount
    domColorHike_hsv = []
    domColorHike_hsv = get_dominant_color_1D(domColorsHike_hsv, CLUSTERS)
    roundToInt(domColorHike_hsv)

    hikeStartDatetime = datetime.datetime.fromtimestamp(startTime)
    hikeEndDatetime = datetime.datetime.fromtimestamp(endTime)
    domColorHike_rgb = hsvToRgb(domColorHike_hsv[0], domColorHike_hsv[1], domColorHike_hsv[2])

    #  Columns for HIKES
    #
    #     HIKE_ID, avg_altitude, AVG_ALTITUDE_RANK,
    #     START_TIME, start_year, start_month, start_day, start_minute, start_dayofweek,
    #     END_TIME, end_year, end_month, end_day, end_minute, end_dayofweek,
    #     color_hsv, color_rgb, color_rank_value, COLOR_RANK,
    #     pictures, PATH

    defaultHikePath = "/hike{}/".format(str(currHike))
    created_timestamp = dbSRCController.get_hike_created_timestamp(currHike)

    dbDESTController.upsert_hike(currHike, round(avgAlt, 2), -currHike,
                                    round(startTime, 0), hikeStartDatetime.year, hikeStartDatetime.month, hikeStartDatetime.day, hikeStartDatetime.hour * 60 + hikeStartDatetime.minute, hikeStartDatetime.weekday(),
                                    round(endTime, 0), hikeEndDatetime.year, hikeEndDatetime.month, hikeEndDatetime.day, hikeEndDatetime.hour * 60 + hikeEndDatetime.minute, hikeEndDatetime.weekday(),
                                    ",".join(map(str, domColorHike_hsv)), ",".join(map(str, domColorHike_rgb)), -1, -currHike,
                                    validRowCount, defaultHikePath, created_timestamp)

    # delete rows with 0 byte pictures from the referenced camera DB in local
    # (remote db will be synced by copying the local copy of the camera db when the transfer is done)
    if (deleteCount > 0):
        print("[{}] ## Deleting {} rows from hike {} ...".format(timenow(), deleteCount, currHike))

        totalCountHike = dbSRCController.get_pictures_count_of_selected_hike(currHike)
        totalCountHike_remote = dbSRCController.get_pictures_count_of_selected_hike(currHike)

        # extra guard to double check the total number of pictures
        if (totalCountHike - deleteCount == validRowCount and
            totalCountHike_remote - deleteCount == validRowCount):
            for timestamp in deleteTimestamps:
                # local copy of camera db
                # ** making a sequence of commits may lock the database,
                #    so let it commit when hike will be updated outside the loop in the next line
                dbSRCController.delete_picture_of_given_timestamp(timestamp, delayedCommit=True)
            dbSRCController.update_hikes_total_picture_count_of_given_hike(validRowCount, currHike)


    # create a color spectrum for this hike
    colorSpectrumRGB_hike = dbDESTController.get_pictures_rgb_hike(currHike)
    generatePics(colorSpectrumRGB_hike, "hike{}".format(currHike) + "-colorSpectrum", destPath)

    print("[{}] ## Hike {} done. {} rows processed".format(timenow(), currHike, validRowCount))
    print("[{}] ### Now processing global ranks across all hikes and pictures before moving on to the next hike..".format(timenow()))

    ### [Mar 31, 2022]
    # Calculate global ranks when each hike is fully transferred
    # This may be computationally inefficient but to make sure there is not to have partially-computed ranks at any point of time during the transfer
    # Because the slideshow will break if any of the rankings is missing.
    rankTimer = time.time()

    globalTimeList = []
    globalAltList = []
    globalColorList = []
    # key function for sort() only accepts 1 argument, so need to explicitly set additional variable as global
    COLOR_HSV_INDEX = 1

    timer1 = time.time()

    ### global ranks for pictures
    rows_dst = dbDESTController.get_pictures_global_ranking_raw_data()
    for i in range(len(rows_dst)):
        row_dst = rows_dst[i]
        globalTimeList.append((row_dst[0], row_dst[4]))
        globalAltList.append((row_dst[0], row_dst[1]))
        globalColorList.append((row_dst[0], row_dst[2]))

    globalTimeList.sort(key= itemgetter(1, 0))
    for i in range(len(globalTimeList)):
        row_dst = globalTimeList[i]
        rank = i + 1
        dbDESTController.update_pictures_global_TimeRank(row_dst[0], rank)

    globalAltList.sort(key=lambda data: data[1])
    for i in range(len(globalAltList)):
        row_dst = globalAltList[i]
        rank = i + 1
        dbDESTController.update_pictures_global_AltRank(row_dst[0], rank)

    globalColorList.sort(key=splitColor)
    for i in range(len(globalColorList)):
        row_dst = globalColorList[i]
        rank = i + 1
        dbDESTController.update_pictures_global_ColRank(row_dst[0], rank)

    print("[{}] --- Global rankings for Pictures took {} seconds.".format(timenow(), str(time.time() - timer1)))

    # create color spectrum for globalColor and globalColor_h
    colorSpectrumRGB_Global = dbDESTController.get_pictures_rgb_global()
    generatePics(colorSpectrumRGB_Global, "hike-global-colorSpectrum", DROPBOX + BASEPATH_DEST)

    colorSpectrumRGB_Global_h = dbDESTController.get_pictures_rgb_global_h()
    generatePics(colorSpectrumRGB_Global_h, "hike-global-h-colorSpectrum", DROPBOX + BASEPATH_DEST)

    timer2 = time.time()

    ## update alt and color global_h rankings for Pictures
    # altrank_global_h
    altSortedHikes = dbDESTController.get_hikes_by_avg_altrank()
    rankIndex = 1

    for res in altSortedHikes:
        hike = res[0]
        # picsInHike = res[1]       # for debugging
        rows = dbDESTController.get_pictures_of_specific_hike_by_altrank(hike)

        for row in rows:
            pID = row[0]
            dbDESTController.update_pictures_altrank_global_h(rankIndex, pID)
            rankIndex += 1
            # print("## Hike {} ({} pictures) is done, rankIndex is now at {}".format(hike, picsInHike, rankIndex))

    print("[{}] --- Alt_h rankings for Pictures took {} seconds.".format(timenow(), str(time.time() - timer2)))
    timer3 = time.time()

    # color_rank_global_h
    colorSortedHikes = dbDESTController.get_hikes_by_color_rank()
    rankIndex = 1

    for res in colorSortedHikes:
        hike = res[0]
        # picsInHike = res[1]       # for debugging
        rows = dbDESTController.get_pictures_of_specific_hike_by_color_rank(hike)

        for row in rows:
            pID = row[0]
            dbDESTController.update_pictures_color_rank_global_h(rankIndex, pID)
            rankIndex += 1
            # print("## Hike {} ({} pictures) is done, rankIndex is now at {}".format(hike, picsInHike, rankIndex))

    print("[{}] --- Col_h rankings for Pictures took {} seconds.".format(timenow(), str(time.time() - timer3)))
    timer4 = time.time()

    ### global ranks for hikes
    globalAltList.clear()
    globalColorList.clear()

    rows_dst = dbDESTController.get_hikes_global_ranking_raw_data()
    for i in range(len(rows_dst)):
        row_dst = rows_dst[i]
        globalAltList.append((row_dst[0], row_dst[1]))
        globalColorList.append((row_dst[0], row_dst[2]))

    globalAltList.sort(key=lambda data: data[1])
    for i in range(len(globalAltList)):
        row_dst = globalAltList[i]
        rank = i + 1
        dbDESTController.update_hikes_global_AltRank(row_dst[0], rank)

    globalColorList.sort(key=splitColor)
    for i in range(len(globalColorList)):
        row_dst = globalColorList[i]
        rank = i + 1
        dbDESTController.update_hikes_global_ColRank(row_dst[0], rank)

    print("[{}] --- Global ranking took {} seconds".format(timenow(), str(time.time() - rankTimer)))

    print("[{}] --- Global ranking took {} seconds.".format(timenow(), str(time.time() - rankTimer)))
    print("[{}] --- Moving on to the next hike!".format(timenow()))

    return 0


def main():
    global dbSRCController, dbDESTController, dummyGlobalColorRank, dummyGlobalAltRank, dummyGlobalCounter, globalCounter_h
    global srcPath, destPath
    global COLOR_HSV_INDEX

    # TODO: initialize DB if does not exist
    getDBControllers()

    ## update path in hikes
    # srcConnection = dbSRCController.connection
    # srcCursor = srcConnection.cursor()
    # destConnection = dbDESTController.connection
    # destCursor = destConnection.cursor()
    #
    # statement = 'SELECT picture_id, hike, camera1, camera2, camera3, camera_landscape FROM pictures where hike < 40'
    #
    # statement = 'select * from pictures'
    # destCursor.execute(statement)
    # allRows = destCursor.fetchall()
    # # print(hikeRows)
    # for row in allRows:
    #     pID = row[0]
    #     hike = row[1]
    #     camera1 = row[2]
    #     camera2 = row[3]
    #     camera3 = row[4]
    #     camera2f = row[5]
    #
    #     c1 = camera1.split('/')
    #     res1 = "/{}/{}".format(c1[-2], c1[-1])
    #
    #     c2 = camera2.split('/')
    #     res2 = "/{}/{}".format(c2[-2], c2[-1])
    #
    #     c3 = camera3.split('/')
    #     res3 = "/{}/{}".format(c3[-2], c3[-1])
    #
    #     cf = camera2f.split('/')
    #     resf = "/{}/{}".format(cf[-2], cf[-1])
    #
    #     statement = 'update pictures set camera1 = "{c1}", camera2 = "{c2}", camera3 = "{c3}", camera_landscape = "{cf}" where picture_id = {pid}'.format(c1=res1, c2=res2, c3=res3, cf=resf, pid=pID)
    #     # destCursor.execute(statement)
    #
    # # destConnection.commit()
    #
    # statement = 'SELECT picture_id, hike, camera1, camera2, camera3, camera_landscape FROM pictures where hike > 40'
    # destCursor.execute(statement)
    # allRows = destCursor.fetchall()
    # # print(hikeRows)
    # for row in allRows:
    #     pID = row[0]
    #     hike = row[1]
    #     camera2 = row[3]
    #     i = camera2.split('/')[-1]
    #     index = i.split('_')[0]
    #
    #     res1 = "/hike{}/{}_cam1.jpg".format(hike, index)
    #     res2 = "/hike{}/{}_cam2.jpg".format(hike, index)
    #     res3 = "/hike{}/{}_cam3.jpg".format(hike, index)
    #     resf = "/hike{}/{}_cam2f.jpg".format(hike, index)
    #
    #     statement = 'update pictures set camera1 = "{c1}", camera2 = "{c2}", camera3 = "{c3}", camera_landscape = "{cf}" where picture_id = {pid}'.format(c1=res1, c2=res2, c3=res3, cf=resf, pid=pID)
    #     # destCursor.execute(statement)
    #
    # # destConnection.commit()
    # destConnection.close()
    #
    # exit()
    #
    #     # statement = 'select time, picture_id, index_in_hike from pictures where hike = {}'.format(hike)
    #     # destCursor.execute(statement)
    #     # pictureRows = destCursor.fetchall()
    #     # count = 1
    #     # for row in pictureRows:
    #     #     # print(row)
    #     #     statement = 'UPDATE pictures SET index_in_hike = {i}, time = {t} WHERE picture_id = {id}'.format(i=count, t = round(row[0], 0), id=row[1])
    #     #     # print(statement)
    #     #     destCursor.execute(statement)
    #     #
    #     #     count += 1
    #
    # destConnection.commit()
    # destConnection.close()
    # exit()

    #
    # for row in hikeRows:
    #     # avg_altitude = 1
    #     # start_time = 3
    #     # end_time = 9
    #     # path = 20
    #     avg_alt = round(row[1], 2)
    #     stime = round(row[3], 0)
    #     etime = round(row[9], 0)
    #     path = '/media/pi/capra-hd/hike{}/'.format(str(row[0]))
    #     statement = 'UPDATE hikes SET avg_altitude = {a}, start_time = {st}, end_time = {et}, path = "{p}" \
    #                 WHERE hike_id = {id}'.format(a=avg_alt, st=stime, et=etime, p=path, id=row[0])
    #
    #     print(statement)
    #     destCursor.execute(statement)
    #
    # destConnection.commit()

    # --------------------------
    # UPDATE pictures SET hike = {} WHERE hike = {}
    # UPDATE pictures SET picture_id = picture_id + {}
    # --------------------------

    # ## update camera1, camera2, camera3, camera_landscape in pictures
    # statement = 'SELECT * FROM pictures ORDER BY time ASC'
    # destCursor.execute(statement)
    # pictureRows = destCursor.fetchall()

    #
    # for row in pictureRows:
    #     # time = 1
    #     # camera1 = 23
    #     # camera2 = 24
    #     # camera3 = 25
    #     # camera_landscape = 26
    #     time = round(row[1], 0)
    #     c1 = '/media/pi/capra-hd/hike{}/{}_cam1.jpg'.format(str(row[7]), str(row[8]))
    #     c2 = '/media/pi/capra-hd/hike{}/{}_cam2.jpg'.format(str(row[7]), str(row[8]))
    #     c3 = '/media/pi/capra-hd/hike{}/{}_cam3.jpg'.format(str(row[7]), str(row[8]))
    #     cl = '/media/pi/capra-hd/hike{}/{}_cam2f.jpg'.format(str(row[7]), str(row[8]))
    #     statement = 'UPDATE pictures SET time = {t}, camera1 = "{c1}", camera2 = "{c2}", camera3 = "{c3}", camera_landscape="{cl}" \
    #                 WHERE picture_id = {id}'.format(t=time, c1=c1, c2=c2, c3=c3, cl=cl, id=row[0])
    #
    #     # print(statement)
    #     destCursor.execute(statement)
    #
    # destConnection.commit()
    # destConnection.close()
    #
    # exit()

    # filter out zero byte pictures in the source DB upon starting
    # filterZeroBytePicturesFromSrc()

    latest_src_hikeID = dbSRCController.get_last_hike_id()
    latest_dest_hikeID = dbDESTController.get_last_hike_id()
    print("[{}] @@@ # hikes on from Source: {}".format(timenow(), str(latest_src_hikeID)))
    print("[{}] @@@ # hikes on at Dest: {}".format(timenow(), str(latest_dest_hikeID)))

    currHike = 1
    checkSum_transferred = 0
    checkSum_rotated = 0
    checkSum_total = 0

    dummyGlobalCounter = 1
    masterTimer = time.time()

    while currHike <= latest_src_hikeID:

        # if (currHike > 1):
        #     break
        #
        # validRows = dbSRCController.get_valid_photos_in_given_hike(currHike)
        # numValidRows = len(validRows)
        # maxRows = dbSRCController.get_last_photo_index_of_hike(currHike)
        #
        # print("[{}] Last index in Hike {}: {}".format(timenow(), str(currHike), str(maxRows)))
        # print("[{}] Expected valid row count: {}".format(timenow(), str(numValidRows)))
        #

        srcPath = build_hike_path(DROPBOX + BASEPATH_SRC, currHike)
        currExpectedHikeSize = dbSRCController.get_size_of_hike(currHike)

        if (currExpectedHikeSize is None):
            currExpectedHikeSize = 0

        # 1. skip empty hikes
        #       + also skip small hikes (< 20) [Jul 8, 2021]
        if (currExpectedHikeSize == 0):
            print("[{}] Hike {} is empty. Proceeding to the next hike...".format(timenow(), str(currHike)))
            currHike += 1
            continue

        elif (currExpectedHikeSize < 20):
            print("[{}] Hike {} seems to be very small (Only {} rows). Skipping the hike...".format(timenow(), str(currHike), str(currExpectedHikeSize)))
            currHike += 1
            continue

        else:
            hikeTimer = time.time()

            destPath = build_hike_path(DROPBOX + BASEPATH_DEST, currHike, True)
            expectedCheckSumTotal = currExpectedHikeSize * 4
            checkSum_transferred, checkSum_rotated, checkSum_total = compute_checksum(destPath, currHike)

            print("[{}] Hike {}: {} files transferred from SRC, {} files expected".format(timenow(), str(currHike), str(checkSum_transferred), str(currExpectedHikeSize*3)))
            print("[{}] Hike {}: {} files expected at DEST, {} files exist".format(timenow(), str(currHike), str(expectedCheckSumTotal), str(checkSum_total)))
            print("[{}] Hike {}: post-processing status: {}".format(timenow(), str(currHike), str(check_hike_postprocessing(currHike))))

            # 2. if a hike is fully transferred, resized and rotated, then skip the transfer for this hike
            # also check if DB is updated to post-processed values as well
            if (checkSum_transferred == currExpectedHikeSize * 3 and
                expectedCheckSumTotal == checkSum_total and
                check_hike_postprocessing(currHike)):

                print("[{}]     # Hike {} fully transferred. Proceeding to the next hike...".format(timenow(), str(currHike)))
                dummyGlobalCounter += currExpectedHikeSize

            else:
                hikeTimer = time.time()
                print("[{}] Processing Hike {}".format(timenow(), str(currHike)))
                buildHike(currHike)
                print("[{}] --- Hike {} took {} seconds".format(timenow(), str(currHike), str(time.time() - hikeTimer)))

            currHike += 1
            globalCounter_h += currExpectedHikeSize

    ### At this point, all hikes are processed.

    print("[{}] --- Building the projector DB took {} seconds ---".format(timenow(), str(time.time() - masterTimer)))



if __name__ == "__main__":
    main()
