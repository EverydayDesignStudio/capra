import globals as g
import glob                                         # File path pattern matching
import os
import os.path
import datetime
import time
import sqlite3                                      # Database Library
import subprocess                                   # Deploy RSyncs
from PIL import ImageTk, Image                      # Pillow image functions
from pathlib import Path
from classes.capra_data_types import Picture, Hike
from classes.sql_controller import SQLController
from classes.sql_statements import SQLStatements
from classes.kmeans import get_dominant_colors_for_picture
from classes.kmeans import get_dominant_color_1D
g.init()

VERBOSE = False

rsync_status = None
cDBController = None
pDBController = None
retry = 0
RETRY_MAX = 5

# Database location

# # Desktop test
# PATH = '../capra-sample-data/'
# CAMERA_DB = PATH + 'capra-hd/capra_camera_test.db'
# PROJECTOR_DB = PATH + 'capra-hd/capra_projector_test.db'

# RPi
PATH = '/media/pi'
CAMERA_DB = PATH + '/capra-hd/capra_camera_test.db'
PROJECTOR_DB = PATH + '/capra-hd/capra_projector.db'
blank_path = '{p}/blank.png'.format(p=PATH)


def timenow():
    return str(datetime.datetime.now()).split('.')[0]


def copy_remote_db():
    # # Desktop test
    # subprocess.Popen(['rsync', '--protect-args', '--update', '-av', '--rsh="ssh"', "root@" + g.IP_ADDR_CAMERA + ":/media/pi/capra-hd/capra_projector.db", "../capra-sample-data/capra-hd/"], stdout=subprocess.PIPE)

    # RPi
    subprocess.Popen(['rsync', '--inplace', '-avAI', '--no-perms', '--rsh="ssh"', "pi@" + g.IP_ADDR_CAMERA + ":/media/pi/capra-hd/capra_camera_test.db", "/media/pi/capra-hd/"], stdout=subprocess.PIPE)

    time.sleep(1)
    return


def transfer_from_camera(src, dest):
    # TODO: write this subprocess call
    rsync_status = deploy_subprocess
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
        return len(glob.glob(path + '/' + pattern))
#        return len([name for name in os.listdir(path) if os.path.isfile(os.path.join(path, name))])


def build_hike_path(base, hikeID=None, makeNew=False):
    res = ""
    if (hikeID is None):
        # put -1 for hikeID to build a path for the upper directory
        # i.e.) "/capra-storage" for rsync destination
        res = PATH + base
    elif (hikeID > 0):
        ins = 'hike'
        if (base != ""):
            ins = '/' + ins

        res = PATH + base + ins + str(hikeID)
    if makeNew and not os.path.exists(res):
        os.makedirs(res, mode=0o755)
    return res
    # return base + 'hike' + hikeID;


def build_picture_path(base, hikeID, index, camNum):
    return PATH + base + '/hike' + str(hikeID) + '/' + str(index) + '_cam' + str(camNum) + '.jpg'
    # return base + 'hike' + str(hikeID) + '/' + str(index) + '_cam' + str(camNum) + '.jpg';


def resize_photo(path, filename, w, h):
    im = Image.open(path + "/" + filename)
    im = im.resize((w, h), Image.ANTIALIAS)
    im.save(path + "/" + filename)


def rotate_photo(path, srcFileName, destFileName, angle):
    image = Image.open(path + "/" + srcFileName)
    image_rotated = image.copy().rotate(angle, expand=True)
    image_rotated.save(path + "/" + destFileName)


# test
def create_camera_db_entries():
    # testing
    cursor = cDBController.connection.cursor()
    ttime = 1561986050.65861
    taltitude = 1
    thike = 3
    for i in range(51):
        tcamera1 = "../capra-sample-data/capra-hd/hike{}/{}_cam1.jpg".format(thike, i)
        tcamera2 = "../capra-sample-data/capra-hd/hike{}/{}_cam2.jpg".format(thike, i)
        tcamera3 = "../capra-sample-data/capra-hd/hike{}/{}_cam3.jpg".format(thike, i)
        statement = 'INSERT OR REPLACE INTO pictures (time, altitude, hike, index_in_hike, camera1, camera2, camera3) VALUES ({}, {}, {}, {}, "{}", "{}", "{}")'.format(ttime, taltitude, thike, i, tcamera1, tcamera2, tcamera3)
        cursor.execute(statement)
        ttime += 1
        taltitude += 1
    cDBController.connection.commit()
    exit()


# test
def update_picture_path_camera_db():
    cursor = cDBController.connection.cursor()
    statement = "SELECT * from pictures;"
    cursor.execute(statement)
    rows = cursor.fetchall()
    for row in rows:
        t1 = row[5][30:]
        t2 = row[6][30:]
        t3 = row[7][30:]
        picPath1 = "/media/pi/capra-hd/test/" + t1
        picPath2 = "/media/pi/capra-hd/test/" + t2
        picPath3 = "/media/pi/capra-hd/test/" + t3
        statement2 = "REPLACE INTO pictures (time, altitude, hike, index_in_hike, camera1, camera2, camera3) VALUES ({}, {}, {}, {}, '{}', '{}', '{}')".format(str(row[0]), str(row[1]), str(row[3]), str(row[4]), picPath1, picPath2, picPath3)
        cursor.execute(statement2)
        cDBController.connection.commit()
    return


