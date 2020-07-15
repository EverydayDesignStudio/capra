----------------------------------------------------------------
-- PROJECTOR (EXPLORER) BUILD SCRIPT
-- color fields are added in pictures and hikes table

DROP TABLE IF EXISTS "pictures";

-- -- picture_id is here, but not in CAMERA db
-- CREATE TABLE "pictures" (
-- 	"picture_id"		INTEGER PRIMARY KEY UNIQUE,
-- 	"time"				REAL UNIQUE,
-- 	"hike"				INTEGER,
-- 	"index_in_hike"		INTEGER,
-- 	"altitude"			REAL,
-- 	"hue"		REAL,
-- 	"saturation"		REAL,
-- 	"value"		REAL,
-- 	"red"		REAL,
-- 	"green"		REAL,
-- 	"blue"		REAL,
-- 	"camera1"			TEXT,
-- 	"camera2"			TEXT,
-- 	"camera3"			TEXT,
-- 	"camera_landscape" 	TEXT,
-- 	"created_date_time" TEXT DEFAULT CURRENT_TIMESTAMP,
-- 	"updated_date_time" TEXT DEFAULT CURRENT_TIMESTAMP,
-- 	FOREIGN KEY("hike") REFERENCES "hikes"("hike_id")
-- );

-- picture_id is here, but not in CAMERA db
CREATE TABLE "pictures" (
	"picture_id"		INTEGER PRIMARY KEY UNIQUE,
	"timestamp"				REAL UNIQUE,
	"year"				INTEGER,
	"month"				INTEGER,
	"day"				INTEGER,
	"minute"				INTEGER,
	"dayofweek"				INTEGER,
	"hike"				INTEGER,
	"index_in_hike"		INTEGER,
	"altitude"			REAL,
	"camera1"			TEXT,
	"camera1_color_hsv"	TEXT,
	"camera1_color_rgb"	TEXT,
	"camera2"			TEXT,
	"camera2_color_hsv"	TEXT,
	"camera2_color_rgb"	TEXT,
	"camera3"			TEXT,
	"camera3_color_hsv"	TEXT,
	"camera3_color_rgb"	TEXT,
	"camera_landscape" 	TEXT,
	"created_date_time" TEXT DEFAULT CURRENT_TIMESTAMP,
	"updated_date_time" TEXT DEFAULT CURRENT_TIMESTAMP,
	FOREIGN KEY("hike") REFERENCES "hikes"("hike_id")
);

DROP TABLE IF EXISTS "hikes";

-- hike_id is not PRIMARY KEY AUTOINCREMENT since it will never be incremented
-- on the projector and in the off case it is, it could get out of sync with camera
CREATE TABLE "hikes" (
	"hike_id"			INTEGER UNIQUE,
	"avg_altitude"		REAL,
	"avg_color_camera1_hsv"	TEXT,
	"avg_color_camera2_hsv"	TEXT,
	"avg_color_camera3_hsv"	TEXT,
	"start_timestamp"		REAL UNIQUE,
	"start_year"		INTEGER,
	"start_month"		INTEGER,
	"start_day"		INTEGER,
	"start_minute"		INTEGER,
	"start_dayofweek"		INTEGER,
	"end_timestamp"			REAL UNIQUE,
	"end_year"		INTEGER,
	"end_month"		INTEGER,
	"end_day"		INTEGER,
	"end_minute"		INTEGER,
	"end_dayofweek"		INTEGER,
	"pictures"			INTEGER,
	"path" 				TEXT UNIQUE,
	"created_date_time" TEXT DEFAULT CURRENT_TIMESTAMP,
	"updated_date_time" TEXT DEFAULT CURRENT_TIMESTAMP
);

DROP TABLE IF EXISTS "state";

-- Holds the current state of the controls at all times on the projector
CREATE TABLE "state" (
	"mode"				INTEGER UNIQUE,
	"hike"				INTEGER,
	"picture_id"		INTEGER,
	"created_date_time" TEXT DEFAULT CURRENT_TIMESTAMP,
	"updated_date_time" TEXT DEFAULT CURRENT_TIMESTAMP

);
