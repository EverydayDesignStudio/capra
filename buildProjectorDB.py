import colorsys
from sklearn.cluster import KMeans  # pip install -U scikit-learn
from collections import Counter
import cv2  # pip install opencv-python : for resizing image
import math
import numpy as np
import random
import time
import os
import glob
import sys
import sqlite3
import datetime
from operator import itemgetter
from PIL import ImageTk, Image                      # Pillow image functions
from classes.sql_controller import SQLController
from classes.sql_statements import SQLStatements
from classes.kmeans import get_dominant_color_1D
from colormath.color_objects import HSVColor, LabColor
from colormath.color_conversions import convert_color
from colormath.color_diff import delta_e_cie2000

####################################################

currHike = -1
globalCounter_h = 0
dummyGlobalColorRank = -1
dummyGlobalAltRank = -1
dummyGlobalCounter = 0

DROPBOX = "/Users/myoo/Dropbox/"

BASEPATH_SRC = "Everyday Design Studio/A Projects/100 Ongoing/Capra/capra-storage/capra-storage-july/"
BASEPATH_DEST = "Everyday Design Studio/A Projects/100 Ongoing/Capra/capra-storage/capra-storage-min-transfer/"

# TODO: set DB accordingly
src_db_name = "capra_projector_jan2021_min_AllHikes.db"
dest_db_name = "capra_projector_jan2021_min_test.db"

####################################################

WHITE_IMAGE = DROPBOX + BASEPATH_DEST + "white.jpg"

srcPath = ""
destPath = ""
SRCDBPATH = DROPBOX + BASEPATH_SRC + src_db_name
DESTDBPATH = DROPBOX + BASEPATH_DEST + dest_db_name

dbSRCController = None
dbDESTController = None

COLOR_HSV_INDEX = -1    # used in the sortColor helper function

NEW_DATA = False

CLUSTERS = 4        # assumes X number of dominant colors in a pictures
REPETITION = 8

FILENAME = "[!\.]*_cam[1-3].jpg"
FILENAME_FULLSIZE = "[!\.]*_cam2f.jpg"
# sample dimensions: (100, 60), (160, 95), (320, 189), (720, 427)
DIMX = 100
DIMY = 60
TOTAL = DIMX * DIMY

res_red = []
res_green = []
res_blue = []


def timenow():
    return str(datetime.datetime.now()).split('.')[0]


# make db connections
def getDBControllers():
    global dbSRCController, dbDESTController

    # TODO: create DB if not exist

    dbSRCController = SQLController(database=SRCDBPATH)

    # TODO: if dest does not exist, create a new DB
    dbDESTController = SQLController(database=DESTDBPATH)


def count_files_in_directory(path, pattern):
    if (not os.path.exists(path)):
        return 0
    else:
        return len(glob.glob(path + pattern))


def build_hike_path(path, hikeID, makeNew=False):
    res = path + 'hike' + str(hikeID) + '/'
    if makeNew and not os.path.exists(res):
        os.makedirs(res, mode=0o755)
    return res


# (h [0-180], s[1-255], v[1-255])
# returns a list: [r, b, g]
def hsvToRgb(h, s, v):
    color_rgb = colorsys.hsv_to_rgb(h/180., s/255., v/255.)
    ret = list(map(lambda a : round(a*255), list(color_rgb)))
    return ret

def formatColors(colors):
    res = ""
    for color in colors:
        res += ",".join(map(str, color)) + "|"
    return res[:-1]

def roundToHundredth(lst):
    for i in range(len(lst)):
        lst[i] = round(float(lst[i]), 2)
    return lst


def generatePics(colors_sorted, name: str):
    # Generates the picture
    height = 50
    img = np.zeros((height, len(colors_sorted), 3), np.uint8)  # (0,255)

    for x in range(0, len(colors_sorted)-1):
        c = [colors_sorted[x][0], colors_sorted[x][1], colors_sorted[x][2]]
        img[:, x] = c

    cv2.imwrite(destPath + '{n}.png'.format(n=name), img)


