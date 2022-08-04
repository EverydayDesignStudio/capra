#!/usr/bin/env python3

# from classes.ui_components import UILabel, UIUnderlay
from projector_slideshow import Status, StatusMode, StatusOrientation, StatusPlayPause, StatusScope
import unittest


class StatusTest(unittest.TestCase):
    def testSameStatusObject(self):
        stat1 = Status()
        stat1.next_mode()
        stat2 = Status()
        stat2.change_scope()
        stat3 = Status()

        self.assertEqual(id(stat1), id(stat2))
        self.assertEqual(id(stat2), id(stat3))
        self.assertEqual(id(Status()), id(Status()))

    def testNextMode(self):
        self.assertEqual(Status().get_mode(), StatusMode.TIME)

        Status().next_mode()
        self.assertEqual(Status().get_mode(), StatusMode.ALTITUDE)

        Status().next_mode()
        self.assertEqual(Status().get_mode(), StatusMode.COLOR)

        Status().next_mode()
        self.assertEqual(Status().get_mode(), StatusMode.TIME)

        self.assertEqual(type(Status().get_mode()), StatusMode)

    def testChangeScope(self):
        Status().change_scope()
        self.assertEqual(Status().get_scope(), StatusScope.GLOBAL)

        Status().change_scope()
        self.assertEqual(Status().get_scope(), StatusScope.HIKE)

        self.assertEqual(type(Status().get_scope()), StatusScope)

    def testChangePlayPause(self):
        Status()._playpause = StatusPlayPause.PAUSE

        Status().change_playpause()
        self.assertEqual(Status().get_playpause(), StatusPlayPause.PLAY)

        Status().change_playpause()
        self.assertEqual(Status().get_playpause(), StatusPlayPause.PAUSE)

        self.assertEqual(type(Status().get_playpause()), StatusPlayPause)

    def testChangeOrientation(self):
        Status()._orientation = StatusOrientation.LANDSCAPE

        Status().change_orientation()
        self.assertEqual(Status().get_orientation(), StatusOrientation.PORTRAIT)

        Status().change_orientation()
        self.assertEqual(Status().get_orientation(), StatusOrientation.LANDSCAPE)

        self.assertEqual(type(Status().get_orientation()), StatusOrientation)

    def testSetOrientation(self):
        Status()._orientation = StatusOrientation.PORTRAIT

        Status().set_orientation_landscape()
        self.assertEqual(Status().get_orientation(), StatusOrientation.LANDSCAPE)

        Status().set_orientation_vertical()
        self.assertEqual(Status().get_orientation(), StatusOrientation.PORTRAIT)

        self.assertEqual(type(Status().get_orientation()), StatusOrientation)


if __name__ == '__main__':
    print('Results of : projector_classes_test.py\n')
    unittest.main()
