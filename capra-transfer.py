import glob     # File path pattern matching
import os
import sys
import os.path
import datetime
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
from math import sqrt
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

VERBOSE = False

GPIO.setmode(GPIO.BCM)                              # Set's GPIO pins to BCM GPIO numbering
GPIO.setup(g.HALL_EFFECT_PIN, GPIO.IN)              # Set our input pin to be an input
HALL_EFFECT_ON = threading.Event()                  # https://blog.miguelgrinberg.com/post/how-to-make-python-wait

logger = None
rsync_status = None
RETRY = 0
RETRY_MAX = 5

STOP = False

currHike = -1
globalCounter_h = 0
dummyGlobalColorRank = -1
dummyGlobalAltRank = -1
dummyGlobalCounter = 0

COLOR_HSV_INDEX = -1    # used in the sortColor helper function
NEW_DATA = False        # is there any updated data coming in?

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


#######################################################################
#####                   BACKGROUND PROCESSES                      #####
#######################################################################

class readHallEffectThread(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        # deploy this as a background process
        self.daemon = True
        self.start()

    def run(self):
        while True:
            if (GPIO.input(g.HALL_EFFECT_PIN)):
                g.HALL_EFFECT = False
            else:
                g.HALL_EFFECT = True

            if (g.HALL_EFFECT != g.PREV_HALL_VALUE):
                if (g.HALL_BOUNCE_TIMER is None):
                    print("signal change! setting the timer..")
                    g.HALL_BOUNCE_TIMER = current_milli_time()

                if (current_milli_time() - g.HALL_BOUNCE_TIMER > g.HALL_BOUNCE_LIMIT):
                    print("the signal is valid!")
                    if (g.HALL_EFFECT):
                        print("\tFalse -> True")
                        g.PREV_HALL_VALUE = True
                        HALL_EFFECT_ON.set()
                        g.flag_start_transfer = True
                    else:
                        print("\tTrue -> False")
                        g.PREV_HALL_VALUE = False
                        HALL_EFFECT_ON.clear()
                        g.flag_start_transfer = False

            elif (g.HALL_BOUNCE_TIMER is not None):
                print("signal change is lost. resetting the timer")
                g.HALL_BOUNCE_TIMER = None


# https://stackoverflow.com/questions/28769023/get-output-of-system-ping-without-printing-to-the-console
def isCameraUp():
    is_up = False
    with open(os.devnull, 'w') as DEVNULL:
        try:
            subprocess.check_call(
                ['ping', '-c', '3', g.IP_ADDR_CAMERA],
                stdout=DEVNULL,  # suppress output
                stderr=DEVNULL
            )
            is_up = True
        except subprocess.CalledProcessError:
            is_up = False
    return is_up


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

def updateDB():
    proc = subprocess.Popen(["sqldiff", CAMERA_DB, CAMERA_BAK_DB], stdout=subprocess.PIPE)
    line = proc.stdout.readline()
    if line != b'':
        # there are new incoming changes in DB
        print("## Updated DB detected. Starting the transfer process...")
        return True
    else:
        # two databases are identical
        print("## DB is still fresh.")
        return False


def copy_remote_db():
    if (exists_remote(CAMERA_DB_REMOTE)):
        print("@@ Found the remote DB!")
        subprocess.Popen(['rsync', '--inplace', '-avAI', '--no-perms', '--rsh="ssh"', "pi@" + g.IP_ADDR_CAMERA + ":" + CAMERA_DB_REMOTE, DATAPATH], stdout=subprocess.PIPE)
    else:
        print("@@ Did NOT locate the remote DB! :\\")

    time.sleep(1)
    return


def copy_master_db():
    subprocess.Popen(['cp', PROJECTOR_DB, PROJECTOR_BAK_DB], stdout=subprocess.PIPE)
    return


def make_backup_remote_db():
    subprocess.Popen(['cp', CAMERA_DB, CAMERA_BAK_DB], stdout=subprocess.PIPE)
    return


# 1. make db connections
def getDBControllers():
    global dbSRCController, dbDESTController

    # this is a locally saved db, copied from camera
    dbSRCController = SQLController(database=CAMERA_DB)

    # TODO: if dest does not exist, create a new DB by copying and renaming the skeleton file
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
    return subprocess.call(['ssh', 'pi@' + g.IP_ADDR_CAMERA, 'test -e ' + pipes.quote(path)]) == 0


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
    return hikeColor is not None and hikeColor and not (hikeColor[0] < 0.001 and hikeColor[1] < 0.001 and hikeColor[2] < 0.001)


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
    lum = sqrt(0.241 * r + 0.691 * g + 0.068 * b)
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


#######################################################################
#####                   MAJOR WRAPPER FUNCTIONS                   #####
#######################################################################

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

    commit = [round(row_src['time'], 0),
                picDatetime.year, picDatetime.month, picDatetime.day, picDatetime.hour * 60 + picDatetime.minute, picDatetime.weekday(),
                currHike, validRowCount, dummyGlobalCounter,
                round(row_src['altitude'], 2), -1, -1, dummyGlobalCounter,
                ",".join(map(str, colors_hsv[0])), ",".join(map(str, colors_rgb[0])), -1, -1, -1, dummyGlobalCounter,
                color_size, formatColors(colors_rgb), ",".join(map(str, confidences)),
                camera1, camera2, camera3, camera2f, row_src['created_date_time']]

    return commit, colors_hsv[0]


def filterZeroBytePicturesFromSrc():
    global dbSRCController

    print("[{}] Checking 0 byte pictures in the source directory before start transferring..".format(timenow()))

    latest_src_hikeID = dbSRCController.get_last_hike_id()
    latest_dest_hikeID = dbDESTController.get_last_hike_id()
    print("[{}] ## hikes from Source: {}".format(timenow(), str(latest_src_hikeID)))
    print("[{}] ## hikes at Dest: {}".format(timenow(), str(latest_dest_hikeID)))

    currHike = 1
    delCount = 0

    while currHike <= latest_src_hikeID:
        print("[{}] ### Checking hike {}".format(timenow(), currHike))
        srcPath = build_hike_path(CAMERAPATH_REMOTE, currHike)

        totalCountHike = dbSRCController.get_pictures_count_of_selected_hike(currHike)
        print("[{}] ### Hike {} originally has {} rows".format(timenow(), currHike, totalCountHike))

        if (not os.path.isdir(srcPath)):
            currHike += 1
            continue

        allRows = dbSRCController.get_pictures_of_selected_hike(currHike)

        for row in allRows:
            picPathCam1_src = srcPath + "{}_cam1.jpg".format(row['index_in_hike'])
            picPathCam2_src = srcPath + "{}_cam2.jpg".format(row['index_in_hike'])
            picPathCam3_src = srcPath + "{}_cam3.jpg".format(row['index_in_hike'])

            ### !! Potential bottle-neck - making 6 calls for a single condition check
            if (exists_remote(picPathCam1_src) and not exists_non_zero_remote(picPathCam1_src) or
                exists_remote(picPathCam2_src) and not exists_non_zero_remote(picPathCam2_src) or
                exists_remote(picPathCam3_src) and not exists_non_zero_remote(picPathCam3_src)):

                print("[{}] \t Row {} has an empty picture. Deleting a row..".format(timenow(), row['index_in_hike']))

                dbSRCController.delete_picture_of_given_timestamp(row['time'], True) # delay commit to prevent concurrency issues
                delCount += 1

        totalCountHike = dbSRCController.get_pictures_count_of_selected_hike(currHike)

        if (delCount > 0):
            print("[{}] {} rows deleted".format(timenow(), delCount))
            print("[{}] Hike {} now has {} rows".format(timenow(), currHike, totalCountHike))

            dbSRCController.update_hikes_total_picture_count_of_given_hike(totalCountHike, currHike, True)

        # commit changes only when a given hike is fully scanned
        dbSRCController.connection.commit()
        currHike += 1


## this is essentially the main function
def buildHike(currHike):
    global dbSRCController, dbDESTController
    global srcPath, destPath
    global dummyGlobalColorRank, dummyGlobalAltRank, dummyGlobalCounter, globalCounter_h

    global rsync_status, hall_effect
    global logger
    global threads, threadPool, STOP

    avgAlt = 0
    startTime = 9999999999
    endTime = -1
    domColorsHike_hsv = []
    pics = {}
    commits = {}
    threads = []
    threadPool = ThreadPoolExecutor(max_workers=5)

    validRowCount = 0           ### This is the 'corrected' numValidRows (may 14)
    index_in_hike = 0
    validRows = dbSRCController.get_valid_photos_in_given_hike(currHike)
    numValidRows = len(validRows)
    maxRows = dbSRCController.get_last_photo_index_of_hike(currHike)

    print("[{}] Last index in Hike {}: {}".format(timenow(), str(currHike), str(maxRows)))
    print("[{}] Expected valid row count: {}".format(timenow(), str(numValidRows)))

    while (index_in_hike <= maxRows + 2):   # allow a loose upper bound (max + 2) to handle the last index

        # # check the connection before processing a new row
        # if (not g.HALL_EFFECT):
        #     print("[{}]     HALL-EFFECT SIGNAL LOST !! Terminating transfer process..".format(timenow()))
        #     logger.info("[{}]     HALL-EFFECT SIGNAL LOST !! Terminating transfer process..".format(timenow()))
        #     return
        # if (not isCameraUp()):
        #     print("[{}]     CAMERA SIGNAL LOST !! Please check the connection and retry. Terminating transfer process..".format(timenow()))
        #     logger.info("[{}]     CAMERA SIGNAL LOST !! Please check the connection and retry. Terminating transfer process..".format(timenow()))
        #     return

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

        # TODO: if pictures exist on the Projector but no row data in the destDB, skip transfer but extract the data from the srcDB

        if (not exists_remote(picPathCam1_src) or not exists_remote(picPathCam2_src)):
            index_in_hike += 1
            continue

        if (index_in_hike <= maxRows and index_in_hike % 200 == 0):
            print("[{}] ### Checkpoint at {}".format(timenow(), str(index_in_hike)))


        isNew = False
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

            isNew = True
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


        # update timestamps
        if (row_src['time'] < startTime):
            startTime = row_src['time']
        if (row_src['time'] > endTime):
            endTime = row_src['time']

        avgAlt += int(row_src['altitude'])

        # rotate and resize, copy those to the dest folder
        img = None
        img_res = None
        # resize and rotate for newly added pictures
        #    1. make a copy of pic2 as pic2'f'
        if (not os.path.exists(picPathCam2f_dest)):
            img = Image.open(picPathCam2_dest)
            img_res = img.copy()
            img_res.save(picPathCam2f_dest)

        #    2. resize to 427x720 and rotate 90 deg
        try:
            if (not os.path.exists(picPathCam1_dest) or
                not os.path.exists(picPathCam2_dest) or
                not os.path.exists(picPathCam2f_dest) or
                not os.path.exists(picPathCam3_dest)):

                img = Image.open(picPathCam1_src)
                img_res = img.resize((720, 427), Image.ANTIALIAS).rotate(270, expand=True)
                img_res.save(picPathCam1_dest)

                img = Image.open(picPathCam2_src)
                img_res = img.resize((720, 427), Image.ANTIALIAS).rotate(270, expand=True)
                img_res.save(picPathCam2_dest)

                if (os.path.exists(picPathCam3_src)):
                    img = Image.open(picPathCam3_src)
                    img_res = img.resize((720, 427), Image.ANTIALIAS).rotate(270, expand=True)
                    img_res.save(picPathCam3_dest)
                else:
                    img = Image.open(WHITE_IMAGE)
                    img_res = img.copy().rotate(90, expand=True)
                    img_res.save(picPathCam3_dest)
        except:
            print("!! Hike {} @ row {} has truncated pictures. Skipping a row..".format(currHike, index_in_hike))
            index_in_hike += 1
            continue

        # increment the validRowCounter since we have successfully trasferred the pictures for this row
        validRowCount += 1

        if (not os.path.exists(picPathCam3_src)):
            picPathCam3_dest = None

        threads.append(threadPool.submit(dominantColorWrapper, currHike, validRowCount, row_src, picPathCam1_dest, picPathCam2_dest, picPathCam3_dest, (DIMX, DIMY)))

        dummyGlobalCounter += 1
        index_in_hike += 1

    # wait for threads to finish
    for thread in futures.as_completed(threads):
        commit, domCol_hsv = thread.result()
        domColorsHike_hsv.append(domCol_hsv)
        fileName = "{}_camN".format(commit[7])
        commits[fileName] = commit
    threadPool.shutdown(wait=True)

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

    # create a color spectrum for this hike
    colorSpectrumRGB_hike = dbDESTController.get_pictures_rgb_hike(currHike)
    generatePics(colorSpectrumRGB_hike, "hike{}".format(currHike) + "-colorSpectrum", destPath)

    print("[{}] ## Hike {} done. {} rows processed".format(timenow(), currHike, validRowCount))


def start_transfer():
    global dbSRCController, dbDESTController, dummyGlobalColorRank, dummyGlobalAltRank, dummyGlobalCounter, globalCounter_h
    global srcPath, destPath
    global COLOR_HSV_INDEX

    global rsync_status, hall_effect
    global logger
    global threads, threadPool, STOP

    # filter out zero byte pictures in the source DB upon starting
    filterZeroBytePicturesFromSrc()

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

    dummyGlobalCounter = 1
    masterTimer = time.time()

    # 3. determine how many hikes should be transferred
    while currHike <= latest_remote_hikeID:

        # if (not g.HALL_EFFECT):
        #     print("[{}]     HALL-EFFECT SIGNAL LOST !! Terminating transfer process..".format(timenow()))
        #     logger.info("[{}]     HALL-EFFECT SIGNAL LOST !! Terminating transfer process..".format(timenow()))
        #     return
        # if (not isCameraUp()):
        #     print("[{}]     CAMERA SIGNAL LOST !! Please check the connection and retry. Terminating transfer process..".format(timenow()))
        #     logger.info("[{}]     CAMERA SIGNAL LOST !! Please check the connection and retry. Terminating transfer process..".format(timenow()))
        #     return

        ### TODO: update constants
        srcPath = build_hike_path(CAMERAPATH_REMOTE, currHike)
        currExpectedHikeSize = dbSRCController.get_size_of_hike(currHike)

        if (currExpectedHikeSize is None):
            currExpectedHikeSize = 0

        # 1. skip empty hikes
        #       + also skip small hikes (< 20) [Jul 8, 2021]
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
            NEW_DATA = True
            hikeTimer = time.time()

            destPath = build_hike_path(DATAPATH, currHike, True)
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
                logger.info("[{}]     # Hike {} fully transferred. Proceeding to the next hike...".format(timenow(), str(currHike)))
                dummyGlobalCounter += currExpectedHikeSize

            else:
                hikeTimer = time.time()
                print("[{}] Processing Hike {}".format(timenow(), str(currHike)))
                buildHike(currHike)
                print("[{}] --- Hike {} took {} seconds".format(timenow(), str(currHike), str(time.time() - hikeTimer)))

            currHike += 1
            globalCounter_h += currExpectedHikeSize


    ### At this point, all hikes are processed.

    ### TODO: remove TRUE for the final code
    # calculate global ranks for pictures, only when there is new data
    if (True or NEW_DATA):
        rankTimer = time.time()

        globalTimeList = []
        globalAltList = []
        globalColorList = []
        # key function for sort() only accepts 1 argument, so need to explicitly set additional variable as global
        COLOR_HSV_INDEX = 1

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

        # create color spectrum for globalColor and globalColor_h
        colorSpectrumRGB_Global = dbDESTController.get_pictures_rgb_global()
        generatePics(colorSpectrumRGB_Global, "hike-global-colorSpectrum", DATAPATH)

        colorSpectrumRGB_Global_h = dbDESTController.get_pictures_rgb_global_h()
        generatePics(colorSpectrumRGB_Global_h, "hike-global-h-colorSpectrum", DATAPATH)

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

        NEW_DATA = False

    print("[{}] --- Global ranking took {} seconds".format(timenow(), str(time.time() - rankTimer)))
    print("[{}] --- Building the projector DB took {} seconds ---".format(timenow(), str(time.time() - masterTimer)))

    STOP = True


# ==================================================================

def main():
    global STOP, RETRY

    # readHallEffectThread()

    while True:
        # HALL_EFFECT_ON.wait()
        createLogger()
        start_time = time.time()
        try:
            if (isCameraUp()):
                # # if camera DB is still fresh, do not run transfer script
                # if (os.path.exists(CAMERA_DB) and
                    # os.path.exists(CAMERA_BAK_DB) and
                    # not updateDB()):
                #     g.flag_start_transfer = False
                #     HALL_EFFECT_ON.clear()
                #     continue

                if (os.path.exists(CAMERA_DB) and
                    os.path.exists(CAMERA_BAK_DB) and
                    not updateDB()):
                    print("@@ DB is still fresh!")
                else:
                    print("@@ DB needs to be synced!")

                print("[{}] Copying the camera DB over to the Projector..".format(timenow()))
                copy_remote_db()

                # copy the current snapshot of master DB for checking references
                print("[{}] Making a copy of the master DB on the Projector..".format(timenow()))
                copy_master_db()

                print("[{}] Creating DB controllers..".format(timenow()))
                getDBControllers()

                start_transfer()
                print("[{}] --- {} seconds ---".format(timenow(), str(time.time() - start_time)))
                logger.info("[{}] --- {} seconds ---".format(timenow(), str(time.time() - start_time)))

                # if transfer is successfully finished pause running until camera is dismounted and re-mounted
                print("## Transfer finished. Pause the script")
                # g.flag_start_transfer = False
                # HALL_EFFECT_ON.clear()
                make_backup_remote_db()

            else:
                print("[{}]     CAMERA SIGNAL LOST !! Please check the connection and retry. Terminating transfer process..".format(timenow()))
                logger.info("[{}]     CAMERA SIGNAL LOST !! Please check the connection and retry. Terminating transfer process..".format(timenow()))

            if (STOP):
                break;

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


if __name__ == "__main__":
    main()