def sortby_hue_luminosity(r, g, b, repetitions=1):
    lum = math.sqrt(0.241 * r + 0.691 * g + 0.068 * b)
    h, s, v = colorsys.rgb_to_hsv(r, g, b)

    h2 = int(h * repetitions)
    # h2 = h * repetitions
    # lum2 = int(lum * repetitions)
    # lum = int(lum * repetitions)
    v2 = int(v * repetitions)
    # v2 = v * repetitions

    # Connects the blacks and whites between each hue chunk
    # Every other (each even) color hue chunk, the values are flipped so the
    # white values are on the left and the black values are on the right
    if h2 % 2 == 1:
        v2 = repetitions - v2
        lum = repetitions - lum

    return (h2, lum)


def sort_by_alts(data, alt_index, index_in_hike):
    data.sort(key=itemgetter(alt_index, 0))  # 8 - altitude

    rankList = {}
    for i in range(len(data)):
        rankList[itemgetter(index_in_hike)(data[i])] = i+1   # 7 - index_in_hike

    return rankList

def splitColor(item):
    tmp = itemgetter(COLOR_HSV_INDEX)(item)      # 12 - color_hsv
    return sortby_hue_luminosity(int(tmp.split(",")[0]), int(tmp.split(",")[1]), int(tmp.split(",")[2]), REPETITION)

def sort_by_colors(data, color_index, index_in_hike, output=True):
    global COLOR_HSV_INDEX
    # key function for sort() only accepts 1 argument, so need to explicitly set additional variable as global
    COLOR_HSV_INDEX = color_index

    # Sort the colors by hue & luminosity
    data.sort(key=splitColor)

    rankList = {}
    for i in range(len(data)):
        rankList[itemgetter(index_in_hike)(data[i])] = i+1   # 7 - index_in_hike

    if (output):
        # generate a color spectrum based on the color rank
        colorCount = 1
        colorSpectrumRGB_test = []
        for i in range(len(data)):
            tmp = data[i][color_index]    # 12 - color_hsv
            colorSpectrumRGB_test.append((tmp.split(",")[0], tmp.split(",")[1], tmp.split(",")[2]))
            colorCount += 1

        generatePics(colorSpectrumRGB_test, "hike{}-{}x{}".format(currHike, DIMX, DIMY) + "-colorSpectrum_jan2021")

    return rankList


def dominantColorWrapper(currHike, row, image1, image2, image3=None, image_processing_size=None):
    global dummyGlobalCounter

    ### TODO: change this index to row[3] if cameraDB is used
    index_in_hike = row[8]

    color_size, colors_hsv, colors_rgb, confidences = get_multiple_dominant_colors(image1=image1, image2=image2, image3=image3, image_processing_size=(DIMX, DIMY))

    picDatetime = datetime.datetime.fromtimestamp(row[1])

    #     TIME,
    #     year, month, day, minute, dayofweek,
    #     hike, index_in_hike, altitude, altrank_hike, ALTRANK_GLOBAL, ALTRANK_GLOBAL_H,             # TODO: implement altitude ranks, index 9, 10, 11
    #     color_hsv, color_rgb, color_rank_value, color_rank_hike, COLOR_RANK_GLOBAL, COLOR_RANK_GLOBAL_H,    # TODO: implement color ranks, index 15, 16, 17
    #     colors_count, colors_rgb, colors_conf,
    #     camera1, camera2, camera3, camera_landscape

    # ** 0 is monday in dayofweek
    # ** camera_landscape points to the path to cam2
    ### TODO: change this index to row[0] and row[1] if cameraDB is used
    commit = [row[1],
                picDatetime.year, picDatetime.month, picDatetime.day, picDatetime.hour * 60 + picDatetime.minute, picDatetime.weekday(),
                currHike, index_in_hike, row[9], -1, -1, dummyGlobalCounter,
                ",".join(map(str, colors_hsv[0])), ",".join(map(str, colors_rgb[0])), -1, -1, -1, dummyGlobalCounter,
                color_size, formatColors(colors_rgb), ",".join(map(str, confidences)),
                row[22], row[23], row[24], row[23][:-4] + "f" + row[23][-4:]]

    # if (index_in_hike >= 417 and index_in_hike <= 430):
    #     print("# " + str(index_in_hike))
    #     print(commit)

    return commit, colors_hsv[0]


