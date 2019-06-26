#!/usr/bin/env python3

import os
import sys
sys.path.append('..')
from sql_controller import SQLController

DB = '/Volumes/Capra/capra-storage/capra_explorer.db'
DB_EMPTY = '/Volumes/Capra/capra-storage/capra_explorer_empty.db'

controller = SQLController(database=DB_EMPTY)


def test_get_hike_count():
    count = controller.get_hike_count()
    assert count == 5, 'Should be 5'


def test_get_last_hike_id():
    hike_id = controller.get_last_hike_id()
    assert hike_id == 5, 'Should be 5'


def test_get_last_time():
    val = controller.get_time_since_last_hike()
    print('Last time: {t}'.format(t=val))


def test_create_or_continue_hike():
    DIRECTORY = '/Volumes/Capra/capra-storage/'
    hike_num = controller.get_last_hike_id()
    folder = 'hike{n}/'.format(n=hike_num)
    os.makedirs(DIRECTORY + folder)


def test_get_last_photo_index_of_hike():
    val = controller.get_last_photo_index_of_hike(3)
    print('value: {v}'.format(v=val))


def test_create_new_hike():
    controller.create_new_hike()


def test_create_new_picture():
    controller.create_new_picture(5, 25)



if __name__ == "__main__":
    test_get_last_time()

    print('Everything passed')
