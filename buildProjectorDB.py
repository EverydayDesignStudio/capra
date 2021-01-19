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
from classes.sql_controller import SQLController
from classes.sql_statements import SQLStatements
from classes.kmeans import get_dominant_color_1D
from colormath.color_objects import HSVColor, LabColor
from colormath.color_conversions import convert_color
from colormath.color_diff import delta_e_cie2000


####################################################
### TODO: Congifure these variables

# hike6 - 903
# hike5 - 1389
# hike3 - 2157

# hike29 - 2288

# hike31 - 560
# hike33 - 1726
# hike10 - 3561

# When grouping rows, specify starting and ending index (e.g. 3_camX ~ 17_camX ==> 3, 17)
INDEX_START = 1100
INDEX_END = 1200
# INDEX_END = 20
currHike = 29

dummyGlobalColorRank = -1
dummyGlobalAltRank = -1

####################################################

DROPBOX = "/Users/myoo/Dropbox/"
BASEPATH = "Everyday Design Studio/A Projects/100 Ongoing/Capra/capra-storage/capra-storage-july/"

# DATAPATH = '/Users/myoo/Development/capra_data/_sample/hike00/'
DATAPATH = DROPBOX + BASEPATH + "hike10/"
# DB_SOURCE = DROPBOX + BASEPATH + "capra_projector_dec2020_min_hike10_src.db"
DB_SOURCE = DROPBOX + BASEPATH + "capra_projector_dec2020_min_AllHikes.db"
DB_DEST = DROPBOX + BASEPATH + "capra_projector_dec2020_min_hike29_dest.db"

####################################################

BASEHIKEPATH = "/media/pi/capra-hd/hike" + str(currHike) + "/"


dbSRCController = None
dbDESTController = None

ROWCOUNT = INDEX_END - INDEX_START + 1

CLUSTERS = 4        # assumes X number of dominant colors in a pictures

FILENAME = "[!\.]*_cam[1-3].jpg"
FOLDERNAME = DATAPATH.rsplit('/', 2)[1]
# sample dimensions: (100, 60), (160, 95), (320, 189), (720, 427)
DIMX = 100
DIMY = 60
TOTAL = DIMX * DIMY

res_red = []
res_green = []
res_blue = []


# make db connections
def getDBControllers():
    global dbSRCController, dbDESTController

    dbSRCController = SQLController(database=DB_SOURCE)

    # TODO: if dest does not exist, create a new DB
    dbDESTController = SQLController(database=DB_DEST)


def count_files_in_directory(path):
    if (not os.path.exists(path)):
        return 0
    else:
        return len(glob.glob(path + FILENAME))




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
#        c = [colors_sorted[x][0] * 255, colors_sorted[x][1] * 255, colors_sorted[x][2] * 255]
        c = [colors_sorted[x][0], colors_sorted[x][1], colors_sorted[x][2]]
        img[:, x] = c

    cv2.imwrite(DATAPATH + '{n}.png'.format(n=name), img)


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


def sort_by_alts(commits):
    tmpList = []
    for p_name, p_info in commits.items():
        res = []
        res.append(p_info[7])   # index_in_hike
        res.append(p_info[8])   # altitude
        tmpList.append(res)

    tmpList.sort(key=lambda x: x[1])

    rankList = ROWCOUNT*[None]
    count = 1
    for i in range(len(tmpList)):
        tmp = tmpList[i]
        rankList[tmp[0]-INDEX_START] = count
        count += 1

    # print("<tmpList>")
    # print(tmpList)
    # print("<altList>")
    # print(rankList)

    return rankList

def sort_by_colors(dic):
    tmpList = []
    for p_name, p_info in dic.items():
        res = p_info["most_dominant_color_rgb"]
        res.insert(0, p_name)
        res.append(p_info["index"])
        tmpList.append(res)

    # Sort the colors by hue & luminosity
    repetition = 8
    tmpList.sort(key=lambda rgb: sortby_hue_luminosity(rgb[1], rgb[2], rgb[3], repetition))

    # Generates the image
    rankList = ROWCOUNT*[None]
    count = 1
    for i in range(len(tmpList)):
        tmp = tmpList[i]
        rankList[tmp[4]-INDEX_START] = count
        count += 1

    # print("\n<COLOR RANK> - {}".format(len(rankList)))
    # for i in range(len(rankList)):
    #     res = "{} - {}".format(i, rankList[i])
    #     if (rankList[i] == None):
    #         continue
    #     print(rankList[i])


    ## TEST - generate color spectrum based on the color rank
    colorCount = 1
    colorSpectrumRGB_test = []
    for i in range(len(tmpList)):
        tmp = tmpList[i]
        tmp.pop(4)
        tmp.pop(0)
        colorSpectrumRGB_test.append(tmp)
        colorCount += 1

    generatePics(colorSpectrumRGB_test, FOLDERNAME + "-{}x{}".format(DIMX, DIMY) + "-colorSpectrum_dec2020")

    return rankList