def get_multiple_dominant_colors(image1, image2, image3=None, image_processing_size=None):
    global res_red, res_green, res_blue

    """
    takes an image as input
    returns FOUR values
        i) number of colors
        ii) X number of dominant colors in HSV (int values)
        iii) X number of dominant colors in RGB (int values)
        iv) list of confidence values of the same size (2 decimal places)

    dominant colors are found by running k-means algorithm on the pixels of an image
    & returning the centroid of the largest cluster(s)

    processing time is sped up by working with a smaller image;
    this resizing can be done with the image_processing_size param
    which takes a tuple of image dims as input

    >>> get_multiple_dominant_colors(my_image, k, image_processing_size = (25, 25))
    4                                                               # 4 colors
    [[20, 79, 72], [33, 182, 38], [4, 5, 241], [139, 17, 178]]      # dominant colors in HSV
    [[72, 65, 50], [35, 38, 11], [241, 237, 236], [174, 166, 178]]  # dominant colors in RGB
    [268.7, 103.0, 73.79, 15.32]                                    # confidence values

    """

    k = CLUSTERS
    image = None

    # read in image of interest
    bgr_image1 = cv2.imread(image1)
    bgr_image2 = cv2.imread(image2)
    # convert to HSV; this is a better representation of how we see color
    hsv_image1 = cv2.cvtColor(bgr_image1, cv2.COLOR_BGR2HSV)
    hsv_image2 = cv2.cvtColor(bgr_image2, cv2.COLOR_BGR2HSV)

    image1 = cv2.resize(hsv_image1, image_processing_size, interpolation=cv2.INTER_AREA)
    image2 = cv2.resize(hsv_image2, image_processing_size, interpolation=cv2.INTER_AREA)

    # reshape the image to be a list of pixels
    image1 = image1.reshape((image1.shape[0] * image1.shape[1], 3))
    image2 = image2.reshape((image2.shape[0] * image2.shape[1], 3))

    if (image3 is not None):
        bgr_image3 = cv2.imread(image3)
        hsv_image3 = cv2.cvtColor(bgr_image3, cv2.COLOR_BGR2HSV)
        image3 = cv2.resize(hsv_image3, image_processing_size, interpolation=cv2.INTER_AREA)
        image3 = image3.reshape((image3.shape[0] * image3.shape[1], 3))

    if (image3 is None):
        image = np.concatenate((image1, image2))
    else:
        image = np.concatenate((image1, image2, image3))

    # else:
    #     # read in image of interest
    #     bgr_image1 = cv2.imread(image1)
    #     # convert to HSV; this is a better representation of how we see color
    #     hsv_image1 = cv2.cvtColor(bgr_image1, cv2.COLOR_BGR2HSV)
    #
    #     image1 = cv2.resize(hsv_image1, image_processing_size, interpolation=cv2.INTER_AREA)
    #
    #     # reshape the image to be a list of pixels
    #     image = image1.reshape((image1.shape[0] * image1.shape[1], 3))

    # cluster and assign labels to the pixels
    clt = KMeans(n_clusters=k)
    labels = clt.fit_predict(image)

    # count labels to find most popular
    label_counts = Counter(labels)

    # subset out k popular centroids
    topK = label_counts.most_common(k)
    dominant_colors_hsv = []
    confidences = []

    for label in topK:
        tmp = [ int(e) for e in clt.cluster_centers_[label[0]].tolist() ]
        dominant_colors_hsv.append(tmp)
        base = TOTAL*3
        confidences.append(round(label[1]/base, 2))

    # exclude colors that are similar to existing ones and with < 0.1 confidence value
    index_to_remove = set()

    for i in range(k):
        color_i = dominant_colors_hsv[i]
        color_i_hsv = HSVColor(color_i[0], color_i[1], color_i[2])
        color_i_lab = convert_color(color_i_hsv, LabColor)

        color_i_delta = []

        for j in range(i+1, k):
            color_j = dominant_colors_hsv[j]
            color_j_hsv = HSVColor(color_j[0], color_j[1], color_j[2])
            color_j_lab = convert_color(color_j_hsv, LabColor)

            delta_e = delta_e_cie2000(color_i_lab, color_j_lab);

            color_i_delta.append(delta_e)

        for j in range (len(color_i_delta)):
            if (confidences[i+j+1] < 0.2 and color_i_delta[j] < 40):
                index_to_remove.add(i+j+1)

    itr = list(index_to_remove)
    itr.sort(reverse = True)

    # trim insignificant colors
    for i in range(len(itr)):
        dominant_colors_hsv.pop(itr[i])
        confidences.pop(itr[i])

    # convert HSV to get RGB colors
    dominant_colors_rgb = []
    for color_hsv in dominant_colors_hsv:
        ret = hsvToRgb(color_hsv[0], color_hsv[1], color_hsv[2])
        dominant_colors_rgb.append(ret)

    res_red.append(str(dominant_colors_rgb[0][0]))
    res_green.append(str(dominant_colors_rgb[0][1]))
    res_blue.append(str(dominant_colors_rgb[0][2]))

    return len(confidences), dominant_colors_hsv, dominant_colors_rgb, confidences


