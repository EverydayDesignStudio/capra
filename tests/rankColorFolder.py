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
from colormath.color_objects import HSVColor, LabColor
from colormath.color_conversions import convert_color
from colormath.color_diff import delta_e_cie2000


####################################################
### TODO: Congifure these variables

# DATAPATH = '/Users/myoo/Development/capra_data/_sample/hike1_test/'
DATAPATH = '/Users/myoo/Dropbox/Everyday Design Studio/A Projects/100 Ongoing/Capra/capra-storage/capra-storage-july/hike33/'
CLUSTERS = 4        # assumes X number of dominant colors in a pictures

# If you want to group rows together (e.g. 0_cam1, 0_cam2, 0_cam3 as one row), set this to True.
# Enabling this will concatenate 3 pictures together when analyzing dominant colors.
COMBINE_ROWS = True

# When grouping rows, specify starting and ending index (e.g. 3_camX ~ 17_camX ==> 3, 17)
INDEX_START = 1
INDEX_END = 1726

####################################################

FILENAME = "[!\.]*_cam[1-3].jpg"
FOLDERNAME = DATAPATH.rsplit('/', 2)[1]
# sample dimensions: (100, 60), (160, 95), (320, 189), (720, 427)
DIMX = 100
DIMY = 60
TOTAL = DIMX * DIMY

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


def generatePics(colors_sorted, name: str):
    # Generates the picture
    height = 50
    img = np.zeros((height, len(colors_sorted), 3), np.uint8)  # (0,255)

    for x in range(0, len(colors_sorted)-1):
        c = [colors_sorted[x][0] * 255, colors_sorted[x][1] * 255, colors_sorted[x][2] * 255]
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


def sort_by_colors(dic):

    tmpList = []
    for p_name, p_info in dic.items():
        res = p_info["most_dominant_color_rgb"]
        res.insert(0, p_name)
        tmpList.append(res)

    # Sort the colors by hue & luminosity
    repetition = 8
    tmpList.sort(key=lambda rgb: sortby_hue_luminosity(rgb[1], rgb[2], rgb[3], repetition))

    print('\n\n\n')

    # Generates the image
    colors = []
    count = 1
    print("<Rank> - <FileName>")
    for i in range(len(tmpList)):
        tmp = tmpList[i]
        print("{} - {}".format(count, tmp.pop(0)))
        colors.append(tmp)
        count += 1

    adds = ""
    if (COMBINE_ROWS):
        adds = "-rows"
    generatePics(colors, FOLDERNAME + "-{}x{}".format(DIMX, DIMY) + '-8' + adds)

def get_multiple_dominant_colors(image1, image2=None, image3=None, image_processing_size=None):
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

    if (image2 is not None and image3 is not None):
        print(image1)
        print(image2)
        print(image3)
        # read in image of interest
        bgr_image1 = cv2.imread(image1)
        bgr_image2 = cv2.imread(image2)
        bgr_image3 = cv2.imread(image3)
        # convert to HSV; this is a better representation of how we see color
        hsv_image1 = cv2.cvtColor(bgr_image1, cv2.COLOR_BGR2HSV)
        hsv_image2 = cv2.cvtColor(bgr_image2, cv2.COLOR_BGR2HSV)
        hsv_image3 = cv2.cvtColor(bgr_image3, cv2.COLOR_BGR2HSV)

        image1 = cv2.resize(hsv_image1, image_processing_size, interpolation=cv2.INTER_AREA)
        image2 = cv2.resize(hsv_image2, image_processing_size, interpolation=cv2.INTER_AREA)
        image3 = cv2.resize(hsv_image3, image_processing_size, interpolation=cv2.INTER_AREA)

        # reshape the image to be a list of pixels
        image1 = image1.reshape((image1.shape[0] * image1.shape[1], 3))
        image2 = image2.reshape((image2.shape[0] * image2.shape[1], 3))
        image3 = image3.reshape((image3.shape[0] * image3.shape[1], 3))

        image = np.concatenate((image1, image2, image3))

    else:
        # read in image of interest
        bgr_image1 = cv2.imread(image1)
        # convert to HSV; this is a better representation of how we see color
        hsv_image1 = cv2.cvtColor(bgr_image1, cv2.COLOR_BGR2HSV)

        image1 = cv2.resize(hsv_image1, image_processing_size, interpolation=cv2.INTER_AREA)

        # reshape the image to be a list of pixels
        image = image1.reshape((image1.shape[0] * image1.shape[1], 3))

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
        base = TOTAL
        if (COMBINE_ROWS):
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

    print(dominant_colors_hsv)
    print(dominant_colors_rgb)
    print(confidences)
    print('\n')

    return len(confidences), dominant_colors_hsv, dominant_colors_rgb, confidences


def main():
    orig_stdout = sys.stdout
    adds = ""
    if (COMBINE_ROWS):
        adds = "-rows"
    f = open(DATAPATH + "{}-{}x{}".format(FOLDERNAME, DIMX, DIMY) + '-8' + adds + '_output.txt', 'w')
    sys.stdout = f

    k = count_files_in_directory(DATAPATH)
    pics = {}

    if (COMBINE_ROWS):
        if (k % 3 != 0):
            print("Please make sure every row has exactly 3 pictures")
            exit()

        if (INDEX_START > INDEX_END):
            print("Invalid indices")
            exit()

        for i in range(INDEX_START, INDEX_END+1, 1):
            filePath1 = DATAPATH + "{}_cam1.jpg".format(i)
            filePath2 = DATAPATH + "{}_cam2.jpg".format(i)
            filePath3 = DATAPATH + "{}_cam3.jpg".format(i)
            if (not os.path.exists(filePath1) or not os.path.exists(filePath2) or not os.path.exists(filePath3)):
                continue

            fileName = "{}_camN".format(i)
            color_size, colors_hsv, colors_rgb, confidences = get_multiple_dominant_colors(image1=filePath1, image2=filePath2, image3=filePath3, image_processing_size=(DIMX, DIMY))

            res = {
                "picture_name": fileName,
                "color_size": color_size,
                "colors_hsv": colors_hsv,
                "colors_rgb": colors_rgb,
                "confidences": confidences,
                "most_dominant_color_hsv": colors_hsv[0],
                "most_dominant_color_rgb": colors_rgb[0]
            }

            pics[fileName] = res

        sort_by_colors(pics)

    else:
        for file in os.scandir(DATAPATH):
            filePath = file.path
            fileName = filePath.rpartition('/')[2]
            if (filePath.endswith(".jpg")):
                print(fileName)
                color_size, colors_hsv, colors_rgb, confidences = get_multiple_dominant_colors(image1=filePath, image_processing_size=(DIMX, DIMY))

                res = {
                    "picture_name": fileName,
                    "color_size": color_size,
                    "colors_hsv": colors_hsv,
                    "colors_rgb": colors_rgb,
                    "confidences": confidences,
                    "most_dominant_color_hsv": colors_hsv[0],
                    "most_dominant_color_rgb": colors_rgb[0]
                }

                pics[fileName] = res

        sort_by_colors(pics)


    sys.stdout = orig_stdout
    f.close()

if __name__ == "__main__":
    main()
