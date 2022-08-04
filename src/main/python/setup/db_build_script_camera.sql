----------------------------------------------------------------
-- CAMERA (COLLECTOR) BUILD SCRIPT

DROP TABLE IF EXISTS "pictures";

-- no picture_id, this is added upon transfer back to projector
CREATE TABLE "pictures" (
	"time"				REAL UNIQUE,
	"altitude"			REAL,
	"hike"				INTEGER,
	"index_in_hike"		INTEGER,
	"camera1"			TEXT UNIQUE,
	"camera2"			TEXT UNIQUE,
	"camera3"			TEXT UNIQUE,
	"created_date_time" TEXT DEFAULT CURRENT_TIMESTAMP,
	"updated_date_time" TEXT DEFAULT CURRENT_TIMESTAMP,
	FOREIGN KEY("hike") REFERENCES "hikes"("hike_id")
);

DROP TABLE IF EXISTS "hikes";

-- hike_id is a PRIMARY KEY AUTOINCREMENT which maintains the hike count
-- even when the table is deleted the hike count persists
CREATE TABLE "hikes" (
	"hike_id"			INTEGER PRIMARY KEY AUTOINCREMENT,
	"start_time"		REAL UNIQUE,
	"end_time"			REAL UNIQUE,
	"pictures"			INTEGER,
	"path" 				TEXT UNIQUE,
	"created_date_time" TEXT DEFAULT CURRENT_TIMESTAMP,
	"updated_date_time" TEXT DEFAULT CURRENT_TIMESTAMP
);