def buildHike(currHike):
    global dbSRCController, dbDESTController
    global srcPath, destPath
    global res_red, res_green, res_blue
    global dummyGlobalColorRank, dummyGlobalAltRank, dummyGlobalCounter, globalCounter_h

    # Write to file
    # orig_stdout = sys.stdout
    # f = open(DATAPATH + "{}-{}x{}".format(FOLDERNAME, DIMX, DIMY) + '_output_list_RGB.txt', 'w')
    # sys.stdout = f

    validRows = dbSRCController.get_valid_photos_in_given_hike(currHike)
    numValidRows = len(validRows)

    print("NumValidRows: {}".format(numValidRows))

    avgAlt = 0
    startTime = 9999999999
    endTime = -1
    domColorsHike_hsv = []
    pics = {}
    commits = {}

    count = 0
    for index_in_hike in range(numValidRows):
        # row = validRows[index_in_hike]
        row = dbSRCController.get_hikerow_by_index(currHike, index_in_hike)

        picPathCam1_src = srcPath + "{}_cam1.jpg".format(index_in_hike)
        picPathCam2_src = srcPath + "{}_cam2.jpg".format(index_in_hike)
        picPathCam2f_src = srcPath + "{}_cam2f.jpg".format(index_in_hike)
        picPathCam3_src = srcPath + "{}_cam3.jpg".format(index_in_hike)

        picPathCam1_dest = destPath + "{}_cam1.jpg".format(index_in_hike)
        picPathCam2_dest = destPath + "{}_cam2.jpg".format(index_in_hike)
        picPathCam2f_dest = destPath + "{}_cam2f.jpg".format(index_in_hike)
        picPathCam3_dest = destPath + "{}_cam3.jpg".format(index_in_hike)

        if (row is None):
            continue

        # TODO: extract row data only when files are already transferred
        # if (os.path.exists(picPathCam1_dest) and
        #     os.path.exists(picPathCam2_dest) and
        #     os.path.exists(picPathCam2f_dest) and
        #     os.path.exists(picPathCam3_dest)):
        #     domColorsHike_hsv.append(dbDESTController.get_picture_dominant_color(row[0], 'hsv'))
        #     continue

        # if (not os.path.exists(picPathCam1) or not os.path.exists(picPathCam2) or not os.path.exists(picPathCam3)):
        if (not os.path.exists(picPathCam1_src) or not os.path.exists(picPathCam2_src)):
            continue

        if (index_in_hike % 200 == 0):
            print("### Checkpoint at {}".format(index_in_hike))

        ### TODO: change this index to row[0] if cameraDB is used
        # update timestamps
        if (row[1] < startTime):
            startTime = row[1]
        if (row[1] > endTime):
            endTime = row[1]

        ### TODO: change this index to row[1] if cameraDB is used
        avgAlt += int(row[9])

        # rotate and resize, copy those to the dest folder
        img = None
        img_res = None
        # resize and rotate for newly added pictures
        #    1. make a copy of pic2 as pic2f
        if (not os.path.exists(picPathCam2f_src)):
            img = Image.open(picPathCam2_src)
            img_res = img.copy()
            img_res.save(picPathCam2f_dest)

        #    2. resize to 427x720 and rotate 90 deg
        ## TODO: refine color - saturation --> talk with Sam
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


        fileName = "{}_camN".format(index_in_hike)

        if (not os.path.exists(picPathCam3_src)):
            picPathCam3_dest = None
        # color_size, colors_hsv, colors_rgb, confidences = get_multiple_dominant_colors(image1=picPathCam1_dest, image2=picPathCam2_dest, image3=picPathCam3_dest, image_processing_size=(DIMX, DIMY))
        commit, domCol_hsv = dominantColorWrapper(currHike, row, picPathCam1_dest, picPathCam2_dest, image3=picPathCam3_dest, image_processing_size=(DIMX, DIMY))

        commits[fileName] = commit
        domColorsHike_hsv.append(domCol_hsv)

        dummyGlobalCounter += 1
        count += 1

    ### Post-processing
    # attach color ranking within the current hike
    # then, upsert rows
    # colRankList = sort_by_colors(pics.copy())
    # altRankList = sort_by_alts(commits.copy())
    colRankList = sort_by_colors(list(commits.copy().values()), color_index=12, index_in_hike=7, output=True)
    altRankList = sort_by_alts(list(commits.copy().values()), alt_index=8, index_in_hike=7)

    for index_in_hike in range(numValidRows):
        fileName = "{}_camN".format(index_in_hike)

        if index_in_hike not in altRankList or index_in_hike not in colRankList:
            continue

        altrank = altRankList[index_in_hike]
        commits[fileName][9] = altrank
        commits[fileName][10] = dummyGlobalAltRank
        commits[fileName][11] = globalCounter_h + altrank

        colrank = colRankList[index_in_hike]
        commits[fileName][15] = colrank
        commits[fileName][16] = dummyGlobalColorRank
        commits[fileName][17] = globalCounter_h + colrank

