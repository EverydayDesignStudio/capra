import globals as g
import glob                                         # File path pattern matching
import os
import os.path
import datetime
import time
import sqlite3                                      # Database Library
import subprocess                                   # Deploy RSyncs
import traceback
from PIL import ImageTk, Image                      # Pillow image functions
from pathlib import Path
from classes.capra_data_types import Picture, Hike
from classes.sql_controller import SQLController
from classes.sql_statements import SQLStatements
from classes.kmeans import get_dominant_colors_for_picture
from classes.kmeans import get_dominant_color_1D
from logging.handlers import FileHandler
g.init()

VERBOSE = False

rsync_status = None
cDBController = None
pDBController = None
retry = 0
RETRY_MAX = 5

checkSum_transferred = 0
checkSum_rotated = 0
checkSum_total = 0

# ### Database location ###
CAPRAPATH = g.CAPRAPATH_PROJECTOR
DATAPATH = g.DATAPATH_PROJECTOR
CAMERA_DB = DATAPATH + g.DBNAME_CAMERA
PROJECTOR_DB = DATAPATH + g.DBNAME_MASTER

# ### Create Logger ###
if os.name == 'nt':
    log_file = "C:\tmp\transfer.log"
else:
    directory = CAPRAPATH + '/' + "log"
    log_file = CAPRAPATH + 'transferLog-' + time.strftime("%Y%m%d) + '.log'
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


def copy_remote_db():
    subprocess.Popen(['rsync', '--inplace', '-avAI', '--no-perms', '--rsh="ssh"', "pi@" + g.IP_ADDR_CAMERA + ":/media/pi/capra-hd/capra_camera_test.db", "/media/pi/capra-hd/"], stdout=subprocess.PIPE)

    time.sleep(1)
    return


# 1. make db connections
def getDBControllers():
    global cDBController, pDBController

    # this will be a local db, copied from camera
    cDBController = SQLController(database=CAMERA_DB)
    # master projector db
    pDBController = SQLController(database=PROJECTOR_DB)


# 2. copy remote DB
def update_transfer_animation_db():
    # if date.today() != date.fromtimestamp(Path(g.PATH_TRANSFER_ANIMATION_DB).stat().st_mtime):
    transfer_from_camera(g.PATH_CAMERA_DB, g.PATH_TRANSFER_ANIMATION_DB)


def count_files_in_directory(path, pattern):
    if (not os.path.exists(path)):
        return 0
    else:
        return len(glob.glob(path + pattern))


def build_hike_path(hikeID, makeNew=False):
    res = DATAPATH + str(hikeID) + '/'
    if makeNew and not os.path.exists(res):
        os.makedirs(res, mode=0o755)
    return res


def build_picture_path(hikeID, index, camNum, rotated=False):
    insert = ""
    if (rotated):
        insert = "r"
    return build_hike_path(hikeID) + str(index) + '_cam' + str(camNum) + insert + '.jpg'


def resize_photo(photoPath, w, h):
    im = Image.open(photoPath)
    im = im.resize((w, h), Image.ANTIALIAS)
    im.save(photoPath)


def rotate_photo(srcFile, destFile, angle):
    image = Image.open(srcFile)
    image_rotated = image.copy().rotate(angle, expand=True)
    image_rotated.save(destFile)


def compute_checksum(currHike):
    global checkSum_total, checkSum_rotated, checkSum_transferred
    checkSum_transferred = count_files_in_directory(build_hike_path(currHike), g.FILENAME)
    checkSum_rotated = count_files_in_directory(build_hike_path(currHike), g.FILENAME_ROTATED)
    checkSum_total = checkSum_transferred + checkSum_rotated


def start_transfer():
    global cDBController, pDBController, rsync_status, retry
    global checkSum_transferred, checkSum_rotated, checkSum_total

    latest_master_hikeID = pDBController.get_last_hike_id()
    latest_remote_hikeID = cDBController.get_last_hike_id()
    print("[{}] @@@ # hikes on Projector: {}".format(timenow(), str(latest_master_hikeID)))
    print("[{}] @@@ # hikes on Camera: {}".format(timenow(), str(latest_remote_hikeID)))
    logger.info("[{}] @@@ # hikes on Projector: {}".format(timenow(), str(latest_master_hikeID)))
    logger.info("[{}] @@@ # hikes on Camera: {}".format(timenow(), str(latest_remote_hikeID)))

    currHike = 1
    checkSum = 0

    # 3. determine how many hikes should be transferred
    while currHike <= latest_remote_hikeID:

        currExpectedHikeSize = cDBController.get_size_of_hike(currHike)
        if (currExpectedHikeSize is None):
            currExpectedHikeSize = 0
        expectedCheckSumTotal = currExpectedHikeSize * 4

        compute_checksum(currHike)
        print("[{}] Hike {}: Total {} rows -- {} out of {} photos transferred".format(timenow(), str(currHike), str(currExpectedHikeSize), str(checkSum_transferred), str(currExpectedHikeSize * 3)))
        print("[{}] Hike {}: Total {} photos expected, found {} photos".format(timenow(), str(currHike), str(expectedCheckSumTotal), str(checkSum_total)))
        logger.info("[{}] Hike {}: Total {} rows -- {} out of {} photos transferred".format(timenow(), str(currHike), str(currExpectedHikeSize), str(checkSum_transferred), str(currExpectedHikeSize * 3)))
        logger.info("[{}] Hike {}: Total {} photos expected, found {} photos".format(timenow(), str(currHike), str(expectedCheckSumTotal), str(checkSum_total)))

        # if a hike is fully transferred, resized and rotated, then skip the transfer for this hike
        # TODO: check return value for empty or non-existing hikes
        if (currExpectedHikeSize != 0 and checkSum_transferred == currExpectedHikeSize * 3 and expectedCheckSumTotal == checkSum_total):
            print("[{}]     # Hike {} fully transferred. Proceeding to the next hike...".format(timenow(), str(currHike)))
            logger.info("[{}]     # Hike {} fully transferred. Proceeding to the next hike...".format(timenow(), str(currHike)))
            currHike += 1
            continue

        # C-1.  validity check
        #   ** For photos with invalid data, we won't bother restoring/fixing incorrect metatdata.
        #      The row (all 3 photos) will be dropped as a whole
        validRows = cDBController.get_valid_photos_in_given_hike(currHike)
        numValidRows = len(validRows)
        checkSum_transfer_and_rotated = 4 * numValidRows

        if (checkSum_transferred < currExpectedHikeSize * 3):
            print("[{}]   Resume transfer on Hike {}: {} out of {} files".format(timenow(), currHike, checkSum_transferred, str(currExpectedHikeSize * 3)))
            logger.info("[{}]   Resume transfer on Hike {}: {} out of {} files".format(timenow(), currHike, checkSum_transferred, str(currExpectedHikeSize * 3)))
            # TRANSFER
            i = 0
            transferTimer = time.time()
            # for row in validRows:
            while(i < len(validRows)):
                row = validRows[i]

                # (time, alt, color, hike, index, cam1, cam2, cam3, date_created, date_updated)
                src = row[5][:-5] + "*" + row[5][-4:]      # "/home/pi/capra-storage/hike1/1_cam2.jpg" --> "/home/pi/capra-storage/hike1/1_cam*.jpg"
                dest = build_hike_path(currHike, True)

                rsync_status = subprocess.Popen(['rsync', '--ignore-existing', '-avA', '--no-perms', '--rsh="ssh"', 'pi@' + g.IP_ADDR_CAMERA + ':' + src, dest], stdout=subprocess.PIPE)
                rsync_status.wait()

                # when rsync is successfully finished,
                if (rsync_status.returncode == 0):
                    # TODO: Transfer Animation stuff
                    i += 1
                else:
                    print("[{}] ### Rsync failed at row {}".format(timenow(), str(row[4] - 1)))
                    logger.info("[{}] ### Rsync failed at row {}".format(timenow(), str(row[4] - 1)))

            print("[{}]   Transfer finished for hike {} -- took {} seconds".format(timenow(), str(currHike), str(time.time() - transferTimer)))
            logger.info("[{}]   Transfer finished for hike {} -- took {} seconds".format(timenow(), str(currHike), str(time.time() - transferTimer)))

        # Compare Checksum
        compute_checksum(currHike)
        print("[{}] Total valid rows in Hike {}: {}".format(timenow(), str(currHike), str(numValidRows)))
        print("[{}] Total transferred files in hike {}: {}".format(timenow(), str(currHike), str(checkSum_transferred)))
        logger.info("[{}] Total valid rows in Hike {}: {}".format(timenow(), str(currHike), str(numValidRows)))
        logger.info("[{}] Total transferred files in hike {}: {}".format(timenow(), str(currHike), str(checkSum_transferred)))

        if (numValidRows != currExpectedHikeSize):
            print("[{}] !!! Invalid rows detected in hike {}".format(timenow(), str(currHike)))
            logger.info("[{}] !!! Invalid rows detected in hike {}".format(timenow(), str(currHike)))

        # All pictures successfully transferred!
        if (currExpectedHikeSize * 3 == checkSum_transferred):
            print("[{}] All pictures for hike {} successfully transferred. \n\t Now starting post-processing work..".format(timenow(), str(currHike)))
            logger.info("[{}] All pictures for hike {} successfully transferred. \n\t Now starting post-processing work..".format(timenow(), str(currHike)))

            # TODO: remove pictures from camera at this point

            avgAlt = 0
            avgHue = 0
            avgSat = 0
            avgVal = 0
            domColors = []
            startTime = 9999999999
            endTime = -1
            hikeTimer = time.time()

            # for colors
            color_rows_checked = 0
            color_rows_error = 0

            # C-2.  once all data is confirmed and valid, deploy rsync for 3 photos
            for row in validRows:
                # update timestamps
                if (row[0] < startTime):
                    startTime = row[0]
                if (row[0] > endTime):
                    endTime = row[0]

                avgAlt += int(row[1])

                picPath_cam1 = build_picture_path(currHike, row[4], 1)
                picPath_cam2 = build_picture_path(currHike, row[4], 2)
                picPath_cam2r = build_picture_path(currHike, row[4], 2, True)
                picPath_cam3 = build_picture_path(currHike, row[4], 3)

                # Make a copy for the second image and rorate CCW 90
                # TODO: make sure we rotate photos in the right direction
                rotate_photo(picPath_cam2, picPath_cam2r, 90)

                # Resize three images
                resize_photo(picPath_cam1, 427, 720)
                resize_photo(picPath_cam2, 427, 720)
                resize_photo(picPath_cam3, 427, 720)

                # Do post-processing
                #  1. calculate dominant HSV/RGB colors
                #  2. update path to each picture for camera 1, 2, 3
                try:
                    color_resCode, color_res = get_dominant_colors_for_picture(picPath_cam2)
                except:
                    print("[{}]     Exception at Hike {}, row {} while extracting dominant color".format(timenow(), currHike, str(row[4])))
                    print(traceback.format_exc())
                    logger.info("[{}]     Exception at Hike {}, row {} while extracting dominant color".format(timenow(), currHike, str(row[4])))
                    logger.info(traceback.format_exc())

                if (color_resCode < 0):
                    color_rows_error += 1
                else:
                    color_rows_checked += 1

                color = color_res.split(", ")
                domColors.append([color[0], color[1], color[2]])

                # (time, hikeID, index_in_hike, altitude, hue, saturation, value, red, green, blue, camera1, camera2, camera3, camera_landscape)
                pDBController.upsert_picture(row[0], currHike, row[4], row[1], color[0], color[1], color[2], color[3], color[4], color[5], picPath_cam1, picPath_cam2, picPath_cam3, "tmp")

        elif (retry < RETRY_MAX):
            # TODO: remove this and implement recovery mechanism on exception
            retry += 1
            print("[{}] Total number of files doesn't match! \n\t Retry {} out of {}".format(timenow(), str(retry), str(RETRY_MAX)))
            logger.info("[{}] Total number of files doesn't match! \n\t Retry {} out of {}".format(timenow(), str(retry), str(RETRY_MAX)))
            continue

        else:
            # what do we do here..?
            print("[{}] MAX RETRY REACHED!! Giving up...".format(timenow()))
            logger.info("[{}] MAX RETRY REACHED!! Giving up...".format(timenow()))
            exit()

        # CHECK FOR RESIZE AND ROTATE
        compute_checksum(currHike)
        print("[{}] Post-processing for Hike {} finished. \
                \n\tTotal {} files. (Expected {} files) \
                \n\t{} valid pictures and {} invalid pictures.".format(timenow(), currHike, checkSum_total, expectedCheckSumTotal, color_rows_checked, color_rows_error))
        logger.info("[{}] Post-processing for Hike {} finished. \
                \n\tTotal {} files. (Expected {} files) \
                \n\t{} valid pictures and {} invalid pictures.".format(timenow(), currHike, checkSum_total, expectedCheckSumTotal, color_rows_checked, color_rows_error))

        # make a row for hike table with postprocessed values
        avgAlt /= numValidRows
        if (checkSum_total / 4 > g.COLOR_CLUSTER):
            hikeDomCol = get_dominant_color_1D(domColors, g.COLOR_CLUSTER)

        # (hike_id, avg_altitude, avg_hue, avg_saturation, avg_value, start_time, end_time, pictures, path)
        print("[{}] @@ Writing a row to hikes table for Hike {} ...".format(timenow(), currHike))
        logger.info("[{}] @@ Writing a row to hikes table for Hike {} ...".format(timenow(), currHike))

        pDBController.upsert_hike(currHike, avgAlt, avgHue, avgSat, avgVal, startTime, endTime, color_rows_checked, dest)

        # TODO: clean up partial files

        print("[{}] ---- hike {} took {} seconds for post-processing ---- ".format(timenow(), str(currHike), str(time.time() - hikeTimer)))
        print("[{}] Hike {} complete. Took total {} seconds.".format(timenow(), currHike, str(time.time() - start_time)))
        print("[{}] Proceeding to the next hike... {} -> {}".format(timenow(), str(currHike), str(currHike + 1)))
        logger.info("[{}] ---- hike {} took {} seconds for post-processing ---- ".format(timenow(), str(currHike), str(time.time() - hikeTimer)))
        logger.info("[{}] Hike {} complete. Took total {} seconds.".format(timenow(), currHike, str(time.time() - start_time)))
        logger.info("[{}] Proceeding to the next hike... {} -> {}".format(timenow(), str(currHike), str(currHike + 1)))

        currHike += 1


# ==================================================================
start_time = time.time()

copy_remote_db()
getDBControllers()

start_transfer()

print("[{}] --- {} seconds ---".format(timenow(), str(time.time() - start_time)))
logger.info("[{}] --- {} seconds ---".format(timenow(), str(time.time() - start_time)))
