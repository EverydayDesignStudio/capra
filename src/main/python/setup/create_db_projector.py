#!/usr/bin/env python3

# Creates brand new database for a Capra Explorer projector

import os
import sqlite3

# Builds from the absolute path of the file regardless from where it is called
path = os.path.dirname(os.path.abspath(__file__))
file = 'db_build_script_projector.sql'
build_script_path = '{p}/{f}'.format(p=path, f=file)

# Open the SQL script
with open(build_script_path, 'r') as sql_file:
    sql_build_script = sql_file.read()

# Run the command
db = sqlite3.connect('capra_projector.db')
cursor = db.cursor()
cursor.executescript(sql_build_script)
print('Building new Capra Explorer projector database...')
db.commit()
db.close()
