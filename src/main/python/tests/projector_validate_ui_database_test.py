#!/usr/bin/env python3

from classes.capra_data_types import Picture, Hike
from classes.sql_controller import SQLController
from classes.sql_statements import SQLStatements
import unittest


class DatabaseValidityTest(unittest.TestCase):
    '''This is to test the validity of a given database, which you select on launch
    The main things tested: \n
    • Does `hikes` table have same count as `SELECT count(*) FROM pictures WHERE hike=n` \n
    • Do rank's last values == count \n
    • Verify hike ranks go 1,2,3...n-2,n-1,n \n
    • Verify archive ranks go 1,2,3...n-2,n-1,n
    '''

    # hard-coded locations
    DB = 'tests/capra_projector_jun2021_min_test_0708.db'  # no / infront makes the path relative
    directory = 'capra-storage'
    sql_controller = None
    sql_statements = None
    picture = None

    # hikes = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10,
    #          15, 16, 19, 29, 30, 31, 33, 41, 43, 44,
    #          50, 51, 52, 53, 54, 58, 59, 60]

    # first picture_id of each hike
    # picids_hikes = [2262, 3152, 3373, 5529, 5912, 7300, 8202, 9616, 11062, 11241,
    #                 14801, 17135, 17159, 18885, 21166, 21209, 21768, 1, 82, 144,
    #                 23493, 24612, 25095, 25570, 26996, 27262, 27631, 29765]

    @classmethod
    def setUpClass(self):
        # NOTE - if the database or id is changed, all the tests will break
        # They are dependent upon that
        self.sql_controller = SQLController(database=self.DB, directory=self.directory)
        self.picture = self.sql_controller.get_picture_with_id(1)

        # For testing directly on the sql statements
        self.sql_statements = SQLStatements()

    @classmethod
    def tearDownClass(self):
        self.sql_controller = None

    def test_get_picture_with_id(self):
        self.assertEqual(self.picture.picture_id, 1)
        self.assertEqual(self.picture.altitude, 14.25)

    # Size Calls
    # --------------------------------------------------------------------------
    def test_get_archive_size(self):
        size = self.sql_controller.get_archive_size()
        # self.assertEqual(size, 30378)
        self.assertEqual(size, 30404)

    def test_hike_sizes_with_ranks(self):
        print('\n   Hike ID\tcount(*)\thikes table\tindex_in_hike\taltrank_hike\tcolor_rank_hike')

        sql = 'SELECT hike_id FROM hikes'
        rows = self.sql_controller._execute_query_for_anything(sql)

        # for h in self.hikes:
        for r in rows:
            h = r[0]
            sz_count = self.sql_controller.get_hike_size_with_id(h)
            sql = 'SELECT pictures FROM hikes WHERE hike_id={h};'.format(h=h)
            sz_hikes_table = self.sql_controller._execute_query_for_int(sql)

            last_index_qry = 'SELECT index_in_hike FROM pictures WHERE hike={h} ORDER BY index_in_hike DESC LIMIT 1;'.format(h=h)
            last_index = self.sql_controller._execute_query_for_int(last_index_qry)
            last_altrank_qry = 'SELECT altrank_hike FROM pictures WHERE hike={h} ORDER BY altrank_hike DESC LIMIT 1;'.format(h=h)
            last_altrank = self.sql_controller._execute_query_for_int(last_altrank_qry)
            last_colorrank_qry = 'SELECT color_rank_hike FROM pictures WHERE hike={h} ORDER BY color_rank_hike DESC LIMIT 1;'.format(h=h)
            last_colorrank = self.sql_controller._execute_query_for_int(last_colorrank_qry)

            if sz_count == sz_hikes_table == last_index == last_altrank == last_colorrank:
                match = '✅'
            else:
                match = '❌'

            print('{bool} {h}\t\t{cnt}\t\t{tbl}\t\t{ind}\t\t{alt}\t\t{clr}'.format(
                bool=match, h=h, cnt=sz_count, tbl=sz_hikes_table, ind=last_index, alt=last_altrank, clr=last_colorrank))

    def test_incremental_validity_ranks_hikes(self):
        print('\n\n')
        sql = 'SELECT hike_id FROM hikes'
        rows = self.sql_controller._execute_query_for_anything(sql)
        for r in rows:  # same as r = rows[0]
            h = r[0]

            queries = ['SELECT index_in_hike FROM pictures WHERE hike={h} ORDER BY index_in_hike ASC;'.format(h=h),
                       'SELECT altrank_hike FROM pictures WHERE hike={h} ORDER BY altrank_hike ASC;'.format(h=h),
                       'SELECT color_rank_hike FROM pictures WHERE hike={h} ORDER BY color_rank_hike ASC;'.format(h=h)]
            for q in queries:
                print('Testing:\t{q}'.format(q=q))
                indexes = self.sql_controller._execute_query_for_anything(q)

                counter = 1
                for i in indexes:
                    self.assertEqual(counter, i[0])
                    counter += 1

    def test_incremental_validity_ranks_archive(self):
        print('\n\n')
        queries = ['SELECT time_rank_global FROM pictures ORDER BY time_rank_global ASC;',
                   'SELECT altrank_global FROM pictures ORDER BY altrank_global ASC;',
                   'SELECT altrank_global_h FROM pictures ORDER BY altrank_global_h ASC;',
                   'SELECT color_rank_global FROM pictures ORDER BY color_rank_global ASC;',
                   'SELECT color_rank_global_h FROM pictures ORDER BY color_rank_global_h ASC;']
        for q in queries:
            print('Testing:\t{q}'.format(q=q))
            indexes = self.sql_controller._execute_query_for_anything(q)

            counter = 1
            for i in indexes:
                self.assertEqual(counter, i[0])
                counter += 1


if __name__ == '__main__':
    print('Results of : projector_validate_ui_database_test.py\n')
    unittest.main()
