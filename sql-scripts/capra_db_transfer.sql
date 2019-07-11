USE capra_projector;
-- then attach capra_camera to it

----------------------------------------------------------------
-- Calculate Values where hike=id

-- Average Altitude
SELECT AVG(altitude) FROM pictures WHERE hike={id};

-- Calculate Average Color
-- python.script()

-- First Time
SELECT time FROM pictures WHERE hike={id} ORDER BY time ASC LIMIT 1;

-- Last Time
SELECT time FROM pictures WHERE hike={id} ORDER BY time DESC LIMIT 1;

-- Count of hike pictures
SELECT count(*) FROM pictures WHERE hike={id};

-- Update the hikes row
UPDATE hikes SET update_date_time=datetime();

UPDATE hikes SET average_altitude={a}, average_color='{c}', end_time={et}, pictures={p}, updated_date_time=datetime() WHERE hike_id={id}


----------------------------------------------------------------
-- Inserts into hikes and pictures on PROJECTOR DB
INSERT INTO hikes (hike_id, average_altitude, average_color, start_time, end_time, pictures, created_date_time, updated_date_time) VALUES ({h}, {a}, '{c}', {st}, {et}, {p}, {cd}, datetime())

INSERT INTO pictures (time, altitude, color, hike, index_in_hike, camera1, camera2, camera3, created_date_time, updated_date_time) VALUES ({t}, {a}, '{c}', {h}, {i}, '{c1}', '{c2}', '{c3}', {cd}, datetime())


----------------------------------------------------------------
-- Delete all items from a table
DELETE FROM hikes;
DELETE FROM pictures;