#        print("[{}] altRank: {}, altRankG: {}, altRankG_h: {}, tcolRank: {}, colRankG: {}, colRankG_h: {}".format(index_in_hike, altrank, dummyGlobalAltRank, str(globalCounter_h + altrank), colrank, dummyGlobalColorRank, str(globalCounter_h + colrank)))

        dummyGlobalColorRank -= 1
        dummyGlobalAltRank -= 1

        # print(commits[fileName])

        commit = tuple(commits[fileName])
        dbDESTController.upsert_picture(*commit)

    # make a row for the hike table with postprocessed values
    avgAlt /= numValidRows
    domColorHike_hsv = []
    domColorHike_hsv = get_dominant_color_1D(domColorsHike_hsv, CLUSTERS)
    roundToHundredth(domColorHike_hsv)

    hikeStartDatetime = datetime.datetime.fromtimestamp(startTime)
    hikeEndDatetime = datetime.datetime.fromtimestamp(endTime)
    domColorHike_rgb = hsvToRgb(domColorHike_hsv[0], domColorHike_hsv[1], domColorHike_hsv[2])

    #     HIKE_ID, avg_altitude, AVG_ALTITUDE_RANK,
    #     START_TIME, start_year, start_month, start_day, start_minute, start_dayofweek,
    #     END_TIME, end_year, end_month, end_day, end_minute, end_dayofweek,
    #     color_hsv, color_rgb, color_rank_value, COLOR_RANK,               # TODO: calculate color rank
    #     pictures, PATH

    defaultHikePath = "/media/pi/capra-hd/hike" + str(currHike) + "/"

    dbDESTController.upsert_hike(currHike, avgAlt, -currHike,
                                    startTime, hikeStartDatetime.year, hikeStartDatetime.month, hikeStartDatetime.day, hikeStartDatetime.hour * 60 + hikeStartDatetime.minute, hikeStartDatetime.weekday(),
                                    endTime, hikeEndDatetime.year, hikeEndDatetime.month, hikeEndDatetime.day, hikeEndDatetime.hour * 60 + hikeEndDatetime.minute, hikeEndDatetime.weekday(),
                                    ",".join(map(str, domColorHike_hsv)), ",".join(map(str, domColorHike_rgb)), -1, -currHike,
                                    numValidRows, defaultHikePath)

    print("[{}] ## Hike {} done. {} rows processed".format(timenow(), currHike, count))


def compute_checksum(path, currHike):
    checkSum_transferred = count_files_in_directory(path, FILENAME)
    checkSum_rotated = count_files_in_directory(path, FILENAME_FULLSIZE)
    return checkSum_transferred, checkSum_rotated, checkSum_transferred + checkSum_rotated

