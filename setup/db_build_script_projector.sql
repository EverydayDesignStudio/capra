----------------------------------------------------------------
-- PROJECTOR (EXPLORER) BUILD SCRIPT
-- color fields are added in pictures and hikes table

DROP TABLE IF EXISTS "pictures";

-- picture_id is here, but not in CAMERA db
CREATE TABLE "pictures" (
	"picture_id"				INTEGER PRIMARY KEY UNIQUE,
	"time"							REAL UNIQUE,
	"year"							INTEGER,
	"month"							INTEGER,
	"day"								INTEGER,
	"minute"						INTEGER,
	"dayofweek"					INTEGER,
	"hike"							INTEGER,
	"index_in_hike"			INTEGER,
	"altitude"					REAL,
	"altrank_hike"			INTEGER,
	"altrank_global"		INTEGER UNIQUE,
	"color_hsv"					TEXT,
	"color_rgb"					TEXT,
	"color_rank_value"	TEXT,
	"color_rank_hike"		INTEGER,
	"color_rank_global"	INTEGER UNIQUE,
	"colors_count"			INTEGER,
	"colors_rgb"				TEXT,
	"camera1"						TEXT,
	"camera2"						TEXT,
	"camera3"						TEXT,
	"camera_landscape" 	TEXT,
	"created_date_time" TEXT DEFAULT CURRENT_TIMESTAMP,
	"updated_date_time" TEXT DEFAULT CURRENT_TIMESTAMP,
	FOREIGN KEY("hike") REFERENCES "hikes"("hike_id")
);

DROP TABLE IF EXISTS "hikes";

CREATE TABLE "hikes" (
	"hike_id"						INTEGER UNIQUE,
	"avg_altitude"			REAL,
	"start_time"				REAL UNIQUE,
	"start_year"				INTEGER,
	"start_month"				INTEGER,
	"start_day"					INTEGER,
	"start_minute"			INTEGER,
	"start_dayofweek"		INTEGER,
	"end_time"					REAL UNIQUE,
	"end_year"					INTEGER,
	"end_month"					INTEGER,
	"end_day"						INTEGER,
	"end_minute"				INTEGER,
	"end_dayofweek"			INTEGER,
	"color_hsv"					TEXT,
	"color_rgb"					TEXT,
	"color_rank_value"	TEXT,
	"color_rank"				INTEGER UNIQUE,
	"pictures"					INTEGER,
	"path" 							TEXT UNIQUE,
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
