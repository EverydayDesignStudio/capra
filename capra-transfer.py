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
import logging
g.init()

VERBOSE = False

GPIO.setmode(GPIO.BCM)                              # Set's GPIO pins to BCM GPIO numbering
GPIO.setup(g.HALL_EFFECT_PIN, GPIO.IN)              # Set our input pin to be an input
HALL_EFFECT_ON = threading.Event()                  # https://blog.miguelgrinberg.com/post/how-to-make-python-wait

logger = None
rsync_status = None
cDBController = None
pDBController = None
retry = 0
RETRY_MAX = 5

checkSum_transferred = 0
checkSum_rotated = 0
checkSum_total = 0

colrankHikeCounter = 0
colrankGlobalCounter = 0

domColors = []
commits = []        # deferred commits due to concurrency
threads = []
threadPool = None

# ### Database location ###
CAPRAPATH = g.CAPRAPATH_PROJECTOR
DATAPATH = g.DATAPATH_PROJECTOR
CAMERA_DB = DATAPATH + g.DBNAME_CAMERA
CAMERA_BAK_DB = DATAPATH + g.DBNAME_CAMERA_BAK
PROJECTOR_DB = DATAPATH + g.DBNAME_MASTER
BLACK_IMAGE = DATAPATH + "black.jpeg"

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


def make_backup_remote_db():
    subprocess.Popen(['cp', CAMERA_DB, CAMERA_BAK_DB], stdout=subprocess.PIPE)
    return


# 1. make db connections
def getDBControllers():
    global cDBController, pDBController

    # this will be a local db, copied from camera
    cDBController = SQLController(database=CAMERA_DB)
    # master projector db
    pDBController = SQLController(database=PROJECTOR_DB)


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
    checkSum_rotated = count_files_in_directory(build_hike_path(currHike), g.FILENAME_ROTATED)
    checkSum_total = checkSum_transferred + checkSum_rotated


def validate_color(hikeColor):
    return hikeColor is not None and hikeColor and not (hikeColor[0] < 0.001 and hikeColor[1] < 0.001 and hikeColor[2] < 0.001)


def check_hike_postprocessing(currHike):
    hikeColor1 = pDBController.get_hike_average_color(currHike, 1)
    hikeColor2 = pDBController.get_hike_average_color(currHike, 2)
    hikeColor3 = pDBController.get_hike_average_color(currHike, 3)
    return validate_color(hikeColor1) and validate_color(hikeColor2) and validate_color(hikeColor3)


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
    color1 = None
    color2 = None
    color3 = None

#    print("{}: {}".format(index_in_hike, row))

    if (pDBController.get_picture_at_timestamp(row[0]) > 0):
        color1 = pDBController.get_picture_dominant_color(row[0], 1)
        color2 = pDBController.get_picture_dominant_color(row[0], 2)
        color3 = pDBController.get_picture_dominant_color(row[0], 3)
    else:
        try:
            # round color values to the nearest hundredth
            if (color1 is None):
                color_resCode, color_res1 = get_dominant_colors_for_picture(picPathCam1)
                color1 = color_res1.split(", ")


            if (color2 is None):
                color_resCode, color_res2 = get_dominant_colors_for_picture(picPathCam2)
                color2 = color_res2.split(", ")


            if (color3 is None):
                color_resCode, color_res3 = get_dominant_colors_for_picture(picPathCam3)
                color3 = color_res3.split(", ")

        # TODO: check if invalid files are handled correctly
        # TODO: how do we redo failed rows?
        except:
            print("[{}]     Exception at Hike {}, row {} while extracting dominant color".format(timenow(), currHike, str(row[3])))
            print(traceback.format_exc())
            logger.info("[{}]     Exception at Hike {}, row {} while extracting dominant color".format(timenow(), currHike, str(row[3])))
            logger.info(traceback.format_exc())

    roundToHundredth(color1)
    roundToHundredth(color2)
    roundToHundredth(color3)

    picDatetime = datetime.datetime.fromtimestamp(row[0])

    # (time, year, month, day, minute, dayofweek,
    #   hike, index_in_hike, altitude, altrank_hike, altrank_global,
    #   camera1, camera1_color_hsv, camera1_color_rgb,
    #   camera2, camera2_color_hsv, camera2_color_rgb,
    #   colrank_value, colrank_hike, colrank_global,
    #   camera3, camera3_color_hsv, camera3_color_rgb, camera_landscape)

    # ** 0 is monday in dayofweek
    # ** camera_landscape points to the path to cam2 pic
    commit = (row[0], picDatetime.year, picDatetime.month, picDatetime.day, picDatetime.hour * 60 + picDatetime.minute, picDatetime.weekday(),
                currHike, index_in_hike, row[1], colrankHikeCounter, colrankGlobalCounter,
                picPathCam1, "({},{},{})".format(color1[0], color1[1], color1[2]), "({},{},{})".format(color1[3], color1[4], color1[5]),
                picPathCam2, "({},{},{})".format(color2[0], color2[1], color2[2]), "({},{},{})".format(color2[3], color2[4], color2[5]),
                -1, colrankHikeCounter, colrankGlobalCounter,
                picPathCam3, "({},{},{})".format(color3[0], color3[1], color3[2]), "({},{},{})".format(color3[3], color3[4], color3[5]), picPathCam2f)

    # TODO: pass information needed for the transfer animation as a JSON file

    return color1, color2, color3, commit


