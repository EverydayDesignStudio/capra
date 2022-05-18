import glob     # File path pattern matching
import os
import sys
import os.path
import datetime
import shutil
import cv2      # pip install opencv-python : for resizing image
import time
import sqlite3      # Database Library
import subprocess
import pipes        # Deploy RSyncs
import traceback
from operator import itemgetter
from pathlib import Path
import logging          ### TODO: add and replace prints with logs to create log files
import RPi.GPIO as GPIO

# image & color processing
from PIL import ImageTk, Image      # Pillow image functions
import math
from colorsys import rgb_to_hsv
import numpy as np

# threading
import threading
from concurrent import futures
from concurrent.futures import ThreadPoolExecutor

# custom modules
from classes.capra_data_types import Picture, Hike
from classes.sql_controller import SQLController
from classes.sql_statements import SQLStatements
from classes.kmeans import get_multiple_dominant_colors
from classes.kmeans import get_dominant_color_1D
from classes.kmeans import hsvToRgb
import globals as g
g.init()

# transfer animation
import platform
from sqlite3.dbapi2 import connect
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from classes.ui_components import *
from projector_slideshow import *

global globalPicture

VERBOSE = False
VERBOSE_HALL_EFFECT = False

GPIO.setmode(GPIO.BCM)                              # Set's GPIO pins to BCM GPIO numbering
GPIO.setup(g.HALL_EFFECT_PIN, GPIO.IN)              # Set our input pin to be an input
HALL_EFFECT_ON = threading.Event()                  # https://blog.miguelgrinberg.com/post/how-to-make-python-wait

logger = None
rsync_status = None
RETRY = 0
RETRY_MAX = 5

TRANSFER_DONE = False

TWO_CAM = False         # special variable to transfer hikes with only two cameras (for Jordan's 9 early hikes)

currHike = -1
globalCounter_h = 0
dummyGlobalColorRank = -1
dummyGlobalAltRank = -1
dummyGlobalCounter = 0

COLOR_HSV_INDEX = -1    # used in the sortColor helper function

commits = []        # deferred commits due to concurrency
threads = []
threadPool = None

# ### Database location ###

# Projector
CAPRAPATH = g.CAPRAPATH_PROJECTOR
DATAPATH = g.DATAPATH_PROJECTOR
PROJECTOR_DB = DATAPATH + g.DBNAME_MASTER
PROJECTOR_BAK_DB = DATAPATH + g.DBNAME_MASTER_BAK

# Camera
CAMERA_DB = DATAPATH + g.DBNAME_CAMERA
CAMERAPATH_REMOTE = g.DATAPATH_CAMERA
CAMERA_DB_REMOTE = CAMERAPATH_REMOTE + g.DBNAME_CAMERA
CAMERA_BAK_DB = DATAPATH + g.DBNAME_CAMERA_BAK

WHITE_IMAGE = DATAPATH + "white.jpg"


# need this indexes hardcoded for the python helper function
# *** These are indexes at the destDB (projector), so the srcDB type doesn't matter
ALTITUDE_INDEX = 10
COLOR_INDEX_HSV = 14
INDEX_IN_HIKE_INDEX = 8

CLUSTERS = 5        # assumes X number of dominant colors in a pictures
REPETITION = 8

# place holder variables for buildling file paths
srcPath = ""
destPath = ""

dbSRCController = None
dbDESTController = None

FILENAME = "[!\.]*_cam[1-3].jpg"
FILENAME_FULLSIZE = "[!\.]*_cam2f.jpg"
# sample dimensions: (100, 60), (160, 95), (320, 189), (720, 427)
DIMX = 100
DIMY = 60
TOTAL = DIMX * DIMY

# https://stackoverflow.com/questions/60977224/pyqt-multithreaded-program-based-on-qrunnable-is-not-working-properly
capraThreadpool = QThreadPool()
transferThreadpool = QThreadPool()

CURRENT_WINDOW = None

#######################################################################
#####                   BACKGROUND PROCESSES                      #####
#######################################################################

class ReadHallEffectThread(QRunnable):
    def __init__(self):
        super(ReadHallEffectThread, self).__init__()
        # self.start()
        self.signals = WorkerSignals()

    def run(self):
        while True:
            if self.signals.terminate:  # Garbage collection
                break

            if (GPIO.input(g.HALL_EFFECT_PIN)):
                g.HALL_EFFECT = False
            else:
                g.HALL_EFFECT = True

            if (g.HALL_EFFECT != g.PREV_HALL_VALUE):
                if (g.HALL_BOUNCE_TIMER is None):
                    if (VERBOSE_HALL_EFFECT):
                        print("[{}] Hall-effect seneor signal change! Setting the timer..".format(timenow()))
                    g.HALL_BOUNCE_TIMER = current_milli_time()

                if (current_milli_time() - g.HALL_BOUNCE_TIMER > g.HALL_BOUNCE_LIMIT):
                    if (VERBOSE_HALL_EFFECT):
                        print("[{}] The signal is valid! Changing the state.".format(timenow()))
                    if (g.HALL_EFFECT):
                        if (VERBOSE_HALL_EFFECT):
                            print("[{}] \tFalse -> True \\\\ Magnet Attached".format(timenow()))
                        g.PREV_HALL_VALUE = True
                        HALL_EFFECT_ON.set()
                        g.flag_start_transfer = True
                    else:
                        if (VERBOSE_HALL_EFFECT):
                            print("[{}] \tTrue -> False \\\\ Magnet Detached".format(timenow()))
                        g.PREV_HALL_VALUE = False
                        HALL_EFFECT_ON.clear()
                        g.flag_start_transfer = False

            elif (g.HALL_BOUNCE_TIMER is not None):
                if (VERBOSE_HALL_EFFECT):
                    print("[{}] Signal change is lost. Resetting the timer".format(timenow()))
                g.HALL_BOUNCE_TIMER = None


class PingCameraThread(QRunnable):
    def __init__(self):
        super(PingCameraThread, self).__init__()
        self.signals = WorkerSignals()

    # https://stackoverflow.com/questions/35750041/check-if-ping-was-successful-using-subprocess-in-python
    # https://stackoverflow.com/questions/28769023/get-output-of-system-ping-without-printing-to-the-console
    def run(self):
        while True:
            if self.signals.terminate:  # Garbage collection
                break

            proc = subprocess.Popen(
                ['ping', '-q', '-c', '1', g.IP_ADDR_CAMERA],
                stdout=subprocess.DEVNULL)
            proc.wait()

            if proc.poll():
                g.CAMERA_UP = False
            else:
                g.CAMERA_UP = True

            # print("Is Camera Up? - {}".format(g.CAMERA_UP))
            time.sleep(1)


#######################################################################
#####                         LOGGING                             #####
#######################################################################

def createLogger():
    global logger

    # ### Create Logger ###
    if os.name == 'nt':
        log_file = "C:\tmp\transfer.log"
    else:
        directory = CAPRAPATH + "log/"
        log_file = directory + 'transferLog-' + time.strftime("%Y%m%d") + '.log'
        if not os.path.exists(directory):
            os.makedirs(directory, exist_ok=True, mode=0o755)

    # create logger with 'spam_application'
    logger = logging.getLogger('CapraTransferLogger')
    logger.setLevel(logging.INFO)

    # create file handler which logs even debug messages
    fh = logging.FileHandler(log_file, 'a+')
    fh.setLevel(logging.INFO)
    logger.addHandler(fh)


