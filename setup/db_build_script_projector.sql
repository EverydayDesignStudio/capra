----------------------------------------------------------------
-- PROJECTOR (EXPLORER) BUILD SCRIPT
-- color fields are added in pictures and hikes table

DROP TABLE IF EXISTS "pictures";

-- picture_id is here, but not in CAMERA db
CREATE TABLE "pictures" (
	"picture_id"		INTEGER PRIMARY KEY UNIQUE,
	"time"				REAL UNIQUE,
	"year"				INTEGER,
	"month"				INTEGER,
	"day"				INTEGER,
	"minute"				INTEGER,
	"dayofweek"				INTEGER,
	"hike"				INTEGER,
	"index_in_hike"		INTEGER,
	"altitude"			REAL,
	"altrank_hike"	INTEGER UNIQUE,
	"altrank_global"	INTEGER UNIQUE,
	"camera1"			TEXT,
	"camera1_color_hsv"	TEXT,
	"camera1_color_rgb"	TEXT,
	"camera2"			TEXT,
	"camera2_color_hsv"	TEXT,
	"camera2_color_rgb"	TEXT,
	"colrank_value"	REAL,
	"colrank_hike"	INTEGER UNIQUE,
	"colrank_global"	INTEGER UNIQUE,
	"camera3"			TEXT,
	"camera3_color_hsv"	TEXT,
	"camera3_color_rgb"	TEXT,
	"camera_landscape" 	TEXT,
	"created_date_time" TEXT DEFAULT CURRENT_TIMESTAMP,
	"updated_date_time" TEXT DEFAULT CURRENT_TIMESTAMP,
	FOREIGN KEY("hike") REFERENCES "hikes"("hike_id")
);

DROP TABLE IF EXISTS "hikes";

CREATE TABLE "hikes" (
	"hike_id"			INTEGER UNIQUE,
	"avg_altitude"		REAL,
	"avg_color_camera1_hsv"	TEXT,
	"avg_color_camera2_hsv"	TEXT,
	"avg_color_camera3_hsv"	TEXT,
	"start_time"		REAL UNIQUE,
	"start_year"		INTEGER,
	"start_month"		INTEGER,
	"start_day"		INTEGER,
	"start_minute"		INTEGER,
	"start_dayofweek"		INTEGER,
	"end_time"			REAL UNIQUE,
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
