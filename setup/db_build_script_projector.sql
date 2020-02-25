----------------------------------------------------------------
-- PROJECTOR (EXPLORER) BUILD SCRIPT
-- color fields are added in pictures and hikes table

DROP TABLE IF EXISTS "pictures";

-- picture_id is here, but not in CAMERA db
CREATE TABLE "pictures" (
	"picture_id"		INTEGER PRIMARY KEY UNIQUE,
	"time"				REAL UNIQUE,
	"hike"				INTEGER,
	"index_in_hike"		INTEGER,
	"altitude"			REAL,
	"hue"		REAL,
	"saturation"		REAL,
	"value"		REAL,
	"red"		REAL,
	"green"		REAL,
	"blue"		REAL,
	"camera1"			TEXT,
	"camera2"			TEXT,
	"camera3"			TEXT,
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
	"avg_brightness" 	REAL,
	"avg_hue" 			REAL,
	"avg_hue_lumosity" 	REAL,
	"start_time"		REAL UNIQUE,
	"end_time"			REAL UNIQUE,
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
