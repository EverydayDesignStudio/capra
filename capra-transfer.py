import globals as g
import os, os.path, datetime, sqlite3, subprocess
from pathlib import Path
from classes.capra_data_types import Picture, Hike
from classes.sql_controller import SQLController
from classes.sql_statements import SQLStatements

rsync_status = None;
cDBController = None;
pDBController = None;
retry = 0;
RETRY_MAX = 5;

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

    # this will be a local db, copied from camera
    cDBController = SQLController(database=CAMERA_DB)
    # master projector db
    pDBController = SQLController(database=PROJECTOR_DB)

# 2. copy remote DB
def update_transfer_animation_db():
    #if date.today() != date.fromtimestamp(Path(g.PATH_TRANSFER_ANIMATION_DB).stat().st_mtime):
    transfer_from_camera(g.PATH_CAMERA_DB, g.PATH_TRANSFER_ANIMATION_DB);

def count_files_in_directory(path):
    if (not os.path.exists(path)):
        return 0;
    else:
        return len([name for name in os.listdir(path) if os.path.isfile(os.path.join(path, name))]);

def build_hike_path(base, hikeID=None, makeNew=False):
    res = "";
    if (hikeID > 0):
        res = PATH + base + '/hike' + str(hikeID);
    else:
        # put -1 for hikeID to build a path for the upper directory
        # i.e.) "/capra-storage" for rsync destination
        res = PATH + base;
    if makeNew and not os.path.exists(res):
        os.makedirs(res)
    return res;
    # return base + 'hike' + hikeID;

def build_picture_path(base, hikeID, index, camNum):
    return PATH + base + '/hike' + str(hikeID) + '/' + str(index) + '_cam' + str(camNum) + '.jpg';
    # return base + 'hike' + str(hikeID) + '/' + str(index) + '_cam' + str(camNum) + '.jpg';

def start_transfer():
    global cDBController, pDBController, rsync_status, retry

    latest_master_hikeID = pDBController.get_last_hike_id();
    latest_remote_hikeID = cDBController.get_last_hike_id();
    numNewHikes = latest_remote_hikeID - latest_master_hikeID;
    hikeCounter = 0;
    checkSum = 0;

    # 3. determine how many hikes should be transferred
    while hikeCounter <= numNewHikes:
        currHike = latest_master_hikeID + hikeCounter;
        if (currHike == 0):
            # skip the validity check for newly created databases
            hikeCounter += 1;
            continue;

        # C-1.  validity check
        #   ** For photos with invalid data, we won't bother restoring/fixing incorrect metatdata.
        #      The row (all 3 photos) will be dropped as a whole
        validRows = cDBController.get_valid_photos_in_given_hike(currHike);
        checkSum = 3 * len(validRows)
        numfiles = count_files_in_directory(build_hike_path("capra-storage", currHike));
        print(len(validRows));
        print("hike2: " + str(numfiles));

        # skip if a hike is fully transferred already
        if (checkSum == numfiles):
            hikeCounter += 1;
            continue;

        avgAlt = 0;
        avgCol = 0;

        # C-2.  once all data is confirmed and valid, deploy rsync for 3 photos
        for row in validRows:
            # (time, alt, color, hike, index, cam1, cam2, cam3, date_created, date_updated)

            src = row[5][:-5] + "*" +  row[5][-4:]      # "/home/pi/capra-storage/hike1/1_cam2.jpg" --> "/home/pi/capra-storage/hike1/1_cam*.jpg"
            dest = build_hike_path("capra-storage", currHike, True)

            avgAlt += int(row[1])

            # deploy rsync and add database row to the master db
            rsync_status = subprocess.call(['rsync', '--update', '-av', src, dest]);

            # when rsync is over,
            if (rsync_status == 0):
                print("row {} transfer completed".format(row[4]))
                # TODO: do postprocessing
                doPostProcessing = 0;
                # TODO: upsert a row to picture table in the master db
                #pDBController.

        # compare checksum
        numfiles = count_files_in_directory(build_hike_path("capra-storage", currHike));
        print("hike2: " + str(numfiles));
        if (checkSum == numfiles):
            # TODO: make a row for hike table with postprocessed values
            # (hike_id, avgAlt, avgCol, start_time, end_time, numpics, path, date_created, date_updated)
            t = 0;


            # G.    clean up partial files and proceed to next hike
            hikeCounter += 1;

        elif (retry < RETRY_MAX):
            retry += 1;
            continue;

        # what do we do here..?
        else:
            exit();

        exit();



# ==================================================================
getDBControllers();
# check if camera DB in projector is outdated
# update_transfer_animation_db();
start_transfer();