def start_transfer():
    global cDBController, pDBController, rsync_status, retry, hall_effect
    global checkSum_transferred, checkSum_rotated, checkSum_total, colrankHikeCounter, colrankGlobalCounter
    global logger
    global domColors, commits, threads, threadPool

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
                # TRANSFER

                # POST-PROCESSING
                avgAlt = 0
                startTime = 9999999999
                endTime = -1

                # for colors
                domColorsCam1 = []
                domColorsCam2 = []
                domColorsCam3 = []

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
                    color1, color2, color3, commit = thread.result()
                    domColorsCam1.append([color1[0], color1[1], color1[2]])
                    domColorsCam2.append([color2[0], color2[1], color2[2]])
                    domColorsCam3.append([color3[0], color3[1], color3[2]])
                    commits.append(commit)
                threadPool.shutdown(wait=True)

                # commit changes
                #  ** sqlite does not support concurrent write options
                for commit in commits:
                    pDBController.upsert_picture(*commit)

                # make a row for the hike table with postprocessed values
                compute_checksum(currHike)
                avgAlt /= numValidRows
                hikeDomCol1 = []
                hikeDomCol2 = []
                hikeDomCol3 = []
                if (checkSum_total / 4 > g.COLOR_CLUSTER):
                    hikeDomCol1 = get_dominant_color_1D(domColorsCam1, g.COLOR_CLUSTER)
                    hikeDomCol2 = get_dominant_color_1D(domColorsCam2, g.COLOR_CLUSTER)
                    hikeDomCol3 = get_dominant_color_1D(domColorsCam3, g.COLOR_CLUSTER)
                    roundToHundredth(hikeDomCol1)
                    roundToHundredth(hikeDomCol2)
                    roundToHundredth(hikeDomCol3)

                # TODO: color ranking
                # https://github.com/EverydayDesignStudio/capra-color/blob/master/generate_colors.py

                # TODO: altitude ranking

                hikeStartDatetime = datetime.datetime.fromtimestamp(startTime)
                hikeEndDatetime = datetime.datetime.fromtimestamp(endTime)

                # (hike_id, avg_altitude, \
                #     avg_color_camera1_hsv, avg_color_camera2_hsv, avg_color_camera3_hsv, \
                #     start_time, start_year, start_month, start_day, start_minute, start_dayofweek \
                #     end_time, end_year, end_month, end_day, end_minute, end_dayofweek \
                #     pictures, path)
                print("[{}] @@ Writing a row to hikes table for Hike {} ...".format(timenow(), currHike))
                logger.info("[{}] @@ Writing a row to hikes table for Hike {} ...".format(timenow(), currHike))
                pDBController.upsert_hike(currHike, avgAlt,
                                            "({},{},{})".format(hikeDomCol1[0], hikeDomCol1[1], hikeDomCol1[2]),
                                            "({},{},{})".format(hikeDomCol2[0], hikeDomCol2[1], hikeDomCol2[2]),
                                            "({},{},{})".format(hikeDomCol3[0], hikeDomCol3[1], hikeDomCol3[2]),
                                            startTime, hikeStartDatetime.year, hikeStartDatetime.month, hikeStartDatetime.day, hikeStartDatetime.hour * 60 + hikeStartDatetime.minute, hikeStartDatetime.weekday(),
                                            endTime, hikeEndDatetime.year, hikeEndDatetime.month, hikeEndDatetime.day, hikeEndDatetime.hour * 60 + hikeEndDatetime.minute, hikeEndDatetime.weekday(),
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
