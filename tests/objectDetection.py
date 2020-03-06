#! /usr/bin/python 3.6

import cv2
import matplotlib.pyplot as plt
import cvlib as cv
from cvlib.object_detection import draw_bbox
import time

from collections import Counter

masterCounter = Counter()

start_time = time.time()

dataPath = "../../capra-sample-data/capra-storage/hike"
hikeID = 2

imageIndex = 2

MAX_INDEX = 32
CONF_THRESHOLD = 0.6


def analyzeHike():
    global masterCounter, start_time

    for i in range(MAX_INDEX + 1):

        imagePath = dataPath + str(hikeID) + "/" + str(i) + "_cam2r.jpg"
        im = cv2.imread(imagePath)
        bbox, label, conf = cv.detect_common_objects(im)

        print("# image {}: \n\t{} \n\t{}".format(i, label, conf))

        res = []
        for j in range(len(label)):
            if (conf[j] > CONF_THRESHOLD):
                res.append(label[j])

        tmpCounter = Counter(res)
        masterCounter += tmpCounter

        print("### Filtered: {}".format(tmpCounter))
        print("### Updated Master: {}".format(masterCounter))

        # if (i > 5):
        #     exit()

    print("--- %s seconds ---" % (time.time() - start_time))


def analyzeImage():
    imagePath = dataPath + str(hikeID) + "/" + str(imageIndex) + "_cam2r.jpg"
    im = cv2.imread(imagePath)
    bbox, label, conf = cv.detect_common_objects(im)
    output_image = draw_bbox(im, bbox, label, conf)

    print(label)
    print(conf)

    print("--- %s seconds ---" % (time.time() - start_time))

    plt.imshow(output_image)
    plt.show()


analyzeHike()
# analyzeImage()
