from sklearn.cluster import KMeans  # pip install -U scikit-learn
from collections import Counter
import numpy as np
import cv2  # pip install opencv-python : for resizing image
from pathlib import Path
import time
import colorsys
from colormath.color_objects import HSVColor, LabColor
from colormath.color_conversions import convert_color
from colormath.color_diff import delta_e_cie2000

DATAPATH = '/Users/myoo/Development/capra_data/_sample/hike0/'
CLUSTERS = 10
DIMX = 160
DIMY = 95
TOTAL = DIMX * DIMY
OUTPUTPATH = DATAPATH + "dominantColors_" + str(DIMX) + "x" + str(DIMY) + '_' + str(CLUSTERS) + ".txt"


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


def get_multiple_dominant_colors(image1, image2, image3, k, image_processing_size=None):
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

    # resize image if new dims provided
    if image_processing_size is not None:
        image1 = cv2.resize(image1, image_processing_size, interpolation=cv2.INTER_AREA)
        image2 = cv2.resize(image2, image_processing_size, interpolation=cv2.INTER_AREA)
        image3 = cv2.resize(image3, image_processing_size, interpolation=cv2.INTER_AREA)

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

    print(dominant_colors_hsv)
    print(confidences)

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

        # print("color {} ({}) : \n\t{}".format(i, color_i, color_i_delta))
        # print("index to remove : {}".format(index_to_remove))

    itr = list(index_to_remove)
    itr.sort(reverse = True)
    print("ITR : {}".format(itr))

    # trim insignificant colors
    for i in range(len(itr)):
        dominant_colors_hsv.pop(itr[i])
        confidences.pop(itr[i])

    dominant_colors_rgb = []
    for color_hsv in dominant_colors_hsv:
        color_rgb = colorsys.hsv_to_rgb(color_hsv[0]/180., color_hsv[1]/255., color_hsv[2]/255.)
        # print(list(color_rgb))
        ret = list(map(lambda a : round(a*255), list(color_rgb)))
        # print(ret)
        dominant_colors_rgb.append(ret)

    print("\n")
    print(dominant_colors_hsv)
    print(dominant_colors_rgb)
    print(confidences)


    return len(confidences), dominant_colors_hsv, dominant_colors_rgb, confidences


startTime = time.time()

pathlist = Path(DATAPATH).glob('*.jpg')
img = ""
res = []
count = 1
# for path in pathlist:
    # if (count < 1000):
    #     count += 1
    #     continue
    # if (count == 1500):
    #     break

    # try:
    # because path is object not string
img1 = str("/Users/myoo/Development/capra_data/_sample/hike0/194_cam1.jpg")
img2 = str("/Users/myoo/Development/capra_data/_sample/hike0/194_cam2.jpg")
img3 = str("/Users/myoo/Development/capra_data/_sample/hike0/194_cam3.jpg")
# imgName = img.rsplit('/', 1)[1]
# print("{} - {}".format(count, imgName))

# read in image of interest
bgr_image1 = cv2.imread(img1)
bgr_image2 = cv2.imread(img2)
bgr_image3 = cv2.imread(img3)
# convert to HSV; this is a better representation of how we see color
hsv_image1 = cv2.cvtColor(bgr_image1, cv2.COLOR_BGR2HSV)
hsv_image2 = cv2.cvtColor(bgr_image2, cv2.COLOR_BGR2HSV)
hsv_image3 = cv2.cvtColor(bgr_image3, cv2.COLOR_BGR2HSV)

# # extract dominant color (in HSV)
# # (aka the centroid of the most popular k means cluster)
# dom_color_hsv = get_dominant_color(hsv_image, k=CLUSTERS, image_processing_size=(DIMX, DIMY))
#
# # temporarily create a pixel with HSV to extract RGB value
# tmp = np.full((1, 1, 3), dom_color_hsv, dtype='uint8')
# dom_color_rgb = cv2.cvtColor(tmp, cv2.COLOR_HSV2RGB)[0][0].tostring()
#
# # convert lists to string
# dom_color_hsv_str = ', '.join(map(str, dom_color_hsv))
# dom_color_rgb_str = ', '.join(map(str, dom_color_rgb))

color_size, dom_colors_hsv, dom_colors_rgb, conf_list= get_multiple_dominant_colors(hsv_image1, hsv_image2, hsv_image3, k=CLUSTERS, image_processing_size=(DIMX, DIMY))

res_hsv = ""
res_rgb = ""
conf = ""

for i in range(color_size):
    add = ","
    if (i == color_size-1):
        add = ""

    res_hsv += str(dom_colors_hsv[i][0]) + "," + str(dom_colors_hsv[i][1]) + "," + str(dom_colors_hsv[i][2]) + add
    res_rgb += str(dom_colors_rgb[i][0]) + "," + str(dom_colors_rgb[i][1]) + "," + str(dom_colors_rgb[i][2]) + add
    conf += str(conf_list[i]) + add



print("\n")
print(res_hsv)
print(res_rgb)
print(conf)

#
# res_rgb = []
# res_hsv = []
# for dom_color_hsv in dom_colors_hsv:
#     # temporarily create a pixel with HSV to extract RGB value
#     tmp = np.full((1, 1, 3), dom_color_hsv, dtype='uint8')
#     dom_color_rgb = cv2.cvtColor(tmp, cv2.COLOR_HSV2RGB)[0][0].tostring()
#
#     # convert lists to string
#     dom_color_hsv_str = ', '.join(map(str, dom_color_hsv))
#     dom_color_rgb_str = ', '.join(map(str, dom_color_rgb))
#
#     res_hsv.append(dom_color_hsv_str)
#     res_rgb.append(dom_color_rgb_str)

#
# row = imgName + ', ' + ', '.join(res_hsv) + ', ' + ', '.join(res_rgb)
#
# res = "{} ({})\n".format(imgName, count)
# res += "\t{}\n".format(res_hsv)
# res += "\t{}\n".format(res_rgb)
# res += "\t{}".format(conf_list)
#
# print("{} ({})".format(imgName, count))
# print("\t{}".format(res_hsv))
# print("\t{}".format(res_rgb))
# print("\t{}".format(conf_list))
#
# # res.append(row)
#
# count += 1
#     # except:
#     #     print(count)
#
# with open(OUTPUTPATH, 'w') as filehandle:
#     for row in res:
#         filehandle.write('%s\n' % row)


endTime = time.time()
print("### {} photos analyzed.".format(str(count)))
print("### Time elapsed: {} seconds".format(endTime - startTime))

# # create a square showing dominant color of equal size to input image
# dom_color_hsv = np.full(bgr_image.shape, dom_color, dtype='uint8')
# # convert to bgr color space for display
# dom_color_bgr = cv2.cvtColor(dom_color_hsv, cv2.COLOR_HSV2BGR)
#
# # concat input image and dom color square side by side for display
# output_image = np.hstack((bgr_image, dom_color_bgr))
#
# # show results to screen
# cv2.imshow('Image Dominant Color', output_image)
# cv2.waitKey(0)