#######################################################################
#####                    AUXILIARY FUNCTIONS                      #####
#######################################################################

def timenow():
    return str(datetime.datetime.now()).split('.')[0]


def current_milli_time():
    return int(round(time.time() * 1000))


def formatColors(colors):
    res = ""
    for color in colors:
        res += ",".join(map(str, color)) + "|"
    return res[:-1]


def roundToInt(lst):
    for i in range(len(lst)):
        lst[i] = round(float(lst[i]), 0)
    return lst


def roundToHundredth(lst):
    for i in range(len(lst)):
        lst[i] = round(float(lst[i]), 2)
    return lst


#######################################################################
#####                     DATABASE FUNCTIONS                      #####
#######################################################################

def isDBNotInSync():
    proc = subprocess.Popen(["sqldiff", CAMERA_DB, CAMERA_BAK_DB], stdout=subprocess.PIPE)
    line = proc.stdout.readline()
    if line != b'':
        # there are new incoming changes in DB
        return True
    else:
        # two databases are identical
        return False


def copy_remote_db():
    if (exists_remote(CAMERA_DB_REMOTE)):
        print("[{}] @@ Found the remote DB. Copying over..".format(timenow()))
        subprocess.Popen(['rsync', '--inplace', '-avAI', '--no-perms', '--rsh="ssh"', "pi@" + g.IP_ADDR_CAMERA + ":" + CAMERA_DB_REMOTE, DATAPATH], stdout=subprocess.PIPE)
    else:
        print("[{}] @@ Did NOT locate the remote DB! :\\".format(timenow()))

    time.sleep(1)
    return


def copy_local_camera_db_to_remote():
    subprocess.Popen(['rsync', '--inplace', '-avAI', '--no-perms', '--rsh="ssh"', CAMERA_DB ,"pi@" + g.IP_ADDR_CAMERA + ":" + CAMERAPATH_REMOTE], stdout=subprocess.PIPE)
    return


def copy_master_db():
    subprocess.Popen(['cp', PROJECTOR_DB, PROJECTOR_BAK_DB], stdout=subprocess.PIPE)
    return


def make_backup_remote_db():
    subprocess.Popen(['cp', CAMERA_DB, CAMERA_BAK_DB], stdout=subprocess.PIPE)
    return


# 1. make db connections
def getDBControllers():
    global dbSRCController, dbSRCController_remote, dbDESTController

    # this is a locally saved db, copied from camera
    dbSRCController = SQLController(database=CAMERA_DB)

    # the remote database in the camera
    dbSRCController_remote = SQLController(database=CAMERA_DB_REMOTE)

    # if dest does not exist, create a new DB by copying and renaming the skeleton file
    if (not os.path.exists(PROJECTOR_DB)):
        src_file = DATAPATH + g.DBNAME_INIT
        shutil.copy(src_file, DATAPATH + g.DBNAME_MASTER) # copy the file to destination dir

    dbDESTController = SQLController(database=PROJECTOR_DB)


#######################################################################
#####                   PATH-RELATED FUNCTIONS                    #####
#######################################################################

def build_hike_path(path, hikeID, makeNew=False):
    res = path + 'hike' + str(hikeID) + '/'
    if makeNew and not os.path.exists(res):
        os.makedirs(res, mode=0o755)
    return res


def escape_whitespace(path_string):
    return path_string.replace(" ", "\\ ")


#######################################################################
#####                CHECKSUM AND GUARD FUNCTIONS                 #####
#######################################################################

def exists_remote(path):
    return subprocess.call(['ssh', 'pi@' + g.IP_ADDR_CAMERA, 'test -e ' + pipes.quote(path)]) == 0    # https://tldp.org/LDP/abs/html/fto.html


def exists_non_zero_remote(path):
    return subprocess.call(['ssh', 'pi@' + g.IP_ADDR_CAMERA, 'test -s ' + pipes.quote(path)]) == 0


def count_files_in_directory(path, pattern):
    if (not os.path.exists(path)):
        return 0
    else:
        return len(glob.glob(path + pattern))


def compute_checksum(path, currHike):
    checkSum_transferred = count_files_in_directory(path, FILENAME)
    checkSum_rotated = count_files_in_directory(path, FILENAME_FULLSIZE)
    return checkSum_transferred, checkSum_rotated, checkSum_transferred + checkSum_rotated


def check_hike_postprocessing(currHike):
    hikeColor = dbDESTController.get_hike_average_color(currHike)
    nonEmpty_color_with_proper_values = hikeColor is not None and hikeColor and not (hikeColor[0] < 0.001 and hikeColor[1] < 0.001 and hikeColor[2] < 0.001)

    if (not nonEmpty_color_with_proper_values):
        print("[{}] !! Hike {}'s dominant color has not computed yet.".format(timenow(), currHike))

    pictures_negative_rank_count = dbDESTController.validate_hike_negative_rank_count_pictures(currHike)
    hikes_rank_values = dbDESTController.validate_hike_get_hike_ranks(currHike)
    no_negative_rank_values = hikes_rank_values is not None and pictures_negative_rank_count == 0 and hikes_rank_values[0] > 0 and hikes_rank_values[1] > 0

    if (not no_negative_rank_values):
        print("[{}] !! Some rank values are not fully computed for Hike {}.".format(timenow(), currHike))

    return nonEmpty_color_with_proper_values and no_negative_rank_values


#######################################################################
#####                   COLOR-RELATED FUNCTIONS                   #####
#######################################################################

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
    h, s, v = rgb_to_hsv(r, g, b)

    h2 = int(h * repetitions)
    v2 = int(v * repetitions)

    # Connects the blacks and whites between each hue chunk
    # Every other (each even) color hue chunk, the values are flipped so the
    # white values are on the left and the black values are on the right
    if h2 % 2 == 1:
        v2 = repetitions - v2
        lum = repetitions - lum

    return (h2, lum)


#######################################################################
#####                  RANKING-RELATED FUNCTIONS                  #####
#######################################################################

def sort_by_alts(data, alt_index, index_in_hike):
    data.sort(key=itemgetter(alt_index, 0))  # 10 - altitude

    rankList = {}
    for i in range(len(data)):
        rankList[itemgetter(index_in_hike)(data[i])] = i+1   # 8 - index_in_hike

    return rankList


def splitColor(item):
    tmp = itemgetter(COLOR_HSV_INDEX)(item)      # 14 - color_hsv, 1 - color_hsv for global ranking
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


#######################################################################
#####                   MAJOR WRAPPER FUNCTIONS                   #####
#######################################################################