def start_transfer():
    global cDBController, pDBController, rsync_status, retry

    latest_master_hikeID = pDBController.get_last_hike_id()
    latest_remote_hikeID = cDBController.get_last_hike_id()
    print("[{}] @@@ # hikes on Projector: {}".format(timenow(), str(latest_master_hikeID)))
    print("[{}] @@@ # hikes on Camera: {}".format(timenow(), str(latest_remote_hikeID)))

    currHike = 1
    checkSum = 0

    # 3. determine how many hikes should be transferred
    while currHike <= latest_remote_hikeID:
        # currHike = latest_master_hikeID + hikeCounter

        currExpectedHikeSize = cDBController.get_size_of_hike(currHike)
        if (currExpectedHikeSize is None):
            currExpectedHikeSize = 0
        expectedCheckSumTotal = currExpectedHikeSize * 4

        # # Desktop test
        # checkSum = count_files_in_directory(build_hike_path("capra-storage", currHike), g.FILENAME) + count_files_in_directory(build_hike_path("capra-storage", currHike), g.FILENAME_ROTATED)

        # RPi
        checkSum_transferred = count_files_in_directory(build_hike_path("/capra-hd", currHike), g.FILENAME)
        checkSum_rotated = count_files_in_directory(build_hike_path("/capra-hd", currHike), g.FILENAME_ROTATED)
        checkSum_total = checkSum_transferred + checkSum_rotated

        print("[{}] Hike {}: Total {} rows -- {} out of {} photos transferred".format(timenow(), str(currHike), str(currExpectedHikeSize), str(checkSum_transferred), str(currExpectedHikeSize * 3)))
        print("[{}] Hike {}: Total {} photos expected, found {} photos".format(timenow(), str(currHike), str(expectedCheckSumTotal), str(currExpectedHikeSize), str(checkSum_total)))

        # if a hike is fully transferred, resized and rotated, then skip the transfer for this hike
        # TODO: check return value for empty or non-existing hikes
        if (currExpectedHikeSize != 0 and checkSum_transferred == currExpectedHikeSize * 3 and expectedCheckSumTotal == checkSum_total):
            print("[{}]     # Hike {} fully transferred. Proceeding to the next hike...".format(timenow(), str(hikeCounter)))
            hikeCounter += 1
            continue

        remote_hike_path = cDBController.get_hike_path(currHike)
        master_hike_path = build_hike_path("/capra-hd", currHike)

        # C-1.  validity check
        #   ** For photos with invalid data, we won't bother restoring/fixing incorrect metatdata.
        #      The row (all 3 photos) will be dropped as a whole

        # TODO: make sure validity for rows are check on Camera's end
        validRows = cDBController.get_valid_photos_in_given_hike(currHike)
        numValidRows = len(validRows)
        checkSum_transfer_and_rotated = 4 * numValidRows

        # TRANSFER
        i = 0
        transferTimer = time.time()
        # for row in validRows:
        while(i < len(validRows)):
            row = validRows[i]

            # (time, alt, color, hike, index, cam1, cam2, cam3, date_created, date_updated)
            src = row[5][:-5] + "*" + row[5][-4:]      # "/home/pi/capra-storage/hike1/1_cam2.jpg" --> "/home/pi/capra-storage/hike1/1_cam*.jpg"

            # # Desktop test
            # dest = build_hike_path("capra-storage", currHike, True)

            # RPi
            dest = build_hike_path("/capra-hd", currHike, True)

            rsync_status = subprocess.Popen(['rsync', '--ignore-existing', '-avA', '--no-perms', '--rsh="ssh"', 'pi@' + g.IP_ADDR_CAMERA + ':' + src, dest], stdout=subprocess.PIPE)
            rsync_status.wait()

            # when rsync is successfully finished,
            if (rsync_status.returncode == 0):
                # TODO: Transfer Animation stuff
                i += 1
            else:
                print("[{}] ### Rsync failed at row {}".format(timenow(), str(row[4] - 1)))

        print("[{}]   Transfer finished for hike {} -- took {} seconds".format(timenow(), str(currHike), str(time.time() - transferTimer)))

        # Compare Checksum

        # # Desktop test
        # numfiles = count_files_in_directory(build_hike_path("capra-storage", currHike), g.FILENAME)
        # numResizedFiles = count_files_in_directory(build_hike_path("capra-storage", currHike), g.FILENAME_ROTATED)

        # RPi
        numTransferredFiles = count_files_in_directory(build_hike_path("/capra-hd", currHike), g.FILENAME)
        numResizedFiles = count_files_in_directory(build_hike_path("/capra-hd", currHike), g.FILENAME_ROTATED)

        print("[{}] Total valid rows in Hike {}: {}".format(timenow(), str(currHike), str(numValidRows)))
        print("[{}] Total transferred files in hike {}: {}".format(timenow(), str(currHike), str(numTransferredFiles)))

        if (numValidRows != currExpectedHikeSize):
            print("[{}] !!! Invalid rows detected in hike {}".format(timenow(), str(currHike)))

        # All pictures successfully transferred!
        if (expectedCheckSum == numTransferredFiles):

            # TODO: remove pictures from camera at this point

            avgAlt = 0
            avgHue = 0
            avgSat = 0
            avgVal = 0
            domColors = []
            startTime = 9999999999
            endTime = -1
            src = ""
            dest = ""
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

                dest = build_hike_path("/capra-hd", currHike, True)

                # Make a copy for the second image and rorate CCW 90
                # TODO: make sure we rotate photos in the right direction
                rotate_photo(dest, str(row[4]) + "_cam2.jpg", str(row[4]) + "_cam2r.jpg", 90)

                # Resize three images
                resize_photo(dest, str(row[4]) + "_cam1.jpg", 427, 720)
                resize_photo(dest, str(row[4]) + "_cam2.jpg", 427, 720)
                resize_photo(dest, str(row[4]) + "_cam3.jpg", 427, 720)

                # Do post-processing
                #  1. calculate dominant HSV/RGB colors
                #  2. update path to each picture for camera 1, 2, 3
                color_resCode, color_res = get_dominant_colors_for_picture(build_hike_path("/capra-hd"), currHike, str(row[4]) + "_cam2.jpg")
                if (color_resCode < 0):
                    color_rows_error += 1
                else:
                    color_rows_checked += 1

                color = color_res.split(", ")
                domColors.append([color[0], color[1], color[2]])

                cam1Dest = dest + "/" + str(row[4]) + "_cam1.jpg"
                cam2Dest = dest + "/" + str(row[4]) + "_cam2.jpg"
                cam3Dest = dest + "/" + str(row[4]) + "_cam3.jpg"

                # (time, hikeID, index_in_hike, altitude, hue, saturation, value, red, green, blue, camera1, camera2, camera3, camera_landscape)
                pDBController.upsert_picture(row[0], currHike, row[4], row[1], color[0], color[1], color[2], color[3], color[4], color[5], cam1Dest, cam2Dest, cam3Dest, "tmp")

        elif (retry < RETRY_MAX):
            # TODO: remove this and implement recovery mechanism on exception
            retry += 1
            print("[{}] Total number of files doesn't match! \n\t Retry {} out of {}".format(timenow(), str(retry), str(RETRY_MAX)))
            continue

        else:
            # what do we do here..?
            print("[{}] MAX RETRY REACHED!! Giving up...".format(timenow()))
            exit()

        # CHECK FOR RESIZE AND ROTATE

        # # Desktop test
        # numTotalFiles = count_files_in_directory(build_hike_path("capra-storage", currHike), g.FILENAME) + count_files_in_directory(build_hike_path("capra-storage", currHike), g.FILENAME_ROTATED)

        # RPi
        numTotalFiles = count_files_in_directory(build_hike_path("/capra-hd", currHike), g.FILENAME) + count_files_in_directory(build_hike_path("/capra-hd", currHike), g.FILENAME_ROTATED)

        print("[{}] hike ".format(timenow()) + str(currHike) + " : " + str(numTotalFiles))

        print("[{}] $ checksum: {}".format(timenow(), str(expectedCheckSum)))
        print("[{}] $ numtotal: {}".format(timenow(), str(numTotalFiles)))

        print("[{}] ### Extracting dominant colors for Hike {} finished, {} valid pictures and {} invalid pictures.".format(timenow(), currHike, color_rows_checked, color_rows_error))

        # make a row for hike table with postprocessed values
        avgAlt /= numRows
        if (numTotalFiles / 4 > g.COLOR_CLUSTER):
            hikeDomCol = get_dominant_color_1D(domColors, g.COLOR_CLUSTER)

        # (hike_id, avg_altitude, avg_hue, avg_saturation, avg_value, start_time, end_time, pictures, path)
        # print("[{}] @@ Writing a row to Hike table..".format(timenow()))
        pDBController.upsert_hike(currHike, avgAlt, avgHue, avgSat, avgVal, startTime, endTime, color_rows_checked, dest)

        # TODO: clean up partial files

        print("[{}] ### ---- hike {} took {} seconds for post-processing ---- ".format(timenow(), str(currHike), str(time.time() - hikeTimer)))
        print("[{}] ### Proceeding to the next hike... {} -> {}".format(timenow(), str(hikeCounter), str(hikeCounter + 1)))

        currHike += 1


# ==================================================================
start_time = time.time()

copy_remote_db()
getDBControllers()

# check if camera DB in projector is outdated
# update_transfer_animation_db();

start_transfer()

print("[{}] --- {} seconds ---".format(timenow(), str(time.time() - start_time)))
