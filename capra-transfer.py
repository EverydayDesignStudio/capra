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

rsync_status = None;
cur_masterDB = None;
cur_remoteDB = None;

def getDBCursor(dbPath):
    conn = sqlite3.connect(dbPath);
    cur = conn.cursor()
    return cur;

def transfer_from_camera(from, to):
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

def build_hike_path(base, hikeID):
    return 'C:\\Users\\Minyoung Yoo\\Dropbox\\_SFU\\7. RA\\capra-sample-data\\capra-storage' + 'hike' + hikeID;
    # return base + 'hike' + hikeID;

def build_picture_path(base, hikeID, index, camNum):
    return 'C:\\Users\\Minyoung Yoo\\Dropbox\\_SFU\\7. RA\\capra-sample-data\\capra-storage' + 'hike' + hikeID
    return base + 'hike' + hikeID + '/' + index + '_cam' + camNum + '.jpg';

def start_transfer():
    # TODO: write query
    latest_master_hikeID = 0;
    latest_remote_hikeID = 0;
    numNewHikes = latest_remote_hikeID - latest_master_hikeID;
    hikeCounter = 1;
    checkSum = 0;

    # 3. determine how many hikes should be transferred
    while hikeCounter <= numNewHikes:
        # TODO: write this query; SELECT pictures FROM hikes WHERE hike_id = (latest_master_hikeID + hikeCounter);
        checkSum = getNumCountFromHike;
        currHike = latest_master_hikeID + hikeCounter;

        # TODO: deploy rsync subprocess
        rsync_status = deploy_rsync_subprocess;

        # 4. while a hike is being transferred, find newly added file and write a row to the master DB
        # 5. once a hike is fully transferred, compare the checksum
        prevPicTotal = 0;
        picCounter_cam1 = 0;
        picCounter_cam2 = 0;
        picCounter_cam3 = 0;
        picTotal = 0;
        while (rsync_status is None and os.path.exists(build_hike_path(g.PATH_ON_PROJECTOR, currHike)) and picTotal < checkSum):
            if (os.path.exists(build_picture_path(g.PATH_ON_PROJECTOR, currHike, picCounter_cam1, 1)):
                # TODO: make query and
                picCounter_cam1 += 1;
            if (os.path.exists(build_picture_path(g.PATH_ON_PROJECTOR, currHike, picCounter_cam2, 2)):
                # TODO: make query and
                picCounter_cam2 += 1;
            if (os.path.exists(build_picture_path(g.PATH_ON_PROJECTOR, currHike, picCounter_cam3, 3)):
                # TODO: make query and
                picCounter_cam3 += 1;

            # TODO: set timeout to be.. 5 min?
            if (set_timeout_flag):
                abort_rsync_subprocess
                break;

            if (prevPicTotal != picTotal):
                prevPicTotal = picTotal;
                picTotal = picCounter_cam1 + picCounter_cam2 + picCounter_cam3;

        # 5-1. restore/re-transfer any missing picture
        # TODO: handle timeout; go through the folder again and re-transfer missing file
        if (rsync_status != 0 or timeout is True or picTotal != checkSum):


        # reset variables before the next iteration
        hikeCounter += 1;


# ==================================================================
start_transfer();
