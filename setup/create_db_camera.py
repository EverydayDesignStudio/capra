#!/usr/bin/env python3

# Creates brand new database for a Capra Collector camera

import os
import sqlite3


# Builds from the absolute path of the file
# regardless from where this scripts is called
path = os.path.dirname(os.path.abspath(__file__))

# Create path for db creation buildscript
file = 'db_build_script_camera.sql'
build_script_path = '{p}/{f}'.format(p=path, f=file)

# Open the SQL script
with open(build_script_path, 'r') as sql_file:
    sql_build_script = sql_file.read()

# Run the SQL command
db = sqlite3.connect('capra_camera.db')
cursor = db.cursor()
cursor.executescript(sql_build_script)
print('Building new Capra Collector camera database...')
db.commit()
db.close()

# Create a new directory for capra-storage
storage_path = '{p}/../../capra-storage'.format(p=path)
if not os.path.exists(storage_path):
    os.makedirs(storage_path)
    print('✅ SUCCESS: directory created @ {sp}'.format(sp=storage_path))
else:
    print('⚠️ WARNING: directory already exists; no directory created')

# Move the newly created database file to capra-storage
new_db_path = '{sp}/capra_camera.db'.format(sp=storage_path)
os.rename('capra_camera.db', new_db_path)

print('✅ SUCCESS: database created @ {dbp}'.format(dbp=new_db_path))