def dominantColorWrapper(currHike, validRowCount, row_src, image1, image2, image3=None, image_processing_size=None):
    global dummyGlobalCounter, globalPicture

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

    commit = [round(row_src['time'], 0),
                picDatetime.year, picDatetime.month, picDatetime.day, picDatetime.hour * 60 + picDatetime.minute, picDatetime.weekday(),
                currHike, validRowCount, dummyGlobalCounter,
                round(row_src['altitude'], 2), -1, -1, dummyGlobalCounter,
                ",".join(map(str, colors_hsv[0])), ",".join(map(str, colors_rgb[0])), -1, -1, -1, dummyGlobalCounter,
                color_size, formatColors(colors_rgb), ",".join(map(str, confidences)),
                camera1, camera2, camera3, camera2f, row_src['created_date_time']]

    globalPicture = Picture(dummyGlobalCounter,
                            round(row_src['time'], 0), picDatetime.year, picDatetime.month, picDatetime.day, picDatetime.hour * 60 + picDatetime.minute, picDatetime.weekday(),
                            currHike, validRowCount, dummyGlobalCounter,
                            round(row_src['altitude'], 2), -1, -1, dummyGlobalCounter,
                            ",".join(map(str, colors_hsv[0])), ",".join(map(str, colors_rgb[0])), -1, -1, dummyGlobalCounter,
                            color_size, formatColors(colors_rgb), ",".join(map(str, confidences)),
                            DATAPATH + camera1, DATAPATH + camera2, DATAPATH + camera3, DATAPATH + camera2f, row_src['created_date_time'], row_src['updated_date_time'])

    return commit, colors_hsv[0]


## this is essentially the main function
def buildHike(currHike):
    global dbSRCController, dbSRCController_remote, dbDESTController
    global srcPath, destPath
    global dummyGlobalColorRank, dummyGlobalAltRank, dummyGlobalCounter, globalCounter_h

    global rsync_status, hall_effect
    global logger
    global threads, threadPool
    global COLOR_HSV_INDEX, TRANSFER_DONE

    avgAlt = 0
    startTime = 9999999999
    endTime = -1
    domColorsHike_hsv = []
    pics = {}
    commits = {}
    threads = []
    threadPool = ThreadPoolExecutor(max_workers=5)

    validRowCount = 0           ### This is the 'corrected' numValidRows [May 14, 2021]
    index_in_hike = 0
    validRows = dbSRCController.get_valid_photos_in_given_hike(currHike)
    numValidRows = len(validRows)
    maxRows = dbSRCController.get_last_photo_index_of_hike(currHike)

    deleteCount = 0             ### to track rows that contain 0 byte pictures in the remote database
    deleteTimestamps = []       ### timestamps of rows to delete

    print("[{}] Last index in Hike {}: {}".format(timenow(), str(currHike), str(maxRows)))
    print("[{}] Expected valid row count: {}".format(timenow(), str(numValidRows)))

    while (index_in_hike <= maxRows + 2):   # allow a loose upper bound (max + 2) to handle the last index

        # check the connection before processing a new row
        if (not g.HALL_EFFECT):
            print("[{}]     HALL-EFFECT SIGNAL LOST !! Terminating transfer process..".format(timenow()))
            logger.info("[{}]     HALL-EFFECT SIGNAL LOST !! Terminating transfer process..".format(timenow()))
            return 1

        row_src = dbSRCController.get_hikerow_by_index(currHike, index_in_hike)

        picPathCam1_src = srcPath + "{}_cam1.jpg".format(index_in_hike)
        picPathCam2_src = srcPath + "{}_cam2.jpg".format(index_in_hike)
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

            if (not exists_remote(picPathCam1_src) or not exists_remote(picPathCam2_src)):
                index_in_hike += 1
                continue

            # check for 0 byte pictures
            #   if spotted, increase deleteCounter and delete those rows
            #   from the remote camera db and the local camera db before proceeding to the next hike
            if (not exists_non_zero_remote(picPathCam1_src) or not exists_non_zero_remote(picPathCam2_src) or
                (not TWO_CAM and not exists_non_zero_remote(picPathCam3_src))):
                print("[{}] \t Row {} has a missing picture. Deleting a row..".format(timenow(), index_in_hike))
                deleteCount += 1
                deleteTimestamps.append(row_src['time'])
                index_in_hike += 1
                continue

            # transfer pictures only when the paths do not exist on the projector
            if (not os.path.exists(picPathCam1_dest)
                or not os.path.exists(picPathCam2_dest)
                or not os.path.exists(picPathCam3_dest)):

                # remove partially transferred files
                if (os.path.exists(picPathCam1_dest)
                    or os.path.exists(picPathCam2_dest)
                    or os.path.exists(picPathCam3_dest)):

                    tmpPath = picPathCam1_dest[:-5]
                    for tmpfile in glob.glob(tmpPath + '*'):
                        os.remove(tmpfile)

                # grab a set of three pictures for each row using regEx
                #     "/home/pi/capra-storage/hike1/1_cam2.jpg"
                #      --> "/home/pi/capra-storage/hike1/1_cam*"

                # srcFilePathBlob = row_src['camera2'][:-5] + {index} + "_cam" + '*'

                tmp = row_src['camera2'].split('/')
                srcFilePathBlob = srcPath + tmp[4][:-5] + str(index_in_hike) + "_cam" + '*'

                # TODO: '--remove-source-files'
                rsync_status = subprocess.Popen(['rsync', '--ignore-existing', '-avA', '--no-perms', '--rsh="ssh"', 'pi@' + g.IP_ADDR_CAMERA + ':' + srcFilePathBlob, destPath], stdout=subprocess.PIPE)
                rsync_status.wait()

                # report if rsync is failed
                if (rsync_status.returncode != 0):
                    print("[{}] ### Rsync failed at row {}".format(timenow(), str(index_in_hike - 1)))
                    logger.info("[{}] ### Rsync failed at row {}".format(timenow(), str(index_in_hike - 1)))

                    # double-check if the failture is due to losing remote connection to the camera
                    if (not g.CAMERA_UP):
                        print("[{}]     CAMERA SIGNAL LOST !! Please check the connection and retry. Terminating transfer process..".format(timenow()))
                        logger.info("[{}]     CAMERA SIGNAL LOST !! Please check the connection and retry. Terminating transfer process..".format(timenow()))

                    # return an arbitrary error code
                    return 1

            # rotate and resize, copy those to the dest folder
            img = None
            img_res = None
            # resize and rotate for newly added pictures
            try:
                #    1. make a copy of pic2 as pic2'f'
                if (not os.path.exists(picPathCam2f_dest)):
                    img = Image.open(picPathCam2_dest)
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
            domColorsHike_hsv.append(domCol_hsv)

        else:
            threads.append(threadPool.submit(dominantColorWrapper, currHike, validRowCount, row_src, picPathCam1_dest, picPathCam2_dest, picPathCam3_dest, (DIMX, DIMY)))

        dummyGlobalCounter += 1
        index_in_hike += 1

    print("[{}] ### Waiting for Futures..".format(timenow()))

    # wait for threads to finish
    for thread in futures.as_completed(threads):
        commit, domCol_hsv = thread.result()
        domColorsHike_hsv.append(domCol_hsv)
        rowIdx = commit[7]
        fileName = "{}_camN".format(rowIdx)
        commits[fileName] = commit

        if (rowIdx % 100 == 0):
            print("[{}]   Checkpoint for Futures at {}".format(timenow(), str(commit[7])))

        # if (rowIdx % 100 == 0):
        #     # display an random picture in the current hike
        #     # these pictures are already in the database, so no need to worry about building a picture object
        #     print("[{}]   Checkpoint for Futures at {} - Transfer Amination Updated.".format(timenow(), str(rowIdx)))
        #     if (rowIdx == 0):
        #         globalPicture = dbDESTController.get_random_picture_of_given_hike(currHike)
        #     else:
        #         globalPicture = dbDESTController.get_random_picture_of_given_hike_within_range(currHike, rowIdx, rowIdx-100)


    threadPool.shutdown(wait=True)

    print("[{}] ### Copying pictures for hike {} done! {} valid rows out of {} rows.".format(timenow(), currHike, validRowCount, maxRows))
    print("[{}] ### Post-processing begins, calculating ranks within the hike..".format(timenow()))

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

       # print("[{}] altRank: {}, altRankG: {}, altRankG_h: {}, tcolRank: {}, colRankG: {}, colRankG_h: {}".format(i, altrank, dummyGlobalAltRank, str(globalCounter_h + altrank), colrank, dummyGlobalColorRank, str(globalCounter_h + colrank)))

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
    generatePics(colorSpectrumRGB_Global, "hike-global-colorSpectrum", DATAPATH)

    colorSpectrumRGB_Global_h = dbDESTController.get_pictures_rgb_global_h()
    generatePics(colorSpectrumRGB_Global_h, "hike-global-h-colorSpectrum", DATAPATH)

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

    print("[{}] --- Global rankings for Hikes took {} seconds.".format(timenow(), str(time.time() - timer4)))

    print("[{}] --- Global ranking took {} seconds.".format(timenow(), str(time.time() - rankTimer)))
    print("[{}] --- Moving on to the next hike!".format(timenow()))

    return 0