def dominantColorWrapper(currHike, row, image1, image2, image3=None, image_processing_size=None):
    ### TODO: change this index to row[3] if cameraDB is used
    index_in_hike = row[8]

    color_size, colors_hsv, colors_rgb, confidences = get_multiple_dominant_colors(image1=image1, image2=image2, image3=image3, image_processing_size=(DIMX, DIMY))

    pic = {
        "index": index_in_hike,
        "color_size": color_size,
        "colors_hsv": colors_hsv,
        "colors_rgb": colors_rgb,
        "confidences": confidences,
        "most_dominant_color_hsv": colors_hsv[0],
        "most_dominant_color_rgb": colors_rgb[0]
    }

    picDatetime = datetime.datetime.fromtimestamp(row[1])

    #     time,
    #     year, month, day, minute, dayofweek,
    #     hike, index_in_hike, altitude, altrank_hike, altrank_global, altrank_global_h,             # TODO: implement altitude ranks, index 9, 10, 11
    #     color_hsv, color_rgb, colrank_value, colrank_hike, colrank_global, color_rank_global_h,    # TODO: implement color ranks, index 15, 16, 17
    #     colors_count, colors_rgb, colors_conf,
    #     camera1, camera2, camera3, camera_landscape

    # ** 0 is monday in dayofweek
    # ** camera_landscape points to the path to cam2 pic
    ### TODO: change this index to row[0] and row[1] if cameraDB is used
    commit = [row[1],
                picDatetime.year, picDatetime.month, picDatetime.day, picDatetime.hour * 60 + picDatetime.minute, picDatetime.weekday(),
                currHike, index_in_hike, row[9], -1, -1, -1,
                ",".join(map(str, colors_hsv[0])), ",".join(map(str, colors_rgb[0])), -1, -1, -1, -1,
                color_size, formatColors(colors_rgb), ",".join(map(str, confidences)),
                row[22], row[23], row[24], row[23][:-4] + "f" + row[23][-4:]]

    # print(commit)

    return pic, commit, colors_hsv[0]


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