def check_hike_postprocessing(currHike):
    hikeColor = dbDESTController.get_hike_average_color(currHike)
    return hikeColor is not None and hikeColor and not (hikeColor[0] < 0.001 and hikeColor[1] < 0.001 and hikeColor[2] < 0.001)


def main():
    global dbSRCController, dbDESTController, dummyGlobalColorRank, dummyGlobalAltRank, dummyGlobalCounter, globalCounter_h
    global srcPath, destPath
    global COLOR_HSV_INDEX

    # TODO: initialize DB if does not exist

    getDBControllers()

    latest_src_hikeID = dbSRCController.get_last_hike_id()
    latest_dest_hikeID = dbDESTController.get_last_hike_id()
    print("[{}] @@@ # hikes on from Source: {}".format(timenow(), str(latest_src_hikeID)))
    print("[{}] @@@ # hikes on at Dest: {}".format(timenow(), str(latest_dest_hikeID)))

    currHike = 1
    checkSum_transferred = 0
    checkSum_rotated = 0
    checkSum_total = 0

    dummyGlobalCounter = 1
    hikeTimer = time.time()

    while currHike <= latest_src_hikeID:

        srcPath = build_hike_path(DROPBOX + BASEPATH_SRC, currHike)
        destPath = build_hike_path(DROPBOX + BASEPATH_DEST, currHike, True)

        if (currHike > 2):
            break;

        currExpectedHikeSize = dbSRCController.get_size_of_hike(currHike)
        if (currExpectedHikeSize is None):
            currExpectedHikeSize = 0

        expectedCheckSumTotal = currExpectedHikeSize * 4
        checkSum_transferred, checkSum_rotated, checkSum_total = compute_checksum(destPath, currHike)

        # print("[{}] Hike {}: {} files expected, {} files exist".format(timenow(), str(currHike), str(expectedCheckSumTotal), str(checkSum_total)))

        # 1. skip empty hikes
        if (currExpectedHikeSize == 0):
            print("[{}] Hike {} is empty. Proceeding to the next hike...".format(timenow(), str(currHike)))
            currHike += 1
            continue

        else:
            NEW_DATA = True

            # 2. if a hike is fully transferred, resized and rotated, then skip the transfer for this hike
            # also check if DB is updated to post-processed values as well
            if (checkSum_transferred == currExpectedHikeSize * 3 and
                expectedCheckSumTotal == checkSum_total and
                check_hike_postprocessing(currHike)):

                print("[{}]     # Hike {} fully transferred. Proceeding to the next hike...".format(timenow(), str(currHike)))
                dummyGlobalCounter += currExpectedHikeSize

            else:
                hikeTimer = time.time()
                print("[{}] Processing Hike {}".format(timenow(), str(currHike)))
                # TODO: return proper values
                buildHike(currHike)

            currHike += 1
            globalCounter_h += currExpectedHikeSize

    ### At this point, all hikes are processed.

    # calculate global ranks for pictures, only when there is new data
    if (True or NEW_DATA):
        rankTimer = time.time()

        globalAltList = []
        globalColorList = []

        rows = dbDESTController.get_pictures_global_ranking_raw_data()
        for i in range(len(rows)):
            row = rows[i]
            globalAltList.append((row[0], row[1]))
            globalColorList.append((row[0], row[2]))

        globalAltList.sort(key=lambda data: data[1])

        # key function for sort() only accepts 1 argument, so need to explicitly set additional variable as global
        COLOR_HSV_INDEX = 1
        globalColorList.sort(key=splitColor)

        for i in range(len(globalAltList)):
            row = globalAltList[i]
            rank = i + 1
            dbDESTController.update_pictures_global_AltRank(row[0], rank)

        for i in range(len(globalColorList)):
            row = globalColorList[i]
            rank = i + 1
            dbDESTController.update_pictures_global_ColRank(row[0], rank)

        NEW_DATA = False


    print("--- global ranking took {} seconds".format(str(time.time() - rankTimer)))

    print("[{}] --- {} seconds ---".format(timenow(), str(time.time() - hikeTimer)))



if __name__ == "__main__":
    main()