def start_transfer():
    global dbSRCController, dbDESTController, dummyGlobalColorRank, dummyGlobalAltRank, dummyGlobalCounter, globalCounter_h
    global srcPath, destPath
    global COLOR_HSV_INDEX, TRANSFER_DONE

    global rsync_status, hall_effect
    global logger
    global threads, threadPool

    latest_master_hikeID = dbDESTController.get_last_hike_id()
    latest_remote_hikeID = dbSRCController.get_last_hike_id()
    print("[{}] @@@ # hikes on Projector: {}".format(timenow(), str(latest_master_hikeID)))
    print("[{}] @@@ # hikes on Camera: {}".format(timenow(), str(latest_remote_hikeID)))
    logger.info("[{}] @@@ # hikes on Projector: {}".format(timenow(), str(latest_master_hikeID)))
    logger.info("[{}] @@@ # hikes on Camera: {}".format(timenow(), str(latest_remote_hikeID)))

    currHike = 1
    checkSum_transferred = 0
    checkSum_rotated = 0
    checkSum_total = 0

    resCode_buildHike = 0

    dummyGlobalCounter = 1
    masterTimer = time.time()

    while currHike <= latest_remote_hikeID:

        # Check signals before processing each hike
        if (not g.HALL_EFFECT):
            print("[{}]     HALL-EFFECT SIGNAL LOST !! Terminating transfer process..".format(timenow()))
            logger.info("[{}]     HALL-EFFECT SIGNAL LOST !! Terminating transfer process..".format(timenow()))
            return 1

        if (not g.CAMERA_UP):
            print("[{}]     CAMERA SIGNAL LOST !! Please check the connection and retry. Terminating transfer process..".format(timenow()))
            logger.info("[{}]     CAMERA SIGNAL LOST !! Please check the connection and retry. Terminating transfer process..".format(timenow()))
            return 1

        srcPath = build_hike_path(CAMERAPATH_REMOTE, currHike)
        currExpectedHikeSize = dbSRCController.get_size_of_hike(currHike)

        if (currExpectedHikeSize is None):
            currExpectedHikeSize = 0

        # Skip empty or small hikes that have less than 20 rows [Jul 8, 2021]
        if (currExpectedHikeSize == 0):
            print("[{}] Hike {} is empty. Proceeding to the next hike...".format(timenow(), str(currHike)))
            logger.info("[{}] Hike {} is empty. Proceeding to the next hike...".format(timenow(), str(currHike)))
            currHike += 1
            continue

        elif (currExpectedHikeSize < 20):
            print("[{}] Hike {} seems to be very small (Only {} rows). Skipping the hike...".format(timenow(), str(currHike), str(currExpectedHikeSize)))
            currHike += 1
            continue


        else:
            hikeTimer = time.time()

            destPath = build_hike_path(DATAPATH, currHike, True)
            expectedCheckSumTotal = currExpectedHikeSize * 4
            checkSum_transferred, checkSum_rotated, checkSum_total = compute_checksum(destPath, currHike)
            isHikeFullyProcessed = check_hike_postprocessing(currHike)

            print("[{}] Hike {}: {} files transferred from SRC, {} files expected".format(timenow(), str(currHike), str(checkSum_transferred), str(currExpectedHikeSize*3)))
            print("[{}] Hike {}: {} files expected at DEST, {} files exist".format(timenow(), str(currHike), str(expectedCheckSumTotal), str(checkSum_total)))
            print("[{}] Hike {}: post-processing status: {}".format(timenow(), str(currHike), str(isHikeFullyProcessed)))

            # If a hike is fully transferred, resized and rotated, then skip the transfer for this hike
            # also check if DB is updated to post-processed values as well
            if (checkSum_transferred == currExpectedHikeSize * 3 and
                expectedCheckSumTotal == checkSum_total and
                isHikeFullyProcessed):

                print("[{}]     # Hike {} fully transferred. Proceeding to the next hike...".format(timenow(), str(currHike)))
                logger.info("[{}]     # Hike {} fully transferred. Proceeding to the next hike...".format(timenow(), str(currHike)))
                dummyGlobalCounter += currExpectedHikeSize

            else:
                hikeTimer = time.time()
                print("[{}] Processing Hike {}".format(timenow(), str(currHike)))
                resCode_buildHike = buildHike(currHike)

                if (resCode_buildHike):
                    print("[{}] Could not finish hike {}.".format(timenow(), str(currHike)))
                    return 1


                ### TODO: send a signal to remote to delete the hike pictures here


                print("[{}] --- Hike {} took {} seconds".format(timenow(), str(currHike), str(time.time() - hikeTimer)))

            currHike += 1
            globalCounter_h += currExpectedHikeSize

    ### [Apr 1, 2022]
    #   This is the only case that indicates all hikes are checked.
    if (currHike > latest_remote_hikeID):
        TRANSFER_DONE = True

    print("[{}] --- Building the projector DB took {} seconds ---".format(timenow(), str(time.time() - masterTimer)))

    return 0

# ==================================================================

