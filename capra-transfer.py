# 0) establish a connection with the hardcorded static IPs
#
# 1) first, copy the entire DB from the collector
#
# 2-1) compare the latest hike on CameraDB & ProjectorDB
#
# 2-2) compare checksum (# of pictures in the hike) for hikes
#
# 2-3) run rsync for each hike; deploy rsync command as a subprocess
#
# 3) detect transferred files by...
#   - keep checking for files based on the hike/picture index (does the file exist?)
#
# 4) locate each matching file from the copy of camera's DB
#
# 5) do the color processing; determine the rumosity and run corresponding functions
#
# 5) insert the corresponding row to the explorer's master DB
#
# !!! 6) notify which files are ready to be presented to the animation script

import globals as g
import os, datetime, sqlite3, subprocess
from pathlib import Path
from classes.capra_data_types import Picture, Hike
from classes.sql_controller import SQLController
from classes.sql_statements import SQLStatements

rsync_status = None;
cDBController = None;
pDBController = None;

# Database location
# DB = '/home/pi/Pictures/capra-projector.db'
# PATH = '/home/pi/Pictures'
PATH = '../capra-sample-data/'
CAMERA_DB = PATH + 'capra-hd/capra_camera_test.db'
PROJECTOR_DB = PATH + 'capra-hd/capra_projector_test.db'
blank_path = '{p}/blank.png'.format(p=PATH)

def transfer_from_camera(src, dest):
    # TODO: write this subprocess call
    rsync_status = deploy_subprocess;
    return;

# 1. make db connections
def getDBControllers():
    global cDBController, pDBController

    cDBController = SQLController(database=CAMERA_DB)
    pDBController = SQLController(database=PROJECTOR_DB)

# 2. copy remote DB
def update_transfer_animation_db():
    #if date.today() != date.fromtimestamp(Path(g.PATH_TRANSFER_ANIMATION_DB).stat().st_mtime):
    transfer_from_camera(g.PATH_CAMERA_DB, g.PATH_TRANSFER_ANIMATION_DB);

def build_hike_path(base, hikeID=None, makeNew=False):
    res = "";
    if (hikeID > 0):
        res = PATH + base + '/hike' + str(hikeID);
    else:
        res = PATH + base;
    if makeNew and not os.path.exists(res):
        os.makedirs(res)
    return res;
    # return base + 'hike' + hikeID;

def build_picture_path(base, hikeID, index, camNum):
    return PATH + base + '/hike' + str(hikeID) + '/' + str(index) + '_cam' + str(camNum) + '.jpg';
    # return base + 'hike' + str(hikeID) + '/' + str(index) + '_cam' + str(camNum) + '.jpg';

def start_transfer():
    global cDBController, pDBController

    latest_master_hikeID = pDBController.get_last_hike_id();
    latest_remote_hikeID = cDBController.get_last_hike_id();
    numNewHikes = latest_remote_hikeID - latest_master_hikeID;
    hikeCounter = 1;
    checkSum = 0;

    # 3. determine how many hikes should be transferred
    while hikeCounter <= numNewHikes:
        # TODO: write this query; SELECT pictures FROM hikes WHERE hike_id = (latest_master_hikeID + hikeCounter);
        checkSum = 0;
        if (hikeCounter == 1):
            checkSum = 100; # getNumCountFromHike;
        elif (hikeCounter == 2):
            checkSum = 153; # getNumCountFromHike;
        currHike = latest_master_hikeID + hikeCounter;

        # A.    retrieve each row in pictures
        # B.    check the validity of data in the row
        #     TODO: SELECT count(*) FROM pictures WHERE hike_id == {} AND altitude < mt.everest AND altitude >= 0
        #                                           AND camera1 IS NOT NULL AND camera2 IS NOT NULL AND camera 3 IS NOT NULL
        # C-1.  if some data is corrupted, fix it or drop the row
        #     TODO: finalize the fixes for each fault (i.e. max/null value on altitude, NULL path, invalid timestamp..)
        # C-2.  once all data is confirmed and valid, deploy rsync for 3 photos
        # D.    wait and check for transfers to be done
        # E.    do the postprocessing (i.e. average altitude and color)
        # F.    write to masterDB
        # G.    clean up partial files and proceed to next hike
        res = cDBController.get_valid_photos_in_given_hike(currHike);
        print(len(res));
        print(res);


        exit();

        # TODO: check database first then deploy rsync for each set of photos
        rsync_status = subprocess.call(['rsync', '-av', build_hike_path("capra-hd", currHike), build_hike_path("capra-storage", -1, True)]); # deploy_rsync_subprocess;


        # 4. while a hike is being transferred, find newly added file and write a row to the master DB
        # 5. once a hike is fully transferred, compare the checksum
        prevPicTotal = 0;
        picCounter_cam1 = 0;
        picCounter_cam2 = 0;
        picCounter_cam3 = 0;
        picTotal = 0;
        # rsync_status is None and
        # try:
        # while (os.path.exists(build_hike_path(g.PATH_ON_PROJECTOR, currHike)) and picTotal < checkSum):
        abort = 0;

        while (os.path.exists(build_hike_path("capra-storage", currHike)) and picTotal < checkSum):
#             if (os.path.exists(build_picture_path(g.PATH_ON_PROJECTOR, currHike, picCounter_cam1, 1)):
            if (os.path.exists(build_picture_path("capra-storage", currHike, picCounter_cam1, 1))):
                # TODO: make query to update the DB
                # TODO: resize photo (720x1280 -> 427*720)
                picCounter_cam1 += 1;
                #print("Cam1++; Cam1 total: {}".format(picCounter_cam1));
            # if (os.path.exists(build_picture_path(g.PATH_ON_PROJECTOR, currHike, picCounter_cam2, 2)):
            if (os.path.exists(build_picture_path("capra-storage", currHike, picCounter_cam2, 2))):
                # TODO: make query to update the DB
                # TODO: duplicate photo (720x1280)
                # TODO: resize photo (720x1280 -> 427*720)
                picCounter_cam2 += 1;
                #print("Cam2++; Cam2 total: {}".format(picCounter_cam2));
            # if (os.path.exists(build_picture_path(g.PATH_ON_PROJECTOR, currHike, picCounter_cam3, 3)):
            if (os.path.exists(build_picture_path("capra-storage", currHike, picCounter_cam3, 3))):
                # TODO: make query to update the DB
                # TODO: resize photo (720x1280 -> 427*720)
                picCounter_cam3 += 1;
                #print("Cam3++; Cam3 total: {}".format(picCounter_cam3));

            # TODO: set timeout to be.. 5 min?
            # if (set_timeout_flag):
            if (False):
                abort_rsync_subprocess
                break;

            tmpTotal = picCounter_cam1 + picCounter_cam2 + picCounter_cam3;
            if (prevPicTotal < tmpTotal):
                prevPicTotal = tmpTotal;
                picTotal = prevPicTotal;
            else:
                abort += 1;

            if (abort >= 10):
                exit();

        # TODO: clean up any existing partial files
        # TODO: do post-processing on calculating average altitude and color
        print("Hike{} Total: {}".format(currHike, picTotal));

        # 5-1. restore/re-transfer any missing picture
        # TODO: handle timeout; go through the folder again and re-transfer missing file
        # >> maybe add a dummy black photo to replace the missing file
        # if (rsync_status != 0 or timeout is True or picTotal != checkSum):


        # reset variables before the next iteration
        hikeCounter += 1;


# ==================================================================
getDBControllers();
# check if camera DB in projector is outdated
# update_transfer_animation_db();
start_transfer();
