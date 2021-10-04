from sklearn.cluster import KMeans  # pip install -U scikit-learn
from collections import Counter
import numpy as np
import cv2  # pip install opencv-python : for resizing image
from pathlib import Path
import time
import globals as g
import colorsys
from colormath.color_objects import HSVColor, LabColor
from colormath.color_conversions import convert_color
from colormath.color_diff import delta_e_cie2000
g.init()

HIKEPATH = '../../capra-sample-data/CapraKMeans/hike4/'  # test
TOTAL = g.COLOR_DIMX * g.COLOR_DIMY
# CLUSTERS = 5    # 5 is chosen to be an optimal k
# DIMX = 160
# DIMY = 95
# OUTPUTPATH = HIKEPATH + "dominantColors_" + str(DIMX) + "x" + str(DIMY) + '_' + str(CLUSTERS) + ".txt"

# (h [0-180], s[1-255], v[1-255])
# returns a list: [r, b, g]
def hsvToRgb(h, s, v):
    color_rgb = colorsys.hsv_to_rgb(h/180., s/255., v/255.)
    ret = list(map(lambda a : round(a*255), list(color_rgb)))
    return ret


def get_dominant_color(image, k=4, image_processing_size=None):
    """
    takes an image as input
    returns the dominant color of the image as a list

    dominant color is found by running k means on the
    pixels & returning the centroid of the largest cluster

    processing time is sped up by working with a smaller image;
    this resizing can be done with the image_processing_size param
    which takes a tuple of image dims as input

    >>> get_dominant_color(my_image, k=4, image_processing_size = (25, 25))
    [56.2423442, 34.0834233, 70.1234123]
    """

    # resize image if new dims provided
    if image_processing_size is not None:
        image = cv2.resize(image, image_processing_size, interpolation=cv2.INTER_AREA)

    # reshape the image to be a list of pixels
    image = image.reshape((image.shape[0] * image.shape[1], 3))

    # cluster and assign labels to the pixels
    clt = KMeans(n_clusters=k)
    labels = clt.fit_predict(image)

    # count labels to find most popular
    label_counts = Counter(labels)

    # subset out most popular centroid
    dominant_color = clt.cluster_centers_[label_counts.most_common(1)[0][0]]

    return list(dominant_color)


def get_five_dominant_colors(image, k=4, image_processing_size=None):
    """
    takes an image as input
    returns two lists
        i) five dominant colors of the image as a list (int values)
        ii) list of confidence values of the same size (2 decimal places)

    dominant colors are found by running k means on the
    pixels & returning the centroid of the largest cluster

    processing time is sped up by working with a smaller image;
    this resizing can be done with the image_processing_size param
    which takes a tuple of image dims as input

    >>> get_five_dominant_colors(my_image, k=4, image_processing_size = (25, 25))
    [
        [0, 0, 254],
        [110, 37, 188],
        [101, 13, 241],
        [45, 26, 181],
        [85, 28, 133]
    ]                                       // five dominant colors in HSV format

    [0.84, 0.05, 0.05, 0.04, 0.02]          // confidence values

    """

    # resize image if new dims provided
    if image_processing_size is not None:
        image = cv2.resize(image, image_processing_size, interpolation=cv2.INTER_AREA)

    # reshape the image to be a list of pixels
    image = image.reshape((image.shape[0] * image.shape[1], 3))

    # cluster and assign labels to the pixels
    clt = KMeans(n_clusters=k)
    labels = clt.fit_predict(image)

    # count labels to find most popular
    label_counts = Counter(labels)

    # subset out 5 popular centroids
    top5 = label_counts.most_common(5)
    dominant_colors = []
    confidences = []
    for label in top5:
        tmp = [ int(e) for e in clt.cluster_centers_[label[0]].tolist() ]
        dominant_colors.append(tmp)
        confidences.append(round(label[1]/TOTAL, 2))

    return dominant_colors, confidences


def get_dominant_color_1D(ary, k):
    clt = KMeans(n_clusters=k)
    labels = clt.fit_predict(ary)

    # count labels to find most popular
    label_counts = Counter(labels)

    # subset out most popular centroid
    dominant_color = clt.cluster_centers_[label_counts.most_common(1)[0][0]]

    return list(dominant_color)


