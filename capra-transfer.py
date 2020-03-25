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
# DB = '/home/pi/Pictures/capra-projector.db'
# PATH = '/home/pi/Pictures'
PATH = '../capra-sample-data/'
CAMERA_DB = PATH + 'capra-hd/capra_camera_test.db'
PROJECTOR_DB = PATH + 'capra-hd/capra_projector_test.db'
blank_path = '{p}/blank.png'.format(p=PATH)


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
    if (hikeID > 0):
        res = PATH + base + '/hike' + str(hikeID)
    else:
        # put -1 for hikeID to build a path for the upper directory
        # i.e.) "/capra-storage" for rsync destination
        res = PATH + base
    if makeNew and not os.path.exists(res):
        os.makedirs(res)
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

#    copy_remote_db()

    latest_master_hikeID = pDBController.get_last_hike_id()
    latest_remote_hikeID = cDBController.get_last_hike_id()

    # TODO: improve check logic; missing hikes or partially-transferred hikes
    numNewHikes = latest_remote_hikeID - latest_master_hikeID

    hikeCounter = 0
    checkSum = 0

    print("[{}] @@@ # hikes on Camera: {}".format(timenow(), str(latest_remote_hikeID)))
    print("[{}] @@@ # hikes on Projector: {}".format(timenow(), str(latest_master_hikeID)))
    print("[{}] @@@ # hikes to transfer: {}".format(timenow(), str(numNewHikes)))

#    numNewHikes = 2
    # 3. determine how many hikes should be transferred
    while hikeCounter <= numNewHikes:
        currHike = latest_master_hikeID + hikeCounter
        print("[{}] @ currHike: {}".format(timenow(), str(currHike)))
        if (currHike == 0):
            # skip the validity check for newly created databases
            print("[{}] @ Adjusting initial value for currHike..".format(timenow()))
            hikeCounter += 1
            continue

        # C-1.  validity check
        #   ** For photos with invalid data, we won't bother restoring/fixing incorrect metatdata.
        #      The row (all 3 photos) will be dropped as a whole
        validRows = cDBController.get_valid_photos_in_given_hike(currHike)
        numRows = len(validRows)
        checkSum_transfer = 3 * numRows
        checkSum_transfer_and_rotated = 4 * numRows
        # TODO: change path to match projector file system
        numfiles = count_files_in_directory(build_hike_path("capra-storage", currHike), g.FILENAME)
        numResizedFiles = count_files_in_directory(build_hike_path("capra-storage", currHike), g.FILENAME_ROTATED)
        print("numRows: " + str(numRows))
        print("files in hike {}: {}".format(str(currHike), str(numfiles)))

        # TRANSFER
        # skip if a hike is fully transferred already
        if (checkSum_transfer_and_rotated == numfiles + numResizedFiles):
            hikeCounter += 1
            continue

        avgAlt = 0
        avgHue = 0
        avgSat = 0
        avgVal = 0
        domColors = []
        startTime = 9999999999
        endTime = -1
        src = ""
        dest = ""

        # for colors
        color_rows_checked = 0
        color_rows_error = 0

        # C-2.  once all data is confirmed and valid, deploy rsync for 3 photos
        for row in validRows:
            # (time, alt, color, hike, index, cam1, cam2, cam3, date_created, date_updated)
            src = row[5][:-5] + "*" + row[5][-4:]      # "/home/pi/capra-storage/hike1/1_cam2.jpg" --> "/home/pi/capra-storage/hike1/1_cam*.jpg"
            dest = build_hike_path("capra-storage", currHike, True)

            # update timestamps
            if (row[0] < startTime):
                startTime = row[0]
            if (row[0] > endTime):
                endTime = row[0]

            avgAlt += int(row[1])

            # deploy rsync and add database row to the master db
            rsync_status = subprocess.Popen(['rsync', '--update', '-av', src, dest], stdout=subprocess.PIPE)
            # TODO: possibly log rsync status or is it too verbose?
            # for line in rsync_status.stdout:
            #    log("rsync: '%s'" % line)

            rsync_status.wait()
            print("Row {} - return code: {}".format(str(row[4]), rsync_status.returncode))
            # when rsync is successfully finished,
            if (rsync_status.returncode == 0):
                print("    Row {} transfer completed".format(row[4]))

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
                color_resCode, color_res = get_dominant_colors_for_picture(currHike, str(row[4]) + "_cam2.jpg")
                if (color_resCode < 0):
                    color_rows_error += 1
                else:
                    color_rows_checked += 1
                print(color_res)

                color = color_res.split(", ")

                # TODO: look into CV library for image recognition and build keyword mapping
                # avgHue += color[0]
                # avgSat += color[1]
                # avgVal += color[2]
                domColors.append([color[0], color[1], color[2]])

                cam1Dest = dest + "/" + str(row[4]) + "_cam1.jpg"
                cam2Dest = dest + "/" + str(row[4]) + "_cam2.jpg"
                cam3Dest = dest + "/" + str(row[4]) + "_cam3.jpg"

                # (time, hikeID, index_in_hike, altitude, hue, saturation, value, red, green, blue, camera1, camera2, camera3, camera_landscape)
                pDBController.upsert_picture(row[0], currHike, row[4], row[1], color[0], color[1], color[2], color[3], color[4], color[5], cam1Dest, cam2Dest, cam3Dest, "tmp")
            else:
                print("### Rsync failed at row {}".format(row[4] - 1))

        # CHECK RESIZE AND ROTATE
        # if the numrows and numResizedFiles doesn't match, perform the check and rotate missing files

        # compare checksum
        # TODO: count files in a specific naming format; cam1, cma2, cam3 and resized
        numTotalFiles = count_files_in_directory(build_hike_path("capra-storage", currHike), g.FILENAME) + count_files_in_directory(build_hike_path("capra-storage", currHike), g.FILENAME_ROTATED)
        print("hike " + str(currHike) + " : " + str(numTotalFiles))

        if (checkSum_transfer_and_rotated == numTotalFiles):
            # /home/pi/capra-storage/hikeX -> /media/pi/capra-hd/hikeX

            print("### Hike {} finished, {} valid pictures and {} invalid pictures.".format(currHike, color_rows_checked, color_rows_error))

            # make a row for hike table with postprocessed values
            avgAlt /= numRows
            # avgHue /= numRows
            # avgSat /= numRows
            # avgVal /= numRows
            if (numTotalFiles / 4 > g.COLOR_CLUSTER):
                hikeDomCol = get_dominant_color_1D(domColors, g.COLOR_CLUSTER)
                print("@@   Hike {}'s dominant color: \n\t\t{}".format(currHike, hikeDomCol))

            # (hike_id, avg_altitude, avg_hue, avg_saturation, avg_value, start_time, end_time, pictures, path)
            print("@@ Writing a row to Hike table..")
            pDBController.upsert_hike(currHike, avgAlt, avgHue, avgSat, avgVal, startTime, endTime, color_rows_checked, dest)

            # TODO: clean up partial files

            print("### Proceeding to the next hike... {} -> {}".format(str(hikeCounter), str(hikeCounter + 1)))
            hikeCounter += 1

        elif (retry < RETRY_MAX):
            print("Total number of files doesn't match!")
            exit()
            retry += 1
            continue

        # what do we do here..?
        else:
            exit()

        # exit()


# ==================================================================
start_time = time.time()

getDBControllers()

# check if camera DB in projector is outdated
# update_transfer_animation_db();

start_transfer()

print("--- %s seconds ---" % (time.time() - start_time))
