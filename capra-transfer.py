import globals as g
import glob                                         # File path pattern matching
import os
import sys
import os.path
import datetime
import threading
from concurrent import futures
from concurrent.futures import ThreadPoolExecutor
import time
import sqlite3                                      # Database Library
import subprocess                                   # Deploy RSyncs
import traceback
import RPi.GPIO as GPIO
from PIL import ImageTk, Image                      # Pillow image functions
from pathlib import Path
from classes.capra_data_types import Picture, Hike
from classes.sql_controller import SQLController
from classes.sql_statements import SQLStatements
from classes.kmeans import get_dominant_colors_for_picture
from classes.kmeans import get_dominant_color_1D
from classes.kmeans import hsvToRgb
import logging
g.init()

VERBOSE = False

GPIO.setmode(GPIO.BCM)                              # Set's GPIO pins to BCM GPIO numbering
GPIO.setup(g.HALL_EFFECT_PIN, GPIO.IN)              # Set our input pin to be an input
HALL_EFFECT_ON = threading.Event()                  # https://blog.miguelgrinberg.com/post/how-to-make-python-wait

logger = None
rsync_status = None
retry = 0
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
CAPRAPATH = g.CAPRAPATH_PROJECTOR
DATAPATH = g.DATAPATH_PROJECTOR
CAMERA_DB = DATAPATH + g.DBNAME_CAMERA
CAMERA_BAK_DB = DATAPATH + g.DBNAME_CAMERA_BAK
PROJECTOR_DB = DATAPATH + g.DBNAME_MASTER
PROJECTOR_BAK_DB = DATAPATH + g.DBNAME_MASTER_BAK
WHITE_IMAGE = DATAPATH + "white.jpg"

### TODO: move constant variables to globals.py

WHITE_IMAGE = DROPBOX + BASEPATH_DEST + "white.jpg"

DROPBOX = "/Users/myoo/Dropbox/"
BASEPATH_SRC = None
BASEPATH_DEST = None
src_db_name = None
dest_db_name = None

DBTYPE = 'projector'   # 'camera' or 'projector'
ROWINDEX_TIMESTAMP = None
ROWINDEX_ALTITUDE = None
ROWINDEX_INDEX_IN_HIKE = None
ROWINDEX_CAMERA1 = None
ROWINDEX_CAMERA2 = None
ROWINDEX_CAMERA3 = None

if (DBTYPE == 'projector'):
    # BASEPATH_SRC = "Everyday Design Studio/A Projects/100 Ongoing/Capra/capra-storage/capra-storage-july/"
    # src_db_name = "capra_projector_jan2021_min_AllHikes.db"

    BASEPATH_SRC = "Everyday Design Studio/A Projects/100 Ongoing/Capra/capra-storage/capra-storage-jordan2_test/"
    src_db_name = "capra_projector_jun2021_min_test2.db"

    BASEPATH_DEST = "Everyday Design Studio/A Projects/100 Ongoing/Capra/capra-storage/capra-storage-min-transfer_full/"
    dest_db_name = "capra_projector_jun2021_min_full.db"

    # BASEPATH_SRC = "Everyday Design Studio/A Projects/100 Ongoing/Capra/capra-storage/capra-storage-min-transfer/"
    # src_db_name = "capra_projector_apr2021_min_camera_full_merge.db"
    # BASEPATH_DEST = "Everyday Design Studio/A Projects/100 Ongoing/Capra/capra-storage/capra-storage-min-transfer/"
    # dest_db_name = "capra_projector_apr2021_min_test_full_merged.db"

    ROWINDEX_TIMESTAMP = 1
    ROWINDEX_ALTITUDE = 9
    ROWINDEX_INDEX_IN_HIKE = 8
    ROWINDEX_CAMERA1 = 22

