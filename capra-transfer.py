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
import os, datetime
from pathlib import Path
import subprocess

rsync_status = None;
cur_masterDB = None;
cur_remoteDB = None;

def getDBCursor(dbPath):
    conn = sqlite3.connect(dbPath);
    cur = conn.cursor();
    return cur;

def transfer_from_camera(src, dest):
    # TODO: write this subprocess call
    rsync_status = deploy_subprocess;
    return;

# 1. make db connections
def connectDBs():
    cur_masterDB = getDBCursor(g.PATH_PROJECTOR_DB);
    cur_remoteDB = getDBCursor(g.PATH_CAMERA_DB);

# 2. copy remote DB
def update_transfer_animation_db():
    if date.today() != date.fromtimestamp(Path(g.PATH_TRANSFER_ANIMATION_DB).stat().st_mtime):
        transfer_from_camera(g.PATH_CAMERA_DB, g.PATH_TRANSFER_ANIMATION_DB);

def build_hike_path(base, hikeID=None, makeNew=False):
    res = "";
    if (hikeID > 0):
        res = '../capra-sample-data/' + base + '/hike' + str(hikeID);
    else:
        res = '../capra-sample-data/' + base;
    if makeNew and not os.path.exists(res):
        os.makedirs(res)
    return res;
    # return base + 'hike' + hikeID;

def build_picture_path(base, hikeID, index, camNum):
    return '../capra-sample-data/' + base + '/hike' + str(hikeID) + '/' + str(index) + '_cam' + str(camNum) + '.jpg';
    # return base + 'hike' + str(hikeID) + '/' + str(index) + '_cam' + str(camNum) + '.jpg';

def start_transfer():
    # TODO: write query
    latest_master_hikeID = 1; ##
    latest_remote_hikeID = 3; ##
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

        # TODO: deploy rsync subprocess
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
                # TODO: make query and
                picCounter_cam1 += 1;
                #print("Cam1++; Cam1 total: {}".format(picCounter_cam1));
            # if (os.path.exists(build_picture_path(g.PATH_ON_PROJECTOR, currHike, picCounter_cam2, 2)):
            if (os.path.exists(build_picture_path("capra-storage", currHike, picCounter_cam2, 2))):
                # TODO: make query and
                picCounter_cam2 += 1;
                #print("Cam2++; Cam2 total: {}".format(picCounter_cam2));
            # if (os.path.exists(build_picture_path(g.PATH_ON_PROJECTOR, currHike, picCounter_cam3, 3)):
            if (os.path.exists(build_picture_path("capra-storage", currHike, picCounter_cam3, 3))):
                # TODO: make query and
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
        print("Hike{} Total: {}".format(currHike, picTotal));

        # 5-1. restore/re-transfer any missing picture
        # TODO: handle timeout; go through the folder again and re-transfer missing file
        # >> maybe add a dummy black photo to replace the missing file
        # if (rsync_status != 0 or timeout is True or picTotal != checkSum):


        # reset variables before the next iteration
        hikeCounter += 1;


# ==================================================================
start_transfer();