def get_dominant_colors_for_hike(hikeID):

    # TODO: may need to log this
    # startTime = time.time()

    # hikepath = g.PATH_ON_PROJECTOR + "hike" + str(hikeID)
    hikepath = "../capra-sample-data/capra-storage/" + "hike" + str(hikeID)
    pathlist = Path(hikepath).glob('*.jpg')
    img = ""
    res = []
    count = 0
    errCount = 0
    errPicNames = []
    for path in pathlist:
        # if (count < 1000):
        #     count += 1
        #     continue
        # if (count == 1500):
        #     break

        try:
            # because path is object not string
            img = str(path)
            imgName = img.rsplit('\\', 1)[1]

            # read in image of interest
            bgr_image = cv2.imread(img)
            # convert to HSV; this is a better representation of how we see color
            hsv_image = cv2.cvtColor(bgr_image, cv2.COLOR_BGR2HSV)

            # extract dominant color (in HSV)
            # (aka the centroid of the most popular k means cluster)
            dom_color_hsv = get_dominant_color(hsv_image, k=g.COLOR_CLUSTER, image_processing_size=(g.COLOR_DIMX, g.COLOR_DIMY))

            # temporarily create a pixel with HSV to extract RGB value
            tmp = np.full((1, 1, 3), dom_color_hsv, dtype='uint8')
            dom_color_rgb = cv2.cvtColor(tmp, cv2.COLOR_HSV2RGB)[0][0].tostring()

            # convert lists to string
            dom_color_hsv_str = ', '.join(map(str, dom_color_hsv))
            dom_color_rgb_str = ', '.join(map(str, dom_color_rgb))

            # All values are in *STRING*
            # [image_name, hue, saturation, value, red, green, blue]
            row = imgName + ', ' + dom_color_hsv_str + ', ' + dom_color_rgb_str
            res.append(row)

            count += 1
        except:
            count += 1
            errCount += 1
            errPicNames.append(imgName)
            continue

    # TODO: add errorPicNames to the log
    if (errCount > 0):
        print("### {} invalid photos in hike {}".format(errCount, hikeID))
        print(errPicNames)

    return res, count, errCount

    # TODO: may need to log this
    # endTime = time.time()
    # print("### {} photos analyzed.".format(str(count)))
    # print("### Time elapsed: {} seconds".format(endTime - startTime))


def get_dominant_colors_for_picture(picturePath):
    # Capra analyzes the color of the middle photo only
    res = ""
    try:
        # read in image of interest
        bgr_image = cv2.imread(picturePath)
        # convert to HSV; this is a better representation of how we see color
        hsv_image = cv2.cvtColor(bgr_image, cv2.COLOR_BGR2HSV)

        # extract dominant color (in HSV)
        # (aka the centroid of the most popular k means cluster)
        dom_color_hsv = get_dominant_color(hsv_image, k=g.COLOR_CLUSTER, image_processing_size=(g.COLOR_DIMX, g.COLOR_DIMY))

        # temporarily create a pixel with HSV to extract RGB value
        tmp = np.full((1, 1, 3), dom_color_hsv, dtype='uint8')
        dom_color_rgb = cv2.cvtColor(tmp, cv2.COLOR_HSV2RGB)[0][0].tostring()

        # convert lists to string
        dom_color_hsv_str = ', '.join(map(str, dom_color_hsv))
        dom_color_rgb_str = ', '.join(map(str, dom_color_rgb))

        # All values are in *STRING*
        # [image_name, hue, saturation, value, red, green, blue]
        res = dom_color_hsv_str + ', ' + dom_color_rgb_str
    except:
        return -1, ""

    return 0, res