else:
    # BASEPATH_SRC = "Everyday Design Studio/A Projects/100 Ongoing/Capra/capra-storage/capra-storage-jordan2/"
    # src_db_name = "capra_camera.db"
    #
    # BASEPATH_DEST = "Everyday Design Studio/A Projects/100 Ongoing/Capra/capra-storage/capra-storage-min-transfer-2/"
    # dest_db_name = "capra_projector_apr2021_min_camera_full.db"

    BASEPATH_SRC = "Everyday Design Studio/A Projects/100 Ongoing/Capra/capra-storage/capra-storage-jordan2_test/"
    src_db_name = "capra_camera.db"

    BASEPATH_DEST = "Everyday Design Studio/A Projects/100 Ongoing/Capra/capra-storage/capra-storage-jordan2_test/"
    dest_db_name = "capra_projector_jun2021_min_test.db"


    ROWINDEX_TIMESTAMP = 0
    ROWINDEX_ALTITUDE = 1
    ROWINDEX_INDEX_IN_HIKE = 3
    ROWINDEX_CAMERA1 = 4

ROWINDEX_CAMERA2 = ROWINDEX_CAMERA1 + 1
ROWINDEX_CAMERA3 = ROWINDEX_CAMERA1 + 2

CLUSTERS = 5        # assumes X number of dominant colors in a pictures
REPETITION = 8

srcPath = ""
destPath = ""
SRCDBPATH = DROPBOX + BASEPATH_SRC + src_db_name
DESTDBPATH = DROPBOX + BASEPATH_DEST + dest_db_name

dbSRCController = None
dbDESTController = None

FILENAME = "[!\.]*_cam[1-3].jpg"
FILENAME_FULLSIZE = "[!\.]*_cam2f.jpg"
# sample dimensions: (100, 60), (160, 95), (320, 189), (720, 427)
DIMX = 100
DIMY = 60
TOTAL = DIMX * DIMY

res_red = []
res_green = []
res_blue = []

# ??
domColors = []
cDBController = None
pDBController = None
p2DBController = None
checkSum_transferred = 0
checkSum_rotated = 0
checkSum_total = 0


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


def timenow():
    return str(datetime.datetime.now()).split('.')[0]


def current_milli_time():
    return int(round(time.time() * 1000))


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
    subprocess.Popen(['rsync', '--inplace', '-avAI', '--no-perms', '--rsh="ssh"', "pi@" + g.IP_ADDR_CAMERA + ":/media/pi/capra-hd/capra_camera_test.db", "/media/pi/capra-hd/"], stdout=subprocess.PIPE)
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
    global cDBController, pDBController, p2DBController

    # this will be a local db, copied from camera
    cDBController = SQLController(database=CAMERA_DB)
    # master projector db
    pDBController = SQLController(database=PROJECTOR_DB)
    # a copy of aster projector db
    p2DBController = SQLController(database=PROJECTOR_BAK_DB)

def count_files_in_directory(path, pattern):
    if (not os.path.exists(path)):
        return 0
    else:
        return len(glob.glob(path + pattern))


def build_hike_path(hikeID, makeNew=False):
    res = DATAPATH + 'hike' + str(hikeID) + '/'
    if makeNew and not os.path.exists(res):
        os.makedirs(res, mode=0o755)
    return res


def build_picture_path(hikeID, index, camNum, rotated=False):
    insert = ""
    if (rotated):
        insert = "f"
    return build_hike_path(hikeID) + str(index) + '_cam' + str(camNum) + insert + '.jpg'


def compute_checksum(currHike):
    global checkSum_total, checkSum_rotated, checkSum_transferred
    checkSum_transferred = count_files_in_directory(build_hike_path(currHike), g.FILENAME)
    checkSum_rotated = count_files_in_directory(build_hike_path(currHike), g.FILENAME_FULLSIZE)
    checkSum_total = checkSum_transferred + checkSum_rotated


def check_hike_postprocessing(currHike):
    hikeColor = pDBController.get_hike_average_color(currHike)
    return hikeColor is not None and hikeColor and not (hikeColor[0] < 0.001 and hikeColor[1] < 0.001 and hikeColor[2] < 0.001)


def roundToHundredth(lst):
    for i in range(len(lst)):
        lst[i] = round(float(lst[i]), 2)
    return lst


def dominant_color_wrapper(currHike, row, colrankHikeCounter, colrankGlobalCounter):
    index_in_hike = row[3]
    picPathCam1 = build_picture_path(currHike, index_in_hike, 1)
    picPathCam2 = build_picture_path(currHike, index_in_hike, 2)
    picPathCam2f = build_picture_path(currHike, index_in_hike, 2, True)
    picPathCam3 = build_picture_path(currHike, index_in_hike, 3)
    colorR = None
    colorG = None
    colorB = None
    colors_hsv_str = ""
    colors_rgb_str = ""
    domColor_hsv_str = ""
    domColor_rgb_str = ""
    conf_str = ""

