# this script is to transform any outdated

import globals as g
import os
import os.path
import datetime
import time
import sqlite3                                      # Database Library
from classes.capra_data_types import Picture, Hike
from classes.sql_controller import SQLController
from classes.sql_statements import SQLStatements
g.init()

start_time = time.time()

oldDBController = None
newDBController = None

# PATH = '/media/pi/capra-hd/'
PATH = '../capra-sample-data/dbTransform/'
OLD_DB = PATH + 'capra_projector_test.db'
NEW_DB = PATH + 'capra_camera_test.db'

print("Old db: {}".format(OLD_DB))
print("New db: {}".format(NEW_DB))

oldDBController = SQLController(database=OLD_DB)
newDBController = SQLController(database=NEW_DB)

oldCursor = oldDBController.connection.cursor()
newCursor = newDBController.connection.cursor()


# *** hikes ***
#         "hike_id"             INTEGER UNIQUE,
#         "avg_altitude"        REAL,
#         "avg_brightness"      REAL,
#         "avg_hue"             REAL,
#         "avg_hue_lumosity"    REAL,
#         "start_time"          REAL UNIQUE,
#         "end_time"            REAL UNIQUE,
#         "pictures"            INTEGER,
#         "path"                TEXT UNIQUE,
#         "created_date_time"   TEXT DEFAULT CURRENT_TIMESTAMP,
#         "updated_date_time"   TEXT DEFAULT CURRENT_TIMESTAMP

#  0   1    2    3    4             5                   6      7            8                           9                     10
# [9, ---, ---, ---, ---, 1562198618.46861, 1562223653.08857, 179, /media/pi/capra-hd/hike9/, 2019-08-21 23:55:27, 2019-08-21 23:55:27]

# ==>>>  "hikes"  (Camera)
# 	     "hike_id"			    INTEGER PRIMARY KEY AUTOINCREMENT,
# 	     "start_time"		    REAL UNIQUE,
# 	     "end_time"			    REAL UNIQUE,
# 	     "pictures"			    INTEGER,
#        "path" 			    TEXT UNIQUE,
# 	     "created_date_time"    TEXT DEFAULT CURRENT_TIMESTAMP,
# 	     "updated_date_time"    TEXT DEFAULT CURRENT_TIMESTAMP

# [1, ---, ---, 1561956190.65629, 1561960917.70036, 3, ---, 2019-11-26 11:26:56, 2019-11-26 11:26:56]

count = 0

# hikes
oldStatement = "SELECT * from hikes;"
oldCursor.execute(oldStatement)
rows = oldCursor.fetchall()
print("@@ HIKES: total {} rows".format(str(len(rows))))
for row in rows:
    statementPictures = "INSERT OR REPLACE INTO hikes \
        (hike_id, start_time, end_time, pictures, path, created_date_time, updated_date_time) \
        VALUES ({}, {}, {}, {}, '{}', '{}', '{}')\
        ".format(str(row[0]), str(row[5]), str(row[6]), str(row[7]), row[8], row[9], row[10])

    newCursor.execute(statementPictures)

    count += 1
    print("### hike row {} done. hikeID: {}".format(str(count), str(row[0])))
newDBController.connection.commit()

# *** pictures ***
#         "picture_id"          INTEGER UNIQUE,
#         "time"                REAL,
#         "altitude"            REAL,
#         "brightness"          REAL,
#         "brightness_rank"     INTEGER,
#         "hue"                 REAL,
#         "hue_rank"            INTEGER,
#         "hue_lumosity"        REAL,
#         "hue_lumosity_rank"   INTEGER,
#         "hike"                INTEGER,
#         "index_in_hike"       INTEGER,
#         "camera1"             TEXT,
#         "camera2"             TEXT,
#         "camera3"             TEXT,
#         "camera_landscape"    TEXT,
#         "created_date_time"   TEXT DEFAULT CURRENT_TIMESTAMP,
#         "updated_date_time"   TEXT DEFAULT CURRENT_TIMESTAMP,
#         PRIMARY KEY("picture_id"),
#         FOREIGN KEY("hike") REFERENCES "hikes"("hike_id")

#  0        1               2    3     4    5    6    7     8  9  10            11                              12                                          13                       14         15                  16
# [274, 1562198633.49308, 63.81, ---, ---, ---, ---, ---, ---, 9, 1, /media/pi/capra-hd/hike9/1_cam1.jpg, /media/pi/capra-hd/hike9/1_cam2.jpg, /media/pi/capra-hd/hike9/1_cam3.jpg, ---, 2019-08-22 04:33:07, 2019-08-22 04:33:07]

# ==>>>  "pictures" (Camera)
# 	     "time"				    REAL UNIQUE,
# 	     "altitude"			    REAL,
# 	     "hike"				    INTEGER,
# 	     "index_in_hike"		INTEGER,
#  	     "camera1"			    TEXT UNIQUE,
# 	     "camera2"			    TEXT UNIQUE,
# 	     "camera3"			    TEXT UNIQUE,
# 	     "created_date_time"    TEXT DEFAULT CURRENT_TIMESTAMP,
# 	     "updated_date_time"    TEXT DEFAULT CURRENT_TIMESTAMP,
# 	     FOREIGN KEY("hike") REFERENCES "hikes"("hike_id")

# [1561956193.86329, 3.0, ---, 1, 0, /media/pi/capra-hd/test/hike1/0_cam1.jpg, /media/pi/capra-hd/test/hike1/0_cam2.jpg, /media/pi/capra-hd/test/hike1/0_cam3.jpg, 2020-03-10 01:51:57, 2020-03-10 01:51:57]

count = 0

# Pictures
oldStatement = "SELECT * from pictures;"
oldCursor.execute(oldStatement)
rows = oldCursor.fetchall()
print("@@ PICTURES: total {} rows".format(str(len(rows))))
for row in rows:
    statementPictures = "INSERT OR REPLACE INTO pictures \
        (time, altitude, hike, index_in_hike, camera1, camera2, camera3, created_date_time, updated_date_time) \
        VALUES ({}, {}, {}, {}, '{}', '{}', '{}', '{}', '{}')\
        ".format(str(row[1]), str(row[2]), str(row[9]), str(row[10]), row[11], row[12], row[13], row[15], row[16])

    newCursor.execute(statementPictures)

    count += 1
    if (count % 1000 == 0):
        print("### CHECKPOINT: picture row {} done".format(str(count)))

newDBController.connection.commit()

print(" ---- executed in {}s ---- ".format(str(time.time() - start_time)))