def main():
    global dbSRCController, dbDESTController, res_red, res_green, res_blue, dummyGlobalColorRank, dummyGlobalAltRank

    getDBControllers()

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

    # for colors
    domColorsHike_hsv = []

    # k = count_files_in_directory(DATAPATH)
    # for color/height ranks
    pics = {}
    commits = {}

    # if (k % 3 != 0):
    #     print("Please make sure every row has exactly 3 pictures")
    #     exit()

    if (INDEX_START > INDEX_END or INDEX_START < 0):
        print("Invalid indices")
        exit()

    count = 0
    upperBound = max(numValidRows, INDEX_END)
    while (count < upperBound):
        if (count < INDEX_START or count > INDEX_END):
            count += 1
            continue

        for index_in_hike in range(INDEX_START, INDEX_END+1, 1):
            # row = validRows[i]
            row = dbSRCController.get_hikerow_by_index(currHike, index_in_hike)

            if (row is None):
                count += 1
                continue

            if (count % 200 == 0):
                print("### Checkpoint at {}".format(count))
            print(count)
            print(row)

            ### TODO: change this index to row[0] if cameraDB is used
            # update timestamps
            if (row[1] < startTime):
                startTime = row[1]
            if (row[1] > endTime):
                endTime = row[1]

            ### TODO: change this index to row[1] if cameraDB is used
            avgAlt += int(row[9])

            filePath1 = DATAPATH + "{}_cam1.jpg".format(index_in_hike)
            filePath2 = DATAPATH + "{}_cam2.jpg".format(index_in_hike)
            filePath3 = DATAPATH + "{}_cam3.jpg".format(index_in_hike)
            # if (not os.path.exists(filePath1) or not os.path.exists(filePath2) or not os.path.exists(filePath3)):
            if (not os.path.exists(filePath1) or not os.path.exists(filePath2)):
                continue


            # TODO: rotate and resize, copy those to the dest folder
            # img = None
            # img_res = None
            # # resize and rotate for newly added pictures
            # #    1. make a copy of pic2 as pic2'f'
            # if (not os.path.exists(picPathCam2f)):
            #     img = Image.open(picPathCam2)
            #     img_res = img.copy()
            #     img_res.save(picPathCam2f)
            #
            # #    2. resize to 427x720 and rotate 90 deg
            # ## TODO: refine color - saturation --> talk with Sam
            # if (isNew):
            #     img = Image.open(picPathCam1)
            #     img_res = img.resize((720, 427), Image.ANTIALIAS).rotate(270, expand=True)
            #     img_res.save(picPathCam1)
            #
            #     img = Image.open(picPathCam2)
            #     img_res = img.resize((720, 427), Image.ANTIALIAS).rotate(270, expand=True)
            #     img_res.save(picPathCam2)
            #
            #     if (os.path.exists(picPathCam3)):
            #         img = Image.open(picPathCam3)
            #         img_res = img.resize((720, 427), Image.ANTIALIAS).rotate(270, expand=True)
            #         img_res.save(picPathCam3)
            #     else:
            #         img = Image.open(WHITE_IMAGE)
            #         img_res = img.copy().rotate(90, expand=True)
            #         img_res.save(picPathCam3)


            fileName = "{}_camN".format(index_in_hike)

            if (not os.path.exists(filePath3)):
                filePath3 = None
            # color_size, colors_hsv, colors_rgb, confidences = get_multiple_dominant_colors(image1=filePath1, image2=filePath2, image3=filePath3, image_processing_size=(DIMX, DIMY))
            pic, commit, domCol_hsv = dominantColorWrapper(currHike, row, filePath1, filePath2, image3=filePath3, image_processing_size=(DIMX, DIMY))

            # pic = {
            #     "picture_name": fileName,
            #     "index": i,
            #     "color_size": color_size,
            #     "colors_hsv": colors_hsv,
            #     "colors_rgb": colors_rgb,
            #     "confidences": confidences,
            #     "most_dominant_color_hsv": colors_hsv[0],
            #     "most_dominant_color_rgb": colors_rgb[0]
            # }
            #
            pics[fileName] = pic
            commits[fileName] = commit
            domColorsHike_hsv.append(domCol_hsv)

            count += 1

        # print("<R,G,B>")
        # for i in range(len(res_red)):
        #     ret = "{},{},{}".format(res_red[i], res_green[i], res_blue[i])
        #     print(ret)


        # attach color ranking within the current hike
        # then, upsert rows
        colRankList = sort_by_colors(pics)
        altRankList = sort_by_alts(commits.copy())
        # TODO: avoid incremental check
        for index_in_hike in range(INDEX_START, INDEX_END+1, 1):
            fileName = "{}_camN".format(index_in_hike)

            commits[fileName][9] = altRankList[index_in_hike-INDEX_START]
            commits[fileName][14] = colRankList[index_in_hike-INDEX_START]
            commits[fileName][10] = dummyGlobalAltRank
            commits[fileName][15] = dummyGlobalColorRank

            # TODO: assign better dummy values
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

        #     hike_id, avg_altitude, avg_altitude_rank
        #     start_time, start_year, start_month, start_day, start_minute, start_dayofweek,
        #     end_time, end_year, end_month, end_day, end_minute, end_dayofweek,
        #     color_hsv, color_rgb, color_rank_value, color_rank,               # TODO: calculate color rank
        #     pictures, path

        # TODO: determine global hike color rank

        dbDESTController.upsert_hike(currHike, avgAlt, -currHike,
                                        startTime, hikeStartDatetime.year, hikeStartDatetime.month, hikeStartDatetime.day, hikeStartDatetime.hour * 60 + hikeStartDatetime.minute, hikeStartDatetime.weekday(),
                                        endTime, hikeEndDatetime.year, hikeEndDatetime.month, hikeEndDatetime.day, hikeEndDatetime.hour * 60 + hikeEndDatetime.minute, hikeEndDatetime.weekday(),
                                        ",".join(map(str, domColorHike_hsv)), ",".join(map(str, domColorHike_rgb)), -1, -currHike,
                                        numValidRows, BASEHIKEPATH)

        print("## Count: {} rows processed".format(count-1))

        # sys.stdout = orig_stdout
        # f.close()

if __name__ == "__main__":
    main()