#    print("{}: {}".format(index_in_hike, row))

    # TODO: perform duplicate check on
    if (pDBController.get_picture_at_timestamp(row[0]) > 0):
        color_hsv = pDBController.get_picture_dominant_color(row[0], 'hsv')
        color_rgb = pDBController.get_picture_dominant_color(row[0], 'rgb')
        # TODO: get 'colors' and check this value as well

    try:
        # round color values to the nearest hundredth
        # TODO: fix the color processing function
        if (color_hsv is None or color_rgb is None):
            color_size, colors_hsv, colors_rgb, confidences = get_multiple_dominant_colors(picPathCam1, picPathCam2, picPathCam3)
            # color_resCode, color_res1 = get_dominant_colors_for_picture(picPathCam1)

            for i in range(color_size):
                add = ","
                if (i == color_size-1):
                    add = ""
                colors_hsv_str += str(colors_hsv[i][0]) + "," + str(colors_hsv[i][1]) + "," + str(colors_hsv[i][2]) + add
                colors_rgb_str += str(colors_rgb[i][0]) + "," + str(colors_rgb[i][1]) + "," + str(colors_rgb[i][2]) + add
                conf_str += str(conf_list[i]) + add

    # TODO: check if invalid files are handled correctly
    # TODO: how do we redo failed rows?
    except:
        print("[{}]     Exception at Hike {}, row {} while extracting dominant color".format(timenow(), currHike, str(row[3])))
        print(traceback.format_exc())
        logger.info("[{}]     Exception at Hike {}, row {} while extracting dominant color".format(timenow(), currHike, str(row[3])))
        logger.info(traceback.format_exc())

    picDatetime = datetime.datetime.fromtimestamp(row[0])

    if (colrankHikeCounter % 100 == 0):
        print("[{}]\t## Hike {} checkpoint at {}".format(timenow(), currHike, colrankHikeCounter))
        logger.info("[{}]\t## Hike {} checkpoint at {}".format(timenow(), currHike, colrankHikeCounter))

    domColor_hsv_str = "{},{},{}".format(colors_hsv[0][0], colors_hsv[0][1], colors_hsv[0][2])
    domColor_rgb_str = "{},{},{}".format(colors_rgb[0][0], colors_rgb[0][1], colors_rgb[0][2])

    #     time,
    #     year, month, day, minute, dayofweek,
    #     hike, index_in_hike, altitude, altrank_hike, altrank_global,      # TODO: implement altitude rank
    #     color_hsv, color_rgb, colrank_value, colrank_hike, colrank_global,
    #     colors_count, colors_rgb, colors_conf,
    #     camera1, camera2, camera3, camera_landscape

    # ** 0 is monday in dayofweek
    # ** camera_landscape points to the path to cam2 pic
    commit = (row[0],
                picDatetime.year, picDatetime.month, picDatetime.day, picDatetime.hour * 60 + picDatetime.minute, picDatetime.weekday(),
                currHike, index_in_hike, row[1], colrankHikeCounter, colrankGlobalCounter,
                domColor_hsv_str, domColor_rgb_str, -1, colrankHikeCounter, colrankGlobalCounter,
                color_size, colors_hsv_str, colors_rgb_str,
                picPathCam1, picPathCam2, picPathCam3, picPathCam2f)

    # *** Could create a secondary DB to save transactions if Capra fails too often during transfer

    # TODO: pass information needed for the transfer animation as a JSON file

    return [colors_hsv[0][0], colors_hsv[0][1], colors_hsv[0][2]], commit


