from sklearn.cluster import KMeans  # pip install -U scikit-learn
from collections import Counter
import numpy as np
import cv2  # pip install opencv-python : for resizing image
from pathlib import Path
import time

DATAPATH = '/Users/myoo/Development/capra_data/_sample/hike0/'
CLUSTERS = 5
DIMX = 720
DIMY = 427
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


def get_multiple_dominant_colors(image, k, image_processing_size=None):
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
        image = cv2.resize(image, image_processing_size, interpolation=cv2.INTER_AREA)

    # reshape the image to be a list of pixels
    image = image.reshape((image.shape[0] * image.shape[1], 3))

    # cluster and assign labels to the pixels
    clt = KMeans(n_clusters=k)
    labels = clt.fit_predict(image)

    # count labels to find most popular
    label_counts = Counter(labels)

    # subset out 5 popular centroids
    top5 = label_counts.most_common(CLUSTERS)
    dominant_colors = []
    confidences = []
    for label in top5:
        tmp = [ int(e) for e in clt.cluster_centers_[label[0]].tolist() ]
        dominant_colors.append(tmp)
        confidences.append(round(label[1]/TOTAL, 2))

    return dominant_colors, confidences


startTime = time.time()

pathlist = Path(DATAPATH).glob('*.jpg')
img = ""
res = []
count = 1
for path in pathlist:
    # if (count < 1000):
    #     count += 1
    #     continue
    # if (count == 1500):
    #     break

    # try:
    # because path is object not string
    img = str(path)
    imgName = img.rsplit('/', 1)[1]
    # print("{} - {}".format(count, imgName))

    # read in image of interest
    bgr_image = cv2.imread(img)
    # convert to HSV; this is a better representation of how we see color
    hsv_image = cv2.cvtColor(bgr_image, cv2.COLOR_BGR2HSV)

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

    dom_colors_hsv, conf_list= get_multiple_dominant_colors(hsv_image, k=CLUSTERS, image_processing_size=(DIMX, DIMY))

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

    row = imgName + ', ' + ', '.join(res_hsv) + ', ' + ', '.join(res_rgb)

    res = "{} ({})\n".format(imgName, count)
    res += "\t{}\n".format(res_hsv)
    res += "\t{}\n".format(res_rgb)
    res += "\t{}".format(conf_list)

    print("{} ({})".format(imgName, count))
    print("\t{}".format(res_hsv))
    print("\t{}".format(res_rgb))
    print("\t{}".format(conf_list))

    # res.append(row)

    count += 1
    # except:
    #     print(count)

with open(OUTPUTPATH, 'w') as filehandle:
    for row in res:
        filehandle.write('%s\n' % row)

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