# def trasnferMain():
#     global RETRY, TRANSFER_DONE
#
#     readHallEffectThread()
#     createLogger()
#     TRANSFER_DONE = False
#
#     resCode_startTransfer = 0
#
#     while True:
#         print("[{}] Waiting on the hall-effect sensor.".format(timenow()))
#         HALL_EFFECT_ON.wait()
#
#         start_time = time.time()
#         try:
#             if (isCameraUp()):
#
#                 # Start by copying the remote DB over to the projector
#                 print("[{}] Copying the camera DB over to the Projector..".format(timenow()))
#                 copy_remote_db()
#
#                 # if camera DB is still fresh, do not run transfer script
#                 if (os.path.exists(CAMERA_DB) and
#                     os.path.exists(CAMERA_BAK_DB) and
#                     not isDBNotInSync()):
#
#                     print("[{}] ## DB is still fresh. No incoming data.".format(timenow()))
#                     print("[{}] ## Proceed with the existing reference to the remote DB.".format(timenow()))
#
#                     ### TODO: may need a better flow
#                     if (TRANSFER_DONE):
#                         print("[{}] ## DB is still fresh. No incoming data.".format(timenow()))
#                         g.flag_start_transfer = False
#                         HALL_EFFECT_ON.clear()
#                         continue
#
#                     ### [Apr 1, 2022]
#                     ### TODO: At this point, we are in the stable status.
#                     ###       Play 'done' screen and play the transfer animation recap
#
#                 else:
#                     print("[{}] ## Change detected in the Remote DB. Start syncing..".format(timenow()))
#                     TRANSFER_DONE = False
#
#                 ### Do we really need this? hmm..
#                 # # copy the current snapshot of master DB for checking references
#                 # print("[{}] \t Making a copy of the master DB on the Projector..".format(timenow()))
#                 # copy_master_db()
#
#                 print("[{}] \t Creating DB controllers..".format(timenow()))
#                 getDBControllers()
#
#                 print("[{}] Starting the transfer now..".format(timenow()))
#                 resCode_startTransfer = start_transfer()
#
#                 if (resCode_startTransfer):
#                     print("[{}] Transfer could not finish. Putting transfer script to sleep..".format(timenow()))
#                     continue
#
#                 print("[{}] --- Transfer is finished in {} seconds ---".format(timenow(), str(time.time() - start_time)))
#                 logger.info("[{}] --- Transfer is finished in {} seconds ---".format(timenow(), str(time.time() - start_time)))
#
#                 # In case if the referenced camera db (local copy) is changed due to 0 byte or incomputable pictures,
#                 # sync the remote db by overwriting with the updated camera db on the projector
#                 if (isDBNotInSync() and TRANSFER_DONE):
#                     print("[{}] Changes have been made to the remote DB while transfer. Updating the changes to the remote..".format(timenow()))
#                     copy_local_camera_db_to_remote()
#
#                 # if transfer is successfully finished pause running until camera is dismounted and re-mounted
#                 print("[{}] Transfer finished. Pause the script".format(timenow()))
#                 make_backup_remote_db()
#
#                 g.flag_start_transfer = False
#                 HALL_EFFECT_ON.clear()
#
#             else:
#                 print("[{}]     CAMERA SIGNAL LOST !! Please check the connection and retry. Terminating transfer process..".format(timenow()))
#                 logger.info("[{}]     CAMERA SIGNAL LOST !! Please check the connection and retry. Terminating transfer process..".format(timenow()))
#
#
#         # TODO: clean up hanging processes when restarting
#         #           fuser capra_projector.db -k
#         except Exception as e:
#             print("[{}]: !!   Encounter an exception while transferring restarting the script..".format(timenow()))
#             logger.info("[{}]: !!   Encounter an exception while transferring restarting the script..".format(timenow()))
#             if hasattr(e, 'message'):
#                 print(e.message, '\n')
#             print(e)
#             print(traceback.format_exc())
#
#             if (RETRY < RETRY_MAX):
#                 python = sys.executable
#                 os.execl(python, python, * sys.argv)
#
#             RETRY += 1



#######################################################################
#####                    TRANSFER ANIMATION                       #####
#######################################################################

class WorkerSignals(QObject):
    '''
    Defines the signals available from a running worker thread.
    Supported signals are:

    finished
        No data passed, just a notifier of completion
    error
        `tuple` (exctype, value, traceback.format_exc() )
    result
        `object` data returned from processing, anything
    '''
    finished = pyqtSignal()
    error = pyqtSignal(tuple)
    result = pyqtSignal(object)
    '''
    Defines status which is checked for in infinite loop
    By setting to True, the thread will quit,
    and closing of the program won't hang
    '''
    terminate = False


class TransferThread(QRunnable):
    '''Thread for handling the main transfer task '''
    def __init__(self):
        super(TransferThread, self).__init__()

        # Needed setup
        self.signals = WorkerSignals()  # Setups signals that will be used to send data back to SlideshowWindow
                                        # Holds a terminate status, used to garbage collect threads

    def run(self):
        global RETRY, TRANSFER_DONE

        TRANSFER_DONE = False

        resCode_startTransfer = 0

        while True:
            # print("[{}] Waiting on the hall-effect sensor.".format(timenow()))
            # HALL_EFFECT_ON.wait()

            start_time = time.time()
            try:
                if (g.CAMERA_UP):

                    # Start by copying the remote DB over to the projector
                    print("[{}] Copying the camera DB over to the Projector..".format(timenow()))
                    copy_remote_db()

                    # if camera DB is still fresh, do not run transfer script
                    if (os.path.exists(CAMERA_DB) and
                        os.path.exists(CAMERA_BAK_DB) and
                        not isDBNotInSync()):

                        print("[{}] ## DB is still fresh. No incoming data.".format(timenow()))
                        print("[{}] ## Proceed with the existing reference to the remote DB.".format(timenow()))

                        ### TODO: may need a better flow
                        if (TRANSFER_DONE):
                            print("[{}] ## DB is still fresh. No incoming data.".format(timenow()))
                            g.flag_start_transfer = False
                            # HALL_EFFECT_ON.clear()
                            continue

                        ### [Apr 1, 2022]
                        ### TODO: At this point, we are in the stable status.
                        ###       Play 'done' screen and play the transfer animation recap

                    else:
                        print("[{}] ## Change detected in the Remote DB. Start syncing..".format(timenow()))
                        TRANSFER_DONE = False

                    ### Do we really need this? hmm..
                    # # copy the current snapshot of master DB for checking references
                    # print("[{}] \t Making a copy of the master DB on the Projector..".format(timenow()))
                    # copy_master_db()

                    print("[{}] \t Creating DB controllers..".format(timenow()))
                    getDBControllers()

                    print("[{}] Starting the transfer now..".format(timenow()))
                    resCode_startTransfer = start_transfer()

                    if (resCode_startTransfer):
                        print("[{}] Transfer could not finish. Putting transfer script to sleep..".format(timenow()))
                        break

                    print("[{}] --- Transfer is finished in {} seconds ---".format(timenow(), str(time.time() - start_time)))
                    logger.info("[{}] --- Transfer is finished in {} seconds ---".format(timenow(), str(time.time() - start_time)))

                    # In case if the referenced camera db (local copy) is changed due to 0 byte or incomputable pictures,
                    # sync the remote db by overwriting with the updated camera db on the projector
                    if (isDBNotInSync() and TRANSFER_DONE):
                        print("[{}] Changes have been made to the remote DB while transfer. Updating the changes to the remote..".format(timenow()))
                        copy_local_camera_db_to_remote()

                    # if transfer is successfully finished pause running until camera is dismounted and re-mounted
                    print("[{}] Transfer finished. Pause the script".format(timenow()))
                    make_backup_remote_db()

                    g.flag_start_transfer = False
                    HALL_EFFECT_ON.clear()

                else:
                    print("[{}]     CAMERA SIGNAL LOST !! Please check the connection and retry. Terminating transfer process..".format(timenow()))
                    logger.info("[{}]     CAMERA SIGNAL LOST !! Please check the connection and retry. Terminating transfer process..".format(timenow()))

                    ### TODO: if retry is exceeded
                    break


            # TODO: clean up hanging processes when restarting
            #           fuser capra_projector.db -k
            except Exception as e:
                print("[{}]: !!   Encounter an exception while transferring restarting the script..".format(timenow()))
                logger.info("[{}]: !!   Encounter an exception while transferring restarting the script..".format(timenow()))
                if hasattr(e, 'message'):
                    print(e.message, '\n')
                print(e)
                print(traceback.format_exc())

                if (RETRY < RETRY_MAX):
                    python = sys.executable
                    os.execl(python, python, * sys.argv)

                RETRY += 1


class TransferAnimationWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Capra Transfer Animation")
        self.setGeometry(0, 0, 1280, 720)

        # Setups up database connection depending on the system
        self.setupSQLController()

        global transferThreadpool

        # Setup Bg Thread for getting picture from Database
        # self.threadpool = QThreadPool()
        transferThreadpool.setMaxThreadCount(1)
        # self.newPictureThread = NewPictureThread(self.sql_controller)
        # self.threadpool.start(self.newPictureThread)
        global globalPicture

        ### TODO: when there is no existing picture in the DB, show the "start" screen
        globalPicture = self.sql_controller.get_random_picture()

        self.transferThread = TransferThread()
        transferThreadpool.start(self.transferThread)

        # Setup BG color
        # c1 = QColor(9, 24, 94, 255)
        self.bgcolor = BackgroundColor(self, QVBoxLayout(), Qt.AlignBottom, self.picture.color_rgb)

        self.setupColorWidgets(self.picture)
        self.setupAltitudeLabel(self.picture)
        self.setupTimeLabelAndBar(self.picture)

        self.superCenterImg = TransferCenterImage(self, self.picture)

        self.setupAltitudeGraphAndLine(self.picture)
        self.altitudegraph.hide()
        self.centerLabel.opacityHide()
        self.line.hide()

        # Setup QTimer for checking for new Picture
        self.handlerCounter = 1
        self.timerAnimationHandler = QTimer()
        self.timerAnimationHandler.timeout.connect(self.animationHandler)
        self.timerAnimationHandler.start(7000)

    def animationHandler(self):
        self.fadeOutTimer = QTimer()
        self.fadeOutTimer.setSingleShot(True)

        if self.handlerCounter % 4 == 1:  # Color
            self.fadeMoveInColorWidgets()
            self.fadeOutTimer.timeout.connect(self.fadeMoveOutColorWidgets)
        elif self.handlerCounter % 4 == 2:  # Altitude
            self.fadeMoveInAltitudeEverything()
            self.fadeOutTimer.timeout.connect(self.fadeMoveOutAltitudeEverything)
        elif self.handlerCounter % 4 == 3:  # Time
            self.fadeMoveInTime()
            self.fadeOutTimer.timeout.connect(self.fadeMoveOutTime)
        elif self.handlerCounter % 4 == 0:  # New Picture: image, bg color, ui elements
            global globalPicture
            ### TODO: what if there is no existing picture in the database? >> base case
            # self.picture = self.sql_controller.get_random_picture()
            # self.picture = globalPicture

            # remember previous picture and if identical, grab a random one
            print("             @@ Self.picture: hike {} - index {} | GlobalPicture: hike {} - index {}".format(self.picture.hike_id, self.picture.index_in_hike, globalPicture.hike_id, globalPicture.index_in_hike))
            if (self.picture.hike_id == globalPicture.hike_id and self.picture.index_in_hike == globalPicture.index_in_hike):
                print("[{}]     Global picture has not changed. Grabbing a random photo".format(timenow()))

                ### TODO: if there is no prior picture in the existing database, grab the start screen
                globalPicture = self.sql_controller.get_random_picture()

            self.picture = globalPicture

            # Update UI Elements
            self.updateColorWidgets(self.picture)
            self.updateTimeLabelAndBar(self.picture)
            self.updateAltitudeLabelAndGraph(self.picture)
            # self.setupTimeLabelAndBar(self.picture)
            # self.setupAltitudeLabel(self.picture)

            # Change Image and Background
            self.superCenterImg.fadeNewImage(self.picture)
            print("            @@ Transfer Animation Picture: Row {rowIdx} at Hike {hike}".format(rowIdx=self.picture.index_in_hike, hike=self.picture.hike_id))
            self.bgcolor.changeColor(self.picture.color_rgb)

        self.fadeOutTimer.start(3500)
        self.handlerCounter += 1

    # Database connection - previous db with UI data
    def setupSQLController(self):
        '''Initializes the database connection.\n
        If on Mac/Windows give dialog box to select database,
        otherwise it will use the global defined location for the database'''

        # Mac/Windows: select the location
        if platform.system() == 'Darwin' or platform.system() == 'Windows':
            # filename = QFileDialog.getOpenFileName(self, 'Open file', '', 'Database (*.db)')
            # self.database = filename[0]
            # self.directory = os.path.dirname(self.database)

            self.database = '/Users/myoo/Dropbox/Everyday Design Studio/A Projects/100 Ongoing/Capra/capra-storage/capra-storage-jordan-projector/capra_projector_jun2021_min_test_0708.db'
            self.directory = '/Users/myoo/Dropbox/Everyday Design Studio/A Projects/100 Ongoing/Capra/capra-storage/capra-storage-jordan-projector'
        else:  # Raspberry Pi: preset location
            self.database = g.DATAPATH_PROJECTOR + g.DBNAME_MASTER
            self.directory = g.DATAPATH_PROJECTOR

        print(self.database)
        print(self.directory)
        self.sql_controller = SQLController(database=self.database, directory=self.directory)

        # self.picture = self.sql_controller.get_picture_with_id(20000) # 28300
        self.picture = self.sql_controller.get_random_picture()

        # self.picture2 = self.sql_controller.get_picture_with_id(27500)
        # self.picture3 = self.sql_controller.get_picture_with_id(12000)
        # self.picture4 = self.sql_controller.get_picture_with_id(10700)
        # 10700, 11990, 12000, 15000, 20000, 27100, 27200, 27300, 27500, 28300

        # TODO - should we preload all the UI Data?
        # self.uiData = self.sql_controller.preload_ui_data()
        # self.preload = True

    # Time Mode
    def setupTimeLabelAndBar(self, picture: Picture):
        self.timeLabel = UILabelTopCenter(self, '', '')
        self.timeLabel.setPrimaryText(picture.uitime_hrmm)
        self.timeLabel.setSecondaryText(picture.uitime_ampm)

        try:
            percent_rank = self.sql_controller.ui_get_percentage_in_archive_with_mode('time', self.picture)
        except:
            percent_rank = 100
        self.timebar = TimeBarTransfer(self, percent_rank)

        self.timeLabel.opacityHide()
        self.timebar.hide()

    def updateTimeLabelAndBar(self, picture: Picture):
        self.timeLabel.setPrimaryText(picture.uitime_hrmm)
        self.timeLabel.setSecondaryText(picture.uitime_ampm)

        try:
            percent_rank = self.sql_controller.ui_get_percentage_in_archive_with_mode('time', self.picture)
        except:
            percent_rank = 100
        self.timebar.trigger_refresh(percent_rank)

    def fadeMoveInTime(self):
        self.timeLabel.show()
        self.timebar.show()

        # Move in top label
        self.animMoveInTimeLabel = QPropertyAnimation(self.timeLabel, b"geometry")
        self.animMoveInTimeLabel.setDuration(2000)
        self.animMoveInTimeLabel.setStartValue(QRect(0, 360, 1280, 110))
        self.animMoveInTimeLabel.setEndValue(QRect(0, 15, 1280, 110))
        self.animMoveInTimeLabel.start()

        # Fade in the timebar
        fadeTimebar = QGraphicsOpacityEffect()
        self.timebar.setGraphicsEffect(fadeTimebar)
        self.animFadeInAltitudeGraph = QPropertyAnimation(fadeTimebar, b"opacity")
        self.animFadeInAltitudeGraph.setStartValue(0)
        self.animFadeInAltitudeGraph.setEndValue(1)
        self.animFadeInAltitudeGraph.setDuration(2000)
        self.animFadeInAltitudeGraph.start()

        self.update()

    def fadeMoveOutTime(self):
        # Move out time label
        self.animMoveOutTimeLabel = QPropertyAnimation(self.timeLabel, b"geometry")
        self.animMoveOutTimeLabel.setDuration(2000)
        self.animMoveOutTimeLabel.setStartValue(QRect(0, 15, 1280, 110))
        self.animMoveOutTimeLabel.setEndValue(QRect(0, 360, 1280, 110))
        self.animMoveOutTimeLabel.start()

        # Fade out time label - issue with interferring with other effects
        # fadeOutTimeLabel = QGraphicsOpacityEffect()
        # self.timeLabel.setGraphicsEffect(fadeOutTimeLabel)
        # self.animFadeOutTimeLabel = QPropertyAnimation(fadeOutTimeLabel, b"opacity")
        # self.animFadeOutTimeLabel.setStartValue(1)
        # self.animFadeOutTimeLabel.setEndValue(0)
        # self.animFadeOutTimeLabel.setDuration(2000)
        # self.animFadeOutTimeLabel.start()

        # Fade out the timebar
        fadeTimebar = QGraphicsOpacityEffect()
        self.timebar.setGraphicsEffect(fadeTimebar)
        self.animFadeOutAltitudeGraph = QPropertyAnimation(fadeTimebar, b"opacity")
        self.animFadeOutAltitudeGraph.setStartValue(1)
        self.animFadeOutAltitudeGraph.setEndValue(0)
        self.animFadeOutAltitudeGraph.setDuration(2000)
        self.animFadeOutAltitudeGraph.start()

        self.update()

    # Altitude Mode
    def setupAltitudeLabel(self, picture: Picture):
        self.centerLabel = UILabelTopCenter(self, '', 'M')
        self.centerLabel.setPrimaryText(picture.uialtitude)

    def setupAltitudeGraphAndLine(self, picture: Picture):
        archiveSize = self.sql_controller.get_archive_size()
        idxList = self.sql_controller.chooseIndexes(int(archiveSize), 1280.0)
        altitudelist = self.sql_controller.ui_get_altitudes_for_archive_sortby('alt', idxList)

        currentAlt = picture.altitude

        altitudelist.insert(0, currentAlt)  # Append the new altitude at the start of the list
        altitudelist = sorted(altitudelist)  # Sorts so the altitude will fit within the correct spot on the graph

        self.altitudegraph = AltitudeGraphTransferQWidget(self, True, altitudelist, currentAlt)
        self.altitudegraph.setGraphicsEffect(UIEffectDropShadow())

        MINV = min(altitudelist)
        MAXV = max(altitudelist)
        H = 500
        self.linePosY = 108 + H - ( ((currentAlt - MINV)/(MAXV-MINV)) * (H-3) )
        # print(self.linePosY)

        self.line = QLabel("line", self)
        bottomImg = QPixmap("assets/line.png")
        self.line.setPixmap(bottomImg)
        self.line.setAlignment(Qt.AlignCenter)

        self.line.setGeometry(0, int(self.linePosY), 1280, 3)

    def updateAltitudeLabelAndGraph(self, picture: Picture):
        self.centerLabel.setPrimaryText(picture.uialtitude)
        self.setupAltitudeGraphAndLine(picture)

    def fadeMoveInAltitudeEverything(self):
        self.altitudegraph.show()
        self.centerLabel.show()
        self.line.show()

        # Alt Line
        self.animMoveInLine = QPropertyAnimation(self.line, b"geometry")
        self.animMoveInLine.setDuration(3000)
        self.animMoveInLine.setStartValue(QRect(0, 360, 1280, 3))
        self.animMoveInLine.setEndValue(QRect(0, self.linePosY, 1280, 3))
        self.animMoveInLine.start()

        fadeEffect = QGraphicsOpacityEffect()
        self.line.setGraphicsEffect(fadeEffect)
        self.animFadeInLine = QPropertyAnimation(fadeEffect, b"opacity")
        # self.anim2 = QPropertyAnimation(self.label, b"windowOpacity")
        self.animFadeInLine.setStartValue(0)
        self.animFadeInLine.setEndValue(1)
        self.animFadeInLine.setDuration(1500)
        self.animFadeInLine.start()

        # Move in top label
        self.animMoveInAltitudeValue = QPropertyAnimation(self.centerLabel, b"geometry")
        self.animMoveInAltitudeValue.setDuration(2000)
        self.animMoveInAltitudeValue.setStartValue(QRect(0, 360, 1280, 110))
        self.animMoveInAltitudeValue.setEndValue(QRect(0, 15, 1280, 110))
        self.animMoveInAltitudeValue.start()

        # Fade in AltitudeGraphTransferQWidget
        fadeEffect2 = QGraphicsOpacityEffect()
        self.altitudegraph.setGraphicsEffect(fadeEffect2)
        self.animFadeInAltitudeGraph = QPropertyAnimation(fadeEffect2, b"opacity")
        self.animFadeInAltitudeGraph.setStartValue(0)
        self.animFadeInAltitudeGraph.setEndValue(1)
        self.animFadeInAltitudeGraph.setDuration(2000)
        self.animFadeInAltitudeGraph.start()

        self.update()

    def fadeMoveOutAltitudeEverything(self):
        # Label
        self.animMoveOutAltitudeValue = QPropertyAnimation(self.centerLabel, b"geometry")
        self.animMoveOutAltitudeValue.setDuration(2000)
        self.animMoveOutAltitudeValue.setStartValue(QRect(0, 30, 1280, 110))
        self.animMoveOutAltitudeValue.setEndValue(QRect(0, 360, 1280, 110))
        self.animMoveOutAltitudeValue.start()

        # Fade Out - Line
        fadeOutLine = QGraphicsOpacityEffect()
        self.line.setGraphicsEffect(fadeOutLine)
        self.animFadeOutLine = QPropertyAnimation(fadeOutLine, b"opacity")
        self.animFadeOutLine.setStartValue(1)
        self.animFadeOutLine.setEndValue(0)
        self.animFadeOutLine.setDuration(2000)
        self.animFadeOutLine.start()

        # Fade Out - Graph
        fadeOutGraph = QGraphicsOpacityEffect()
        self.altitudegraph.setGraphicsEffect(fadeOutGraph)
        self.animFadeOutGraph = QPropertyAnimation(fadeOutGraph, b"opacity")
        self.animFadeOutGraph.setStartValue(1)
        self.animFadeOutGraph.setEndValue(0)
        self.animFadeOutGraph.setDuration(2000)
        self.animFadeOutGraph.start()

        self.update()

    # Color Mode
    def setupColorWidgets(self, picture: Picture):
        self.colorpalette = ColorPaletteNew(self, True, picture.colors_rgb, picture.colors_conf)
        self.colorpalette.setGraphicsEffect(UIEffectDropShadow())

        archiveSize = self.sql_controller.get_archive_size()
        idxList = self.sql_controller.chooseIndexes(int(archiveSize), 1280.0)

        colorlist = self.sql_controller.ui_get_colors_for_archive_sortby('color', idxList)
        self.colorbar = ColorBarTransfer(self, True, colorlist)

        self.hideColorWidgets()

    def updateColorWidgets(self, picture: Picture):
        self.colorpalette.trigger_refresh(True, picture.colors_rgb, picture.colors_conf)

    def showColorWidgets(self):
        self.colorpalette.show()
        self.colorbar.show()

    def hideColorWidgets(self):
        self.colorpalette.hide()
        self.colorbar.hide()

    def fadeMoveInColorWidgets(self):
        self.colorpalette.show()
        self.colorbar.show()

        # Move in ColorPalette
        self.animMoveInColor = QPropertyAnimation(self.colorpalette, b"geometry")
        self.animMoveInColor.setDuration(2000)
        self.animMoveInColor.setStartValue(QRect(0, 360, 0, 0))
        self.animMoveInColor.setEndValue(QRect(0, 15, 0, 0))
        self.animMoveInColor.start()

        # Fade in ColorBar
        fadeEffect = QGraphicsOpacityEffect()
        self.colorbar.setGraphicsEffect(fadeEffect)
        self.animFadeInColor = QPropertyAnimation(fadeEffect, b"opacity")
        self.animFadeInColor.setStartValue(0)
        self.animFadeInColor.setEndValue(1)
        self.animFadeInColor.setDuration(2000)
        self.animFadeInColor.start()

        # This will overwrite the dropshadow effect
        # fadeEffect = QGraphicsOpacityEffect()
        # self.colorpalette.setGraphicsEffect(fadeEffect)
        # self.anim2 = QPropertyAnimation(fadeEffect, b"opacity")
        # self.anim2.setStartValue(0)
        # self.anim2.setEndValue(1)
        # self.anim2.setDuration(2000)
        # self.anim2.start()

        self.update()

    def fadeMoveOutColorWidgets(self):
        # Move out ColorPalette
        self.animMoveOutColor = QPropertyAnimation(self.colorpalette, b"geometry")
        self.animMoveOutColor.setDuration(2000)
        self.animMoveOutColor.setStartValue(QRect(0, 30, 0, 0))
        self.animMoveOutColor.setEndValue(QRect(0, 360, 0, 0))
        self.animMoveOutColor.start()

        # Fade out ColorBar
        fadeEffect = QGraphicsOpacityEffect()
        self.colorbar.setGraphicsEffect(fadeEffect)
        self.animFadeOutColor = QPropertyAnimation(fadeEffect, b"opacity")
        self.animFadeOutColor.setStartValue(1)
        self.animFadeOutColor.setEndValue(0)
        self.animFadeOutColor.setDuration(2000)
        self.animFadeOutColor.start()

        self.update()

    # Keyboard Input
    def keyPressEvent(self, event):
        # Closing App
        if event.key() == Qt.Key_Escape:
            self.close()
        elif event.key() == Qt.Key_1:
            print('1')
            # self.bgcolor.changeColor(self.picture.color_rgb)
        elif event.key() == Qt.Key_2:
            print('2')
            # self.fadeMoveInColorWidgets()
        elif event.key() == Qt.Key_3:
            print('3')
            # self.fadeMoveOutColorWidgets()
        elif event.key() == Qt.Key_4:
            print('4')
            # self.fadeMoveInAltitudeEverything()
        elif event.key() == Qt.Key_5:
            print('5')
            # self.fadeMoveOutAltitudeEverything()
        elif event.key() == Qt.Key_6:
            print('6')
            # self.fadeMoveInTime()
        elif event.key() == Qt.Key_7:
            print('7')
            # self.fadeMoveOutTime()
        elif event.key() == Qt.Key_8:
            print('8')
        elif event.key() == Qt.Key_9:
            print('9')
        elif event.key() == Qt.Key_0:
            print('0')

    def closeEvent(self, event):
        print('User has clicked the red X')
        self.garbageCollection()

    def garbageCollection(self):
        self.transferThread.signals.terminate = True



class CapraWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        global CURRENT_WINDOW, capraThreadpool

        print(" // CapraWindow *** Capra Window initiated!!")
        # self.threadpoolBackground = QThreadPool()
        capraThreadpool.setMaxThreadCount(2)

        self.hallEffectThread = ReadHallEffectThread()
        capraThreadpool.start(self.hallEffectThread)

        self.pingCameraThread = PingCameraThread()
        capraThreadpool.start(self.pingCameraThread)

        createLogger()

        print("Hall-effect: {}".format(g.HALL_EFFECT))
        print("Camera: {}".format(g.CAMERA_UP))

        time.sleep(2)

        if (g.HALL_EFFECT and g.CAMERA_UP):
            print(" // CapraWindow (init) *** Camera is UP! Starting TransferWindow")
            self.window = TransferAnimationWindow()
            CURRENT_WINDOW = "Transfer"
        else:
            print(" // CapraWindow (init) *** Camera is NOT up! Starting SlideshowWindow")
            self.window = SlideshowWindow()
            CURRENT_WINDOW = "Slideshow"

        self.window.show()

        # Setup QTimer for checking the hall-effect sensor signal
        self.checkerCounter = 1
        self.timerSensorChecker = QTimer()
        self.timerSensorChecker.timeout.connect(self.hallEffectChecker)
        self.timerSensorChecker.start(1000)

    def hallEffectChecker(self):
        global CURRENT_WINDOW

        # hall-effect is ON and the camera is UP - we are ready to transfer!
        if (g.HALL_EFFECT and g.CAMERA_UP):
            if (CURRENT_WINDOW == "Slideshow"):
                print(" // CapraWindow (checker) *** Camera is now UP! Switching to TransferWindow")
                self.window.close()
                self.window = TransferAnimationWindow()
                CURRENT_WINDOW = "Transfer"
                self.window.show()
        # hall-effect is OFF - play the slideshow!
        else:
            if (CURRENT_WINDOW == "Transfer"):
                print(" // CapraWindow (checker) *** Camera is NOT up! Switching to SlideshowWindow")
                self.window.close()
                self.window = SlideshowWindow()
                CURRENT_WINDOW = "Slideshow"
                self.window.show()



if __name__ == "__main__":
    # launch transfer animation window
    app = QApplication(sys.argv)
    window = CapraWindow()
    # window.show()
    app.exec_()