def start_transfer():
    global cDBController, pDBController, p2DBController, rsync_status, retry, hall_effect
    global checkSum_transferred, checkSum_rotated, checkSum_total, colrankHikeCounter, colrankGlobalCounter
    global logger
    global domColors, commits, threads, threadPool, STOP

    latest_master_hikeID = pDBController.get_last_hike_id()
    latest_remote_hikeID = cDBController.get_last_hike_id()
    print("[{}] @@@ # hikes on Projector: {}".format(timenow(), str(latest_master_hikeID)))
    print("[{}] @@@ # hikes on Camera: {}".format(timenow(), str(latest_remote_hikeID)))
    logger.info("[{}] @@@ # hikes on Projector: {}".format(timenow(), str(latest_master_hikeID)))
    logger.info("[{}] @@@ # hikes on Camera: {}".format(timenow(), str(latest_remote_hikeID)))

    currHike = 1
    checkSum = 0

    colrankGlobalCounter = 0

    # 3. determine how many hikes should be transferred
    while currHike <= latest_remote_hikeID:

        if (currHike < 9):
            currHike += 1
            continue
        elif (currHike > 9):
            exit()

        if (not g.HALL_EFFECT):
            print("[{}]     HALL-EFFECT SIGNAL LOST !! Terminating transfer process..".format(timenow()))
            logger.info("[{}]     HALL-EFFECT SIGNAL LOST !! Terminating transfer process..".format(timenow()))
            return
        if (not isCameraUp()):
            print("[{}]     CAMERA SIGNAL LOST !! Please check the connection and retry. Terminating transfer process..".format(timenow()))
            logger.info("[{}]     CAMERA SIGNAL LOST !! Please check the connection and retry. Terminating transfer process..".format(timenow()))
            return

        currExpectedHikeSize = cDBController.get_size_of_hike(currHike)
        if (currExpectedHikeSize is None):
            currExpectedHikeSize = 0
        expectedCheckSumTotal = currExpectedHikeSize * 4

        colrankHikeCounter = 0

        # 1. skip empty hikes
        if (currExpectedHikeSize == 0):
            print("[{}] Hike {} is empty. Proceeding to the next hike...".format(timenow(), str(currHike)))
            logger.info("[{}] Hike {} is empty. Proceeding to the next hike...".format(timenow(), str(currHike)))
            currHike += 1
            continue

        compute_checksum(currHike)
        print("[{}] Hike {}: Total {} rows -- {} out of {} photos transferred".format(timenow(), str(currHike), str(currExpectedHikeSize), str(checkSum_transferred), str(currExpectedHikeSize * 3)))
        print("[{}] Hike {}: Total {} photos expected, found {} photos".format(timenow(), str(currHike), str(expectedCheckSumTotal), str(checkSum_total)))
        logger.info("[{}] Hike {}: Total {} rows -- {} out of {} photos transferred".format(timenow(), str(currHike), str(currExpectedHikeSize), str(checkSum_transferred), str(currExpectedHikeSize * 3)))
        logger.info("[{}] Hike {}: Total {} photos expected, found {} photos".format(timenow(), str(currHike), str(expectedCheckSumTotal), str(checkSum_total)))

        # 2. if a hike is fully transferred, resized and rotated, then skip the transfer for this hike
        # also check if DB is updated to post-processed values as well
        if (currExpectedHikeSize != 0 and checkSum_transferred == currExpectedHikeSize * 3 and expectedCheckSumTotal == checkSum_total and check_hike_postprocessing(currHike)):
            print("[{}]     # Hike {} fully transferred. Proceeding to the next hike...".format(timenow(), str(currHike)))
            logger.info("[{}]     # Hike {} fully transferred. Proceeding to the next hike...".format(timenow(), str(currHike)))
            currHike += 1
            continue

        # validity check
        #   ** For photos with invalid data, we won't bother restoring/fixing incorrect metatdata.
        #      The row (all 3 photos) will be dropped as a whole
        validRows = cDBController.get_valid_photos_in_given_hike(currHike)      ### TODO
        numValidRows = len(validRows)
        checkSum_transfer_and_rotated = 4 * numValidRows
        dest = build_hike_path(currHike, True)
        hikeTimer = time.time()

        # completed hikes will have:
        #   i) 4 * hikesize (cam 1 + 2 + 3 + rotated pics)
        #   ii) valid color value of dominant color for each corresponding row in the hike table
        if (True or checkSum_total < currExpectedHikeSize * 4 or not check_hike_postprocessing(currHike)):
            # 3. transfer is not complete - still need to copy more pictures
            if (True or checkSum_transferred < currExpectedHikeSize * 3 or not check_hike_postprocessing(currHike)):

                print("[{}]   Resume transfer on Hike {}: {} out of {} files".format(timenow(), currHike, checkSum_transferred, str(currExpectedHikeSize * 3)))
                logger.info("[{}]   Resume transfer on Hike {}: {} out of {} files".format(timenow(), currHike, checkSum_transferred, str(currExpectedHikeSize * 3)))

                avgAlt = 0
                startTime = 9999999999
                endTime = -1

                # for colors
                domColorsHike_hsv_hsv = []

                threads = []
                threadPool = ThreadPoolExecutor(max_workers=5)
                commits = []

                i = 0
                # for row in validRows:
                while(i < numValidRows):
                    # row:
                    #   (time, alt, hike, index, cam1, cam2, cam3, date_created, date_updated)
                    row = validRows[i]

                    if (not g.HALL_EFFECT):
                        print("[{}]     HALL-EFFECT SIGNAL LOST !! Terminating transfer process..".format(timenow()))
                        logger.info("[{}]     HALL-EFFECT SIGNAL LOST !! Terminating transfer process..".format(timenow()))
                        return
                    if (not isCameraUp()):
                        print("[{}]     CAMERA SIGNAL LOST !! Please check the connection and retry. Terminating transfer process..".format(timenow()))
                        logger.info("[{}]     CAMERA SIGNAL LOST !! Please check the connection and retry. Terminating transfer process..".format(timenow()))
                        return
                    colrankHikeCounter += 1
                    colrankGlobalCounter += 1


                    # update timestamps
                    if (row[0] < startTime):
                        startTime = row[0]
                    if (row[0] > endTime):
                        endTime = row[0]

                    avgAlt += int(row[1])

                    # "/home/pi/capra-storage/hike1/1_cam2.jpg"
                    #   --> "/home/pi/capra-storage/hike1/1_cam*"
                    src = row[4][:-5] + '*'
                    index_in_hike = row[3]
                    picPathCam1 = build_picture_path(currHike, index_in_hike, 1)
                    picPathCam2 = build_picture_path(currHike, index_in_hike, 2)
                    picPathCam2f = build_picture_path(currHike, index_in_hike, 2, True)
                    picPathCam3 = build_picture_path(currHike, index_in_hike, 3)
                    isNew = False

                    # transfer pictures only when the paths do not exist on the projector
                    if (not os.path.exists(picPathCam1)
                        or not os.path.exists(picPathCam2)
                        or not os.path.exists(picPathCam3)):

                        # remove partially transferred files
                        if (os.path.exists(picPathCam1)
                            or os.path.exists(picPathCam2)
                            or os.path.exists(picPathCam3)):

                            tmpPath = picPathCam1[:-5]
                            for tmpfile in glob.glob(tmpPath + '*'):
                                os.remove(tmpfile)

                        isNew = True
                        # '--remove-source-files',
                        rsync_status = subprocess.Popen(['rsync', '--ignore-existing', '-avA', '--no-perms', '--rsh="ssh"', 'pi@' + g.IP_ADDR_CAMERA + ':' + src, dest], stdout=subprocess.PIPE)
                        rsync_status.wait()

                        # report if rsync is failed
                        if (rsync_status.returncode != 0):
                            print("[{}] ### Rsync failed at row {}".format(timenow(), str(index_in_hike - 1)))
                            logger.info("[{}] ### Rsync failed at row {}".format(timenow(), str(index_in_hike - 1)))

                    img = None
                    img_res = None
                    # resize and rotate for newly added pictures
                    #    1. make a copy of pic2 as pic2'f'
                    if (not os.path.exists(picPathCam2f)):
                        img = Image.open(picPathCam2)
                        img_res = img.copy()
                        img_res.save(picPathCam2f)

                    #    2. resize to 427x720 and rotate 90 deg
                    if (isNew):
                        img = Image.open(picPathCam1)
                        img_res = img.resize((720, 427), Image.ANTIALIAS).rotate(90, expand=True)
                        img_res.save(picPathCam1)

                        img = Image.open(picPathCam2)
                        img_res = img.resize((720, 427), Image.ANTIALIAS).rotate(90, expand=True)
                        img_res.save(picPathCam2)

                        if (os.path.exists(picPathCam3)):
                            img = Image.open(picPathCam3)
                            img_res = img.resize((720, 427), Image.ANTIALIAS).rotate(90, expand=True)
                            img_res.save(picPathCam3)
                        else:
                            img = Image.open(BLACK_IMAGE)
                            img_res = img.copy().rotate(90, expand=True)
                            img_res.save(picPathCam3)

                    # concurrently extract the dominant color
                    #    1. calculate dominant HSV/RGB colors
                    #    2. update path to each picture for camera 1, 2, 3
                    threads.append(threadPool.submit(dominant_color_wrapper, currHike, row, colrankHikeCounter, colrankGlobalCounter))

                    i += 1

                # wait for threads to finish
                for thread in futures.as_completed(threads):
                    color_hsv, commit = thread.result()
                    domColorsHike_hsv.append(color_hsv)
                    commits.append(commit)
                threadPool.shutdown(wait=True)

                # commit changes
                #  ** sqlite does not support concurrent write options
                print(".. Pictures for hike {} start committing..".format(currHike))
                for commit in commits:
                    pDBController.upsert_picture(*commit)

                # make a row for the hike table with postprocessed values
                compute_checksum(currHike)
                avgAlt /= numValidRows
                domColorHike_hsv = []
                if (checkSum_total / 4 > g.COLOR_CLUSTER):
                    domColorHike_hsv = get_dominant_color_1D(domColorsHike_hsv, g.COLOR_CLUSTER)
                    roundToHundredth(domColorHike_hsv)

                # TODO: color ranking
                # https://github.com/EverydayDesignStudio/capra-color/blob/master/generate_colors.py

                # TODO: altitude ranking

                hikeStartDatetime = datetime.datetime.fromtimestamp(startTime)
                hikeEndDatetime = datetime.datetime.fromtimestamp(endTime)

                domColorHike_rgb = hsvToRgb(domColorHike_hsv[0], domColorHike_hsv[1], domColorHike_hsv[2])
                domColorHike_hsv_str = "{},{},{}".format(domColorHike_hsv[0], domColorHike_hsv[1], domColorHike_hsv[2])
                domColorHike_rgb_str = "{},{},{}".format(domColorHike_rgb[0], domColorHike_rgb[1], domColorHike_rgb[2])


                #     hike_id, avg_altitude,
                #     start_time, start_year, start_month, start_day, start_minute, start_dayofweek,
                #     end_time, end_year, end_month, end_day, end_minute, end_dayofweek,
                #     color_hsv, color_rgb, color_rank_value, color_rank,               # TODO: calculate color rank
                #     pictures, path

                print("[{}] @@ Writing a row to hikes table for Hike {} ...".format(timenow(), currHike))
                logger.info("[{}] @@ Writing a row to hikes table for Hike {} ...".format(timenow(), currHike))
                pDBController.upsert_hike(currHike, avgAlt,
                                            startTime, hikeStartDatetime.year, hikeStartDatetime.month, hikeStartDatetime.day, hikeStartDatetime.hour * 60 + hikeStartDatetime.minute, hikeStartDatetime.weekday(),
                                            endTime, hikeEndDatetime.year, hikeEndDatetime.month, hikeEndDatetime.day, hikeEndDatetime.hour * 60 + hikeEndDatetime.minute, hikeEndDatetime.weekday(),
                                            domColorHike_hsv_str, domColorHike_rgb_str, -1, currHike,
                                            numValidRows, dest)

                # suppose hike is finished, now do the resizing
                print("[{}]   Hike {} took {} seconds for transfer & PP.".format(timenow(), str(currHike), str(time.time() - hikeTimer)))
                logger.info("[{}]   Hike {} took {} seconds for transfer & PP.".format(timenow(), str(currHike), str(time.time() - hikeTimer)))

            # resizing/rotating is not done
            else:
                rTimer = time.time()
                i = 0
                while(i < len(validRows)):
                    row = validRows[i]
                    picPathCam1 = build_picture_path(currHike, index_in_hike, 1)
                    picPathCam2 = build_picture_path(currHike, index_in_hike, 2)
                    picPathCam2f = build_picture_path(currHike, index_in_hike, 2, True)
                    picPathCam3 = build_picture_path(currHike, index_in_hike, 3)

                    # resize and rotate for newly added pictures
                    #    1. make a copy of pic2 as pic2'f'
                    if (not os.path.exists(picPathCam2f)):
                        Image.open(picPathCam2).copy().save(picPathCam2f)

                    #    2. resize to 427x720 and rotate 90 deg
                    if (isNew):
                        Image.open(picPathCam1).resize((427, 720), Image.ANTIALIAS).rotate(90, expand=True).save(picPathCam1)
                        Image.open(picPathCam2).resize((427, 720), Image.ANTIALIAS).rotate(90, expand=True).save(picPathCam1)
                        Image.open(picPathCam3).resize((427, 720), Image.ANTIALIAS).rotate(90, expand=True).save(picPathCam1)


                    i += 1

                print("[{}]   Hike {} rotating and resizing took {} seconds.".format(timenow(), str(currHike), str(time.time() - rTimer)))
                logger.info("[{}]   Hike {} rotating and resizing took {} seconds.".format(timenow(), str(currHike), str(time.time() - rTimer)))

            if (numValidRows != currExpectedHikeSize):
                print("[{}] !!! Invalid rows detected in hike {}".format(timenow(), str(currHike)))
                logger.info("[{}] !!! Invalid rows detected in hike {}".format(timenow(), str(currHike)))

            # Log summary
            compute_checksum(currHike)
            print("[{}] Total valid rows in Hike {}: {}".format(timenow(), str(currHike), str(numValidRows)))
            print("[{}] Total transferred files in hike {}: {}".format(timenow(), str(currHike), str(checkSum_transferred)))
            logger.info("[{}] Total valid rows in Hike {}: {}".format(timenow(), str(currHike), str(numValidRows)))
            logger.info("[{}] Total transferred files in hike {}: {}".format(timenow(), str(currHike), str(checkSum_transferred)))

        else:
            print("[{}] Hike {} is fully transferred.".format(timenow(), str(currHike)))
            logger.info("[{}] Hike {} is fully transferred.".format(timenow(), str(currHike)))

        print("[{}] Hike {} complete. Took total {} seconds.".format(timenow(), currHike, str(time.time() - hikeTimer)))
        print("[{}] Proceeding to the next hike... {} -> {}".format(timenow(), str(currHike), str(currHike + 1)))
        logger.info("[{}] Hike {} complete. Took total {} seconds.".format(timenow(), currHike, str(time.time() - hikeTimer)))
        logger.info("[{}] Proceeding to the next hike... {} -> {}".format(timenow(), str(currHike), str(currHike + 1)))

        currHike += 1

    # TODO: global color ranking
    # TODO: global altitude ranking

    print("[{}] --- {} seconds ---".format(timenow(), str(time.time() - start_time)))
    logger.info("[{}] --- {} seconds ---".format(timenow(), str(time.time() - start_time)))