def get_five_dominant_colors_for_picture(picturePath):
    # Capra analyzes the color of the middle photo only
    res = ""
    try:
        # read in image of interest
        bgr_image = cv2.imread(picturePath)
        # convert to HSV; this is a better representation of how we see color
        hsv_image = cv2.cvtColor(bgr_image, cv2.COLOR_BGR2HSV)

        # extract dominant color (in HSV)
        # (aka the centroid of the most popular k means cluster)
        dom_colors_hsv, conf_list= get_five_dominant_colors(hsv_image, k=g.COLOR_CLUSTER, image_processing_size=(g.COLOR_DIMX, g.COLOR_DIMY))

        res_rgb = []
        res_hsv = []
        for dom_color_hsv in dom_colors_hsv:
            # temporarily create a pixel with HSV to extract RGB value
            tmp = np.full((1, 1, 3), dom_color_hsv, dtype='uint8')
            dom_color_rgb = cv2.cvtColor(tmp, cv2.COLOR_HSV2RGB)[0][0].tostring()

            # convert lists to string
            dom_color_hsv_str = ', '.join(map(str, dom_color_hsv))
            dom_color_rgb_str = ', '.join(map(str, dom_color_rgb))

            res_hsv.append(dom_color_hsv_str)
            res_rgb.append(dom_color_rgb_str)


        # Example return value:
        #      res_code  = -1 or 0
    	#      res_hsv   = ['7, 19, 181', '40, 50, 61', '35, 114, 68', '158, 15, 182', '80, 16, 176']
    	#      res_rgb   = ['181, 171, 168', '57, 61, 49', '63, 68, 38', '182, 171, 179', '165, 176, 172']
    	#      conf_list = [0.45, 0.17, 0.17, 0.13, 0.09]

    except:
        return -1, [], [], []

    return 0, res_hsv, res_rgb, conf_list


def get_multiple_dominant_colors(image1, image2, image3, image_processing_size=None):
    """
    takes an image as input
    returns two lists
        i) five dominant colors of the image as a list (int values)
        ii) list of confidence values of the same size (2 decimal places)

    dominant colors are found by running k means on the
    pixels & returning the centroid of the largest cluster

    processing time is sped up by working with a smaller image;
    this resizing can be done with the image_processing_size param
    which takes a tuple of image dims as input

    >>> get_multiple_dominant_colors(my_image, k, image_processing_size = (25, 25))
    [
        [0, 0, 254],
        [110, 37, 188],
        [101, 13, 241],
        [45, 26, 181],
        [85, 28, 133]
    ]                                       // five dominant colors in HSV format

    [0.84, 0.05, 0.05, 0.04, 0.02]          // confidence values

    """

    k = g.COLOR_CLUSTER

    # read in image of interest
    bgr_image1 = cv2.imread(image1)
    bgr_image2 = cv2.imread(image2)
    bgr_image3 = cv2.imread(image3)
    # convert to HSV; this is a better representation of how we see color
    hsv_image1 = cv2.cvtColor(bgr_image1, cv2.COLOR_BGR2HSV)
    hsv_image2 = cv2.cvtColor(bgr_image2, cv2.COLOR_BGR2HSV)
    hsv_image3 = cv2.cvtColor(bgr_image3, cv2.COLOR_BGR2HSV)

    # resize image if new dims provided
    if image_processing_size is not None:
        image1 = cv2.resize(hsv_image1, image_processing_size, interpolation=cv2.INTER_AREA)
        image2 = cv2.resize(hsv_image2, image_processing_size, interpolation=cv2.INTER_AREA)
        image3 = cv2.resize(hsv_image3, image_processing_size, interpolation=cv2.INTER_AREA)

    # reshape the image to be a list of pixels
    image1 = image1.reshape((image1.shape[0] * image1.shape[1], 3))
    image2 = image2.reshape((image2.shape[0] * image2.shape[1], 3))
    image3 = image3.reshape((image3.shape[0] * image3.shape[1], 3))

    image = np.concatenate((image1, image2, image3))

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
        confidences.append(round(label[1]/TOTAL, 2))

#    print(dominant_colors_hsv)
#    print(confidences)

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
#    print("ITR : {}".format(itr))

    # trim insignificant colors
    for i in range(len(itr)):
        dominant_colors_hsv.pop(itr[i])
        confidences.pop(itr[i])

    # convert HSV to get RGB colors
    dominant_colors_rgb = []
    for color_hsv in dominant_colors_hsv:
        ret = hsvToRgb(color_hsv[0], color_hsv[1], color_hsv[2])
        dominant_colors_rgb.append(ret)

#    print("\n")
#    print(dominant_colors_hsv)
#    print(dominant_colors_rgb)
#    print(confidences)


    return len(confidences), dominant_colors_hsv, dominant_colors_rgb, confidences