# ==================================================================
getDBControllers()
readHallEffectThread()

while True:
    HALL_EFFECT_ON.wait()
    createLogger()
    start_time = time.time()
    try:
        if (isCameraUp()):
            copy_remote_db()

            # if camera DB is still fresh, do not run transfer script
            if (not updateDB()):
                g.flag_start_transfer = False
                HALL_EFFECT_ON.clear()
                continue

            # copy the current snapshot of master DB for checking references
            copy_master_db()

            start_transfer()
            # if transfer is successfully finished pause running until camera is dismounted and re-mounted
            print("## Transfer finished. Pause the script")
            g.flag_start_transfer = False
            HALL_EFFECT_ON.clear()
            make_backup_remote_db()
        else:
            print("[{}]     CAMERA SIGNAL LOST !! Please check the connection and retry. Terminating transfer process..".format(timenow()))
            logger.info("[{}]     CAMERA SIGNAL LOST !! Please check the connection and retry. Terminating transfer process..".format(timenow()))

    # TODO: clean up hanging processes when restarting
    #           fuser capra_projector.db -k
    except Exception as e:
        print("[{}]: !!   Encounter an exception while transferring restarting the script..".format(timenow()))
        logger.info("[{}]: !!   Encounter an exception while transferring restarting the script..".format(timenow()))
        if hasattr(e, 'message'):
            print(e.message, '\n')
        print(e)
        print(traceback.format_exc())

        python = sys.executable
        os.execl(python, python, * sys.argv)
