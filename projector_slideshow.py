#!/usr/bin/env python3

# Slideshow application for the Capra Explorer
# Allows passing through photos with a smooth fading animation

# TODO
# REVIEW
# REMOVE
# FIXME
# HACK

# Imports
import math
import os
import platform
from classes import sql_controller
import psutil
import sys
import time
import traceback

from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
import PIL
from PIL import Image
# from PIL import ImageTk, Image, ImageQt

# from PIL.ImageQt import ImageQt
if platform.system() == 'Linux':
    from RPi import GPIO
    from lsm303d import LSM303D
from datetime import datetime
from enum import IntEnum, unique, auto

from classes.capra_data_types import Picture, Hike
from classes.sql_controller import SQLController
from classes.led_player import RGB_LED, WHITE_LEDS
# from classes.sql_statements import SQLStatements
from classes.ui_components import *
from classes.singleton import Singleton

# PIN and Settings values are stored here
import globals as g
g.init()
print('projector_slideshow.py running...')


# Filewide Statuses
# ----- Hardware -----
rotaryCounter = 0  # Global value for rotary encoder, so ImageBlender thread doesn't need to ask MainWindow
rotaryCounterLast = 0  # Needed to measure the change of the encoder that happens during the Encoder loop

isReadyForNewPicture = True  # REVIEW - not sure if nedded, could be a solution
picture = None  # REMOVE - not needed anymore. we use ImageBlender


# Statuses
# -----------------------------------------------------------------------------

class StatusOrientation(IntEnum):
    LANDSCAPE = 0
    PORTRAIT = 1


class StatusPlayPause(IntEnum):
    PAUSE = 0
    PLAY = 1


class StatusScope(IntEnum):
    HIKE = 0
    GLOBAL = 1


class StatusMode(IntEnum):
    '''The order as described by the integer values is the order 
    in which the modes will change'''
    __order__ = 'TIME COLOR ALTITUDE'
    TIME = 0
    COLOR = 1
    ALTITUDE = 2


class StatusDirection(IntEnum):
    NEXT = 0
    PREV = 1


# Singleton Status class; starting status values are defined here
class Status(Singleton):
    """
    Singleton class containing all status variables for the slideshow
    \n\t orientation, playpause, scope, mode, direction
    """

    # Class variables, not instance variables
    # Define starting status values here
    _orientation = StatusOrientation.LANDSCAPE
    _playpause = StatusPlayPause.PAUSE
    _scope = StatusScope.HIKE
    _mode = StatusMode.TIME
    _direction = StatusDirection.NEXT

    # Eventually maybe we would need to setup this with input from the database
    def __init__(self):
        super().__init__()

    # Orientation
    def get_orientation(self) -> StatusOrientation:
        return Status()._orientation

    def change_orientation(self):
        Status()._orientation = StatusOrientation((Status()._orientation + 1) % 2)

    def set_orientation_landscape(self):
        Status()._orientation = StatusOrientation.LANDSCAPE

    def set_orientation_vertical(self):
        Status()._orientation = StatusOrientation.PORTRAIT

    # Play Pause
    def get_playpause(self) -> StatusPlayPause:
        return Status()._playpause

    def change_playpause(self):
        Status()._playpause = StatusPlayPause((Status()._playpause + 1) % 2)

    def set_play(self):
        Status()._playpause = StatusPlayPause.PLAY

    def set_pause(self):
        Status()._playpause = StatusPlayPause.PAUSE

    # Scope
    def get_scope(self) -> StatusScope:
        return Status()._scope

    def change_scope(self):
        Status()._scope = StatusScope((Status()._scope + 1) % 2)

    # Mode
    def get_mode(self) -> StatusMode:
        return Status()._mode

    def next_mode(self):
        Status()._mode = StatusMode((Status()._mode + 1) % 3)

    def set_mode_time(self):
        Status()._mode = StatusMode.TIME

    def set_mode_color(self):
        Status()._mode = StatusMode.COLOR

    def set_mode_altitude(self):
        Status()._mode = StatusMode.ALTITUDE

    # Direction
    def get_direction(self) -> StatusDirection:
        return Status()._direction

    def set_direction_next(self):
        Status()._direction = StatusDirection.NEXT

    def set_direction_prev(self):
        Status()._direction = StatusDirection.PREV


# REMOVE - since I'm using a Singleton, I don't actually need these
# Global status values -- they need to have global file scope due to the modification by the hardware
# orientation = StatusOrientation.LANDSCAPE
# playpause = StatusPlayPause.PLAY
# scope = StatusScope.HIKE
# mode = StatusMode.TIME


# Threads
# -----------------------------------------------------------------------------

class WorkerSignals(QObject):
    '''
    Defines the signals available from a running worker thread.
    Supported signals are:

    finished
        No data passed, just a notifier of completion
    error
        `tuple` (exctype, value, traceback.format_exc() )
    result
        `object` data returned from processing, anything
    results
        Four `object` data returned from processing, anything
    progress
        `int` indicating % progress
    '''
    finished = pyqtSignal()
    error = pyqtSignal(tuple)
    result = pyqtSignal(object)
    results = pyqtSignal(object, object, object, object)
    progress = pyqtSignal(int)


class RotaryEncoder(QRunnable):
    '''Custom thread for the rotary coder, so no signal is ever lost'''
    def __init__(self, PIN_A: int, PIN_B: int, *args, **kwargs):
        super(RotaryEncoder, self).__init__()

        self.RoAPin = PIN_A
        self.RoBPin = PIN_B

        GPIO.setup(self.RoAPin, GPIO.IN)
        GPIO.setup(self.RoBPin, GPIO.IN)

        self.signals = WorkerSignals()

        self.flag = 0
        self.Last_RoB_Status = 0
        self.Current_RoB_Status = 0
        self.Last_Direction = 0         # 0 for backward, 1 for forward
        self.Current_Direction = 0      # 0 for backward, 1 for forward

        self.MAXQUEUE = 7
        self.lst = list()
        self.last_time = datetime.now().timestamp()
        self.speedText = ""
        self.average = 0
        self.dt = 0
        self.multFactor = 1

    def calculate_speed(self):
        self.dt = round(datetime.now().timestamp() - self.last_time, 5)
        # data sanitation: clean up random stray values that are extremely low
        if self.dt < .005:
            self.dt = .1

        if len(self.lst) > self.MAXQUEUE:
            self.lst.pop()
        self.lst.insert(0, self.dt)
        self.average = sum(self.lst) / len(self.lst)

        self.last_time = datetime.now().timestamp()

        #   .3      .07     .02
        #   .1      .05     .02
        if self.average >= .3:
            self.speedText = "slow"
        elif self.average >= .07 and self.average < .3:
            self.speedText = "medium"
        elif self.average >= .02 and self.average < .07:
            self.speedText = "fast"
        else:
            self.speedText = "super-duper fast"

        return self.average, self.speedText, self.dt

    # Starting logic comes from the following project:
    # https://www.sunfounder.com/learn/Super_Kit_V2_for_RaspberryPi/lesson-8-rotary-encoder-super-kit-for-raspberrypi.html
    def rotaryTurn(self):
        global rotaryCounter

        self.Last_RoB_Status = GPIO.input(self.RoBPin)

        while(not GPIO.input(self.RoAPin)):
            self.Current_RoB_Status = GPIO.input(self.RoBPin)
            self.flag = 1

        if self.flag == 1:
            Status().set_pause()  # Causes the PlayPause thread to not increment the rotary counter
            self.flag = 0

            if (self.Last_RoB_Status == 0) and (self.Current_RoB_Status == 1):
                self.Current_Direction = 1
            if (self.Last_RoB_Status == 1) and (self.Current_RoB_Status == 0):
                self.Current_Direction = 0

            if (self.Current_Direction != self.Last_Direction):
                self.lst.clear()

            self.average, self.speedText, self.dt = self.calculate_speed()

            speed = 0.5 / self.dt
            self.multFactor = int(0.5 / self.average)
            if (self.multFactor < 1 or self.Current_Direction != self.Last_Direction):
                self.multFactor = 1

            if (self.Current_Direction == 1):
                rotaryCounter = rotaryCounter - 1 * self.multFactor
                Status().set_direction_prev()
            else:
                rotaryCounter = rotaryCounter + 1 * self.multFactor
                Status().set_direction_next()

            self.Last_Direction = self.Current_Direction
            print('rotaryCounter: {g}, diff_time: {d:.4f}, speed: {s:.2f}, MultFactor: {a:.2f} ({st})'.format(g=rotaryCounter, d=self.dt, s=speed, a=self.multFactor, st=self.speedText))

            # The counter is never reset, ImageBlender finds difference between this read and the last read
            # No signal is ever emitted since rotaryCounter is a global value that is only written to in this thread
            # ImageBlender can directly access it safely, at anytime

    def clear(self, ev=None):
        global rotaryCounter
        rotaryCounter = 0
        print('rotaryCounter = {g}'.format(g=rotaryCounter))
        time.sleep(1)

    def run(self):
        while True:
            self.rotaryTurn()


class HardwareButton(QRunnable):
    '''Thread to continually monitor a GPIO PIN, emits signal when button is pressed'''
    def __init__(self, PIN: int, *args, **kwargs):
        super(HardwareButton, self).__init__()

        self.status = False
        self.PIN = PIN
        GPIO.setup(self.PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        self.signals = WorkerSignals()

    def run(self):
        while True:
            if GPIO.input(self.PIN) == False:         # Button press detected
                if self.status == False:              # Button was just OFF
                    self.signals.result.emit(True)
                    self.status = True              # Update the status to ON
            else:                                   # Button is not pressed
                self.status = False
            time.sleep(0.05)


class Accelerometer(QRunnable):
    '''Thread to monitor the LSM303D accelerometer'''
    def __init__(self, address, *args, **kwargs):
        super(Accelerometer, self).__init__()
        self.lsm = LSM303D(address)  # Create accelerometer object from the address (should be 0x1d)
        # self.lsm = LSM303D(0x1d)  # Change to 0x1e if you have soldered the address jumper
        self.lastOrientation = None
        self.signals = WorkerSignals()

    def run(self):
        while True:
            try:
                xyz = self.lsm.accelerometer()
            except Exception as error:
                time.sleep(2.0)
                continue
                raise Exception("Oops! There was no valid accelerometer data.")

            ax = round(xyz[0], 7)
            ay = round(xyz[1], 7)
            az = round(xyz[2], 7)

            pitch = round(180 * math.atan(ax/math.sqrt(ay*ay + az*az))/math.pi, 3)
            roll = round(180 * math.atan(ay/math.sqrt(ax*ax + az*az))/math.pi, 3)

            if abs(pitch) < 20:
                if roll < -45:  # correct vertical
                    orientation = StatusOrientation.PORTRAIT
                elif roll > 45:  # upside-down vertical
                    orientation = None
                else:  # horizontal
                    orientation = StatusOrientation.LANDSCAPE
            else:
                if roll < -30:  # correct vertical
                    orientation = StatusOrientation.PORTRAIT
                elif roll > 30:  # upside-down vertical
                    orientation = None
                else:  # horizontal
                    orientation = StatusOrientation.LANDSCAPE

            # Check to see if orientation changed
            if self.lastOrientation != orientation:
                self.lastOrientation = orientation

                # Ensure it is a usable orientation
                if orientation == StatusOrientation.LANDSCAPE or orientation == StatusOrientation.PORTRAIT:
                    self.signals.result.emit(orientation)

            time.sleep(0.5)


class PlayPause(QRunnable):
    '''Thread to continually increment the slideshow while in PLAY'''
    def __init__(self, *args, **kwargs):
        super(PlayPause, self).__init__()

    def run(self):
        global rotaryCounter

        while True:
            if Status().get_playpause() == StatusPlayPause.PLAY:
                if Status().get_direction() == StatusDirection.NEXT:
                    rotaryCounter += 1
                elif Status().get_direction() == StatusDirection.PREV:
                    rotaryCounter -= 1
            # TODO - should I change this
            time.sleep(2.0)


# Continually tries blending the next image into the current image
class ImageBlender(QRunnable):
    def __init__(self, sql_cntrl, picture, *args, **kwargs):
        super(ImageBlender, self).__init__()

        # The rotary encoder needs an instance of the SQLController
        self.sql_controller = sql_cntrl
        self.picture = picture

        # Needed setup
        self.alpha = 0
        self.signals = WorkerSignals()
        self._skipNextStatus = False  # status for whether to skip next, called from MainWindow
        self._skipPrevStatus = False  # status for whether to skip previous, called from MainWindow

        self.currentf_raw = Image.open(self.picture.cameraf, 'r')
        self.nextf_raw = Image.open(self.picture.cameraf, 'r')

        self.current1_raw = Image.open(self.picture.camera1, 'r')
        self.next1_raw = Image.open(self.picture.camera1, 'r')
        self.current2_raw = Image.open(self.picture.camera2, 'r')
        self.next2_raw = Image.open(self.picture.camera2, 'r')
        self.current3_raw = Image.open(self.picture.camera3, 'r')
        self.next3_raw = Image.open(self.picture.camera3, 'r')

    # Public function only used for the computer version which needs to be told to change the image
    # since the rotary encoder won't changing value
    # TODO - Though, I could implement it so keyboard changes rotaryCount
    #
    # Receives a new "next image" which is consequently blended into the current image.
    # If this process happens in the middle of a blend, then the new image
    # will be blended into this already blended image
    def set_next_images(self, path1, path2, path3, pathf):
        global isReadyForNewPicture
        isReadyForNewPicture = False

        # nextf_raw = Image.open(pathf, 'r')
        # try:
        #     print('try:')
        #     isReadyForNewPicture = True
        #     self.nextf_raw = nextf_raw
        # finally:
        #     print('finally:')

        self.nextf_raw = Image.open(pathf, 'r')
        self.next1_raw = Image.open(path1, 'r')
        self.next2_raw = Image.open(path2, 'r')
        self.next3_raw = Image.open(path3, 'r')
        isReadyForNewPicture = True
        # Jordan

        # REVIEW - I think this might be where the bottle neck is. So my thought
        # is that we just emit a signal back to the main thread to handle this
        # with Image.open(pathf, 'r') as nextf_raw:
        #     self.nextf_raw = nextf_raw
        #     print('a new image has been opened')

        # self.nextf_raw = Image.open(pathf, 'r')

        # print(self.nextf_raw)

        # TODO - implement this with blending the images
        # self.next1_raw = Image.open(path1, 'r')
        # self.next2_raw = Image.open(path2, 'r')
        # self.next3_raw = Image.open(path3, 'r')

        # REVIEW - Old way
        # self.p1 = path1
        # self.p2 = path2
        # self.p3 = path3

        self.alpha = 0.25

    # Public function to tell thread we should skip on the next pass through the loop
    def skipNext(self):
        self._skipNextStatus = True

    def skipPrev(self):
        self._skipPrevStatus = True

    # Public functions to tell thread that we switched orientations
    def loadLandscapeImages(self):
        print("8-22-21 Changing to landscape")
        self.currentf_raw = Image.open(self.picture.cameraf, 'r')
        self.nextf_raw = Image.open(self.picture.cameraf, 'r')

        self.signals.results.emit(self.current1_raw, self.current2_raw, self.current3_raw, self.currentf_raw)

    def loadPortraitImages(self):
        print("8-22-21 Changing to portrait")
        self.current1_raw = Image.open(self.picture.camera1, 'r')
        self.next1_raw = Image.open(self.picture.camera1, 'r')
        self.current2_raw = Image.open(self.picture.camera2, 'r')
        self.next2_raw = Image.open(self.picture.camera2, 'r')
        self.current3_raw = Image.open(self.picture.camera3, 'r')
        self.next3_raw = Image.open(self.picture.camera3, 'r')
        time.sleep(0.5)  # JAR - does this help, by giving more time to update?

        self.signals.results.emit(self.current1_raw, self.current2_raw, self.current3_raw, self.currentf_raw)

    # Private functions for sql queries
    def _control_skip_next(self):
        mode = Status().get_mode()
        scope = Status().get_scope()
        if scope == StatusScope.HIKE:
            if mode == StatusMode.TIME:
                self.picture = self.sql_controller.get_next_time_skip_in_hikes(self.picture)
            elif mode == StatusMode.ALTITUDE:
                self.picture = self.sql_controller.get_next_altitude_skip_in_hikes(self.picture)
            elif mode == StatusMode.COLOR:
                self.picture = self.sql_controller.get_next_color_skip_in_hikes(self.picture)
        elif scope == StatusScope.GLOBAL:
            if mode == StatusMode.TIME:
                self.picture = self.sql_controller.get_next_time_skip_in_global(self.picture)
            elif mode == StatusMode.ALTITUDE:
                self.picture = self.sql_controller.get_next_altitude_skip_in_global(self.picture)
            elif mode == StatusMode.COLOR:
                self.picture = self.sql_controller.get_next_color_skip_in_global(self.picture)

    def _control_skip_previous(self):
        mode = Status().get_mode()
        scope = Status().get_scope()
        if scope == StatusScope.HIKE:
            if mode == StatusMode.TIME:
                self.picture = self.sql_controller.get_previous_time_skip_in_hikes(self.picture)
            elif mode == StatusMode.ALTITUDE:
                self.picture = self.sql_controller.get_previous_altitude_skip_in_hikes(self.picture)
            elif mode == StatusMode.COLOR:
                self.picture = self.sql_controller.get_previous_color_skip_in_hikes(self.picture)
        elif scope == StatusScope.GLOBAL:
            if mode == StatusMode.TIME:
                self.picture = self.sql_controller.get_previous_time_skip_in_global(self.picture)
            elif mode == StatusMode.ALTITUDE:
                self.picture = self.sql_controller.get_previous_altitude_skip_in_global(self.picture)
            elif mode == StatusMode.COLOR:
                self.picture = self.sql_controller.get_previous_color_skip_in_global(self.picture)

    def _control_rotary_next(self, change: int):
        mode = Status().get_mode()
        scope = Status().get_scope()
        currentHike = self.picture.hike_id

        if scope == StatusScope.HIKE:
            if mode == StatusMode.TIME:
                self.picture = self.sql_controller.get_next_time_in_hikes(self.picture, change)
            elif mode == StatusMode.ALTITUDE:
                self.picture = self.sql_controller.get_next_altitude_in_hikes(self.picture, change)
            elif mode == StatusMode.COLOR:
                self.picture = self.sql_controller.get_next_color_in_hikes(self.picture, change)

            if self.picture.hike_id != currentHike:
                print('🧨🧨🧨 NEXT - NEW HIKE! 🧨🧨🧨')
                # self.updateScreenHikesNewHike()
            # else:
                # self.updateScreenHikesNewPictures()
        elif scope == StatusScope.GLOBAL:
            if mode == StatusMode.TIME:
                self.picture = self.sql_controller.get_next_time_in_global(self.picture, change)
            elif mode == StatusMode.ALTITUDE:
                self.picture = self.sql_controller.get_next_altitude_in_global(self.picture, change)
            elif mode == StatusMode.COLOR:
                self.picture = self.sql_controller.get_next_color_in_global(self.picture, change)

    def _control_rotary_previous(self, change: int):
        mode = Status().get_mode()
        scope = Status().get_scope()
        currentHike = self.picture.hike_id

        if scope == StatusScope.HIKE:
            if mode == StatusMode.TIME:
                self.picture = self.sql_controller.get_previous_time_in_hikes(self.picture, change)
            elif mode == StatusMode.ALTITUDE:
                self.picture = self.sql_controller.get_previous_altitude_in_hikes(self.picture, change)
            elif mode == StatusMode.COLOR:
                self.picture = self.sql_controller.get_previous_color_in_hikes(self.picture, change)

            if self.picture.hike_id != currentHike:
                print('🧨🧨🧨 PREVIOUS - NEW HIKE! 🧨🧨🧨')
                # self.updateScreenHikesNewHike()
            # else:
                # self.updateScreenHikesNewPictures()
        elif scope == StatusScope.GLOBAL:
            if mode == StatusMode.TIME:
                self.picture = self.sql_controller.get_previous_time_in_global(self.picture, change)
            elif mode == StatusMode.ALTITUDE:
                self.picture = self.sql_controller.get_previous_altitude_in_global(self.picture, change)
            elif mode == StatusMode.COLOR:
                self.picture = self.sql_controller.get_previous_color_in_global(self.picture, change)

    # TODO - Check if I need to open all of these?
    def _emit_result_update_image_and_alpha(self):
        # Emits signal to MainWindow which calls _new_picture_loaded()
        self.signals.result.emit(self.picture)
        self.nextf_raw = Image.open(self.picture.cameraf, 'r')
        self.next1_raw = Image.open(self.picture.camera1, 'r')
        self.next2_raw = Image.open(self.picture.camera2, 'r')
        self.next3_raw = Image.open(self.picture.camera3, 'r')
        self.alpha = 0.35

    # Continually runs blending together
    def run(self):
        while True:
            # SQLController will only be called if there has been a hardware signal
            # Otherwise, it simply blends the image if alpha is < 0.65
            if self._skipNextStatus == True:
                self._control_skip_next()
                self._emit_result_update_image_and_alpha()  # NOTE - emit
                self._skipNextStatus = False
            elif self._skipPrevStatus == True:
                self._control_skip_previous()
                self._emit_result_update_image_and_alpha()  # NOTE - emit
                self._skipPrevStatus = False
            else:
                global rotaryCounter
                global rotaryCounterLast
                change = rotaryCounter - rotaryCounterLast

                # Pausing for rotary encoder changes happens inside RotaryEncoder thread
                # Because this logic is also used for the auto-play functionality
                if change > 0:
                    # print('POSITIVE')
                    # print(change)

                    rotaryCounterLast = rotaryCounter
                    self._control_rotary_next(change)
                    self._emit_result_update_image_and_alpha()  # NOTE - emit
                elif change < 0:
                    # print('NEGATIVE')
                    # print(change)

                    rotaryCounterLast = rotaryCounter
                    self._control_rotary_previous(abs(change))
                    self._emit_result_update_image_and_alpha()  # NOTE - emit

            if self.alpha < 0.65:
                # Only blends the landscape photo or portrait photos depending on the mode
                if Status().get_orientation() == StatusOrientation.LANDSCAPE:
                    try:
                        self.currentf_raw = Image.blend(self.currentf_raw, self.nextf_raw, self.alpha)
                    except Exception as error:
                        print('Error while blending landscape:')
                        print(error)
                        continue
                elif Status().get_orientation() == StatusOrientation.PORTRAIT:
                    try:
                        self.current1_raw = Image.blend(self.current1_raw, self.next1_raw, self.alpha)
                        self.current2_raw = Image.blend(self.current2_raw, self.next2_raw, self.alpha)
                        self.current3_raw = Image.blend(self.current3_raw, self.next3_raw, self.alpha)
                    except Exception as error:
                        print('Error while blending portrait:')
                        print(error)
                        continue

                # Increments the alpha, so the image will slowly blend
                # self.alpha += 0.1
                # self.alpha += 0.025  # Rougly 20 frames until the old picture is blurred out
                self.alpha += 0.04

                # Emits signal to MainWindow which calls _load_new_images()
                self.signals.results.emit(self.current1_raw, self.current2_raw, self.current3_raw, self.currentf_raw)

                if self.alpha >= 0.65:
                    # Emits signal to MainWindow which calls _finished_image_blend()
                    self.signals.finished.emit()
            # TODO - still figure out this amount
            time.sleep(0.1)  # 1/20frames = 0.05


class MainWindow(QMainWindow):
    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)

        # Test counter variable to see the frame rate
        self.blendCount = 0

        self.loadSavedState()  # Loads the state of last picture, mode, and scope
        self.setupDB()  # Mac or Windows shows the database dialog
        self.preloadUIData()
        self.setupWindowLayout()
        self.setupUI()
        self.setupSoftwareThreads()

        if platform.system() == 'Linux':
            self.setupGPIO()
            self.setupHardwareThreads()

    # Setup Helpers
    # -------------------------------------------------------------------------
    def loadSavedState(self):
        # TODO - Pull from the status text file and update the Status() object
        self._saved_picture_id = 1
        Status().set_mode_time()

    def setupDB(self):
        '''Initializes the database connection.\n
        If on Mac or Windows gives dialog box to select database,
        otherwise it will use the global defined location for the database'''

        # Mac or Windows: select the location
        if platform.system() == 'Darwin' or platform.system() == 'Windows':
            filename = QFileDialog.getOpenFileName(self, 'Open file', '', 'Database (*.db)')
            self.database = filename[0]
            self.directory = os.path.dirname(self.database)
        else:  # Raspberry Pi: preset location
            self.database = g.DATAPATH_PROJECTOR + g.DBNAME_MASTER
            self.directory = g.DATAPATH_PROJECTOR

        print(self.database)
        print(self.directory)
        self.sql_controller = SQLController(database=self.database, directory=self.directory)
        self.picture = self.sql_controller.get_picture_with_id(self._saved_picture_id)

        self.scrollspeed = 1

    def preloadUIData(self):
        self.uiData = self.sql_controller.preload_ui_data()
        self.preload = True

    # Setup the window size, title, and container layout
    def setupWindowLayout(self):
        self.setWindowTitle("Capra Explorer Slideshow")
        self.setGeometry(0, 50, 1280, 720)
        # self.setStyleSheet("background-color: black;")

        pagelayout = QVBoxLayout()
        pagelayout.setContentsMargins(0, 0, 0, 0)

        self.stacklayout = QStackedLayout()
        pagelayout.addLayout(self.stacklayout)

        # Landscape view
        # Sets the initial picture to the first selected image from the DB
        self.pictureLandscape = UIImage(self.picture.cameraf)
        self.stacklayout.addWidget(self.pictureLandscape)

        # Vertical view
        verticallayout = QHBoxLayout()
        verticallayout.setContentsMargins(0, 0, 0, 0)
        verticallayout.setSpacing(0)
        # TODO - this will eventually be images from DB, but they need to be
        # the proper size or else it'll mess up the size of the window
        self.pictureVertical1 = UIImage(self.picture.camera1)
        self.pictureVertical2 = UIImage(self.picture.camera2)
        self.pictureVertical3 = UIImage(self.picture.camera3)

        verticallayout.addWidget(self.pictureVertical3)
        verticallayout.addWidget(self.pictureVertical2)
        verticallayout.addWidget(self.pictureVertical1)

        # verticallayout.addWidget(UIImage(self.picture.camera1))
        # verticallayout.addWidget(UIImage(self.picture.camera2))
        # verticallayout.addWidget(UIImage(self.picture.camera3))

        verticalWidget = QWidget()
        verticalWidget.setLayout(verticallayout)
        self.stacklayout.addWidget(verticalWidget)

        # pagelayout2 = QVBoxLayout()
        # pagelayout2.setContentsMargins(0, 0, 0, 0)
        # pagelayout2.setAlignment(Qt.AlignBottom)

        # Add central widget
        centralWidget = QWidget()
        centralWidget.setLayout(pagelayout)
        self.setCentralWidget(centralWidget)

    # Setup the custom UI components that are on top of the slideshow
    def setupUI(self):
        # Top UI elements
        # ---------------------------------------------------------------------
        self.topUnderlay = UIUnderlay(self)
        self.leftLabel = UILabelTop(self, '', Qt.AlignLeft)
        self.centerLabel = UILabelTopCenter(self, '', '')
        self.rightLabel = UILabelTop(self, '', Qt.AlignRight)

        # Mode UI element
        self.modeOverlay = UIModeOverlay(self, 'assets/Time@1x.png')

        # Portrait UI
        # ---------------------------------------------------------------------
        self.portraitUIContainerTop = UIContainer(self, QHBoxLayout(), Qt.AlignRight)
        self.vlabelCenter = PortraitTopLabel("Altitude")
        self.vlabelCenter.setGraphicsEffect(UIEffectDropShadow())
        self.portraitUIContainerTop.layout.addWidget(self.vlabelCenter)
        self.portraitUIContainerTop.hide()

        # Time, Color, Altitude Graphs
        # ---------------------------------------------------------------------
        spacer = QSpacerItem(0, 25)
        self.bottomUIContainer = UIContainer(self, QVBoxLayout(), Qt.AlignBottom)

        rank = self.sql_controller.ui_get_percentage_in_hike_with_mode('time', self.picture)
        print(f'Rank New: {rank}')

        # Speed Indicator
        self.scrollSpeedLabel = UILabelTop(self, f'{self.scrollspeed}x', Qt.AlignLeft)
        self.scrollSpeedLabel.setGraphicsEffect(UIEffectDropShadow())
        self.bottomUIContainer.layout.addWidget(self.scrollSpeedLabel)

        # Color Palette
        self.palette = ColorPalette(self.picture.colors_rgb, self.picture.colors_conf, True)
        self.palette.setGraphicsEffect(UIEffectDropShadow())
        self.bottomUIContainer.layout.addWidget(self.palette)
        self.bottomUIContainer.layout.addItem(spacer)

        # Altitude Graph
        self.altitudelist = self.sql_controller.ui_get_altitudes_for_hike_sortby('time', self.picture)
        print(self.altitudelist)
        self.altitudegraph = AltitudeGraph(self.altitudelist, True, rank, self.picture.altitude)
        self.altitudegraph.setGraphicsEffect(UIEffectDropShadow())
        self.bottomUIContainer.layout.addWidget(self.altitudegraph)
        # self.bottomUIContainer.layout.addItem(spacer)

        # Color Bar
        self.colorlist = self.sql_controller.ui_get_colors_for_hike_sortby('time', self.picture)
        # TODO - Need data from the hike element, likely need to get the Hike on each new picture (??)
        self.colorbar = ColorBar(self.colorlist, True, rank, self.picture.color_rgb)
        self.colorbar.setGraphicsEffect(UIEffectDropShadow())
        self.bottomUIContainer.layout.addWidget(self.colorbar)

        # Time Bar
        self.timebar = TimeBar(QColor(62, 71, 47), rank, True)
        self.timebar.myHide()
        self.timebar.setGraphicsEffect(UIEffectDropShadow())
        self.bottomUIContainer.layout.addWidget(self.timebar)

        # Spacer at bottom
        self.bottomUIContainer.layout.addItem(spacer)

        # Setups up a UI timer for controlling the fade out of UI elements
        # ---------------------------------------------------------------------
        self.timerFadeOutUI = QTimer()
        self.timerFadeOutUI.setSingleShot(True)
        self.timerFadeOutUI.timeout.connect(self._fadeOutUI)

    # Setup all software threads
    # ImageFader - handles the fading between old and new pictures
    def setupSoftwareThreads(self):
        self.threadpoolSoftware = QThreadPool()
        self.threadpoolSoftware.setMaxThreadCount(2)  # TODO - change if more threads are needed

        # ImageFader, sends 3 callbacks
        # result()      : Picture (row)
        # results()     : every frame that finished a blend (~20frames per blend)
        # finished()    : when blending has finished blending two images;
        #                 callback used to know when to fade out UI elements
        self.imageBlender = ImageBlender(self.sql_controller, self.picture)

        # Receives back from ImageBlender a Picture (row)
        self.imageBlender.signals.result.connect(self._new_picture_loaded)

        # Receives back from ImageBlender blended Images (Image module); updates Pixmap
        self.imageBlender.signals.results.connect(self._load_new_images)

        # Receives finished signal, used to fade out UI and print test values
        self.imageBlender.signals.finished.connect(self._finished_image_blend)
        self.threadpoolSoftware.start(self.imageBlender)

        # Play Pause, sends 0 callbacks
        self.playPauseThread = PlayPause()
        self.threadpoolSoftware.start(self.playPauseThread)

    # Setup hardware pins
    def setupGPIO(self):
        # Set the GPIO mode, alternative is GPIO.BOARD
        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)

        # Rotary Encoder
        self.PIN_ROTARY_A = g.ENC1_A
        self.PIN_ROTARY_B = g.ENC1_B

        # Buttons
        self.PIN_ROTARY_BUTT = g.BUTT_ENC1
        self.PIN_PREV = g.BUTT_PREV
        self.PIN_PLAY_PAUSE = g.BUTT_PLAY_PAUSE
        self.PIN_NEXT = g.BUTT_NEXT
        self.PIN_MODE = g.BUTT_MODE
        self.PIN_HALL_EFFECT = g.HALL_EFFECT_PIN

        # Accelerometer
        self.PIN_ACCEL = g.ACCEL

        # NeoPixels
        # self.PIN_NEOPIXELS = g.NEO1

        # LED indicators
        self.ledWhite = WHITE_LEDS(g.WHITE_LED1, g.WHITE_LED2, g.WHITE_LED3)
        self.ledWhite.turn_off()
        if Status().get_mode() == StatusMode.TIME:
            self.ledWhite.set_time_mode()
        elif Status().get_mode() == StatusMode.COLOR:
            self.ledWhite.set_color_mode()
        elif Status().get_mode() == StatusMode.ALTITUDE:
            self.ledWhite.set_altitude_mode()

        self.ledRGB = RGB_LED(g.RGB2_RED, g.RGB2_GREEN, g.RGB2_BLUE)
        self.ledRGB.turn_off()
        # if Status().get_scope() == StatusScope.GLOBAL:
        #     self.ledRGB.turn_teal()

        # Test LED - which isn't visible from outside of the case
        self.PIN_LED_TEST_RED = g.RGB1_RED
        self.PIN_LED_TEST_GREEN = g.RGB1_GREEN
        # self.PIN_LED_TEST_BLUE = 0  # Used for sending a signal on startup (I think)
        GPIO.setup(self.PIN_LED_TEST_RED, GPIO.OUT)
        GPIO.setup(self.PIN_LED_TEST_GREEN, GPIO.OUT)

    # Setup threads to check for hardware changes
    def setupHardwareThreads(self):
        self.threadpool = QThreadPool()
        self.threadpool.setMaxThreadCount(8)  # TODO - change if more threads are needed

        # Rotary Encoder
        self.rotaryEncoder = RotaryEncoder(self.PIN_ROTARY_A, self.PIN_ROTARY_B)
        # self.rotaryEncoder.signals.result.connect(self.rotary_changed)
        self.threadpool.start(self.rotaryEncoder)

        buttonEncoder = HardwareButton(self.PIN_ROTARY_BUTT)
        buttonEncoder.signals.result.connect(self.pressed_encoder)
        self.threadpool.start(buttonEncoder)

        # Buttons
        buttonMode = HardwareButton(self.PIN_MODE)
        buttonMode.signals.result.connect(self.pressed_mode)
        self.threadpool.start(buttonMode)

        buttonPrev = HardwareButton(self.PIN_PREV)
        buttonPrev.signals.result.connect(self.pressed_prev)
        self.threadpool.start(buttonPrev)

        buttonPlayPause = HardwareButton(self.PIN_PLAY_PAUSE)
        buttonPlayPause.signals.result.connect(self.pressed_play_pause)
        self.threadpool.start(buttonPlayPause)

        buttonNext = HardwareButton(self.PIN_NEXT)
        buttonNext.signals.result.connect(self.pressed_next)
        self.threadpool.start(buttonNext)

        # Accelerometer
        accelerometer = Accelerometer(self.PIN_ACCEL)
        accelerometer.signals.result.connect(self.changed_accelerometer)
        self.threadpool.start(accelerometer)

        # Detects when the a magnet is near the hall effect
        # This may need a custom thread that continually checks for a change in status
        # I.E. there was a magnet near, but now there isn't
        buttonHallEffect = HardwareButton(self.PIN_HALL_EFFECT)
        buttonHallEffect.signals.result.connect(self.pressed_hall_effect)
        self.threadpool.start(buttonHallEffect)

    # UI Callbacks from bg threads
    # -------------------------------------------------------------------------

    def _load_new_images(self, image1, image2, image3, imagef):
        '''Loads the newly blended image from the background thread into the UIImages on the MainWindow \n
        image 1, 2, 3 are strings to the path location
        imagef is an raw Image.open()'''

        # Test variable to show how many times it blends the two images
        # not necessarily in 1 second though
        self.blendCount += 1

        self.pictureLandscape.update_pixmap(imagef)
        # JAR - comment this out
        # self.pictureVertical1.update_image("disk_cam1.jpg")
        # self.pictureVertical2.update_image("disk_cam2.jpg")
        # self.pictureVertical3.update_image("disk_cam3.jpg")

        # JAR - uncomment this
        # self.pictureVertical1.update_pixmap(image1)
        # self.pictureVertical2.update_pixmap(image2)
        # self.pictureVertical3.update_pixmap(image3)

        # NOTE - Adjusting any Widget (even a QLabel) is causing all the widgets to repaint
        if Status().get_orientation() == StatusOrientation.LANDSCAPE:
            try:
                self.pictureLandscape.update_pixmap(imagef)
            except Exception as error:
                print('Error while update_pixmap landscape:')
                print(error)
        elif Status().get_orientation() == StatusOrientation.PORTRAIT:
            try:
                self.pictureVertical1.update_pixmap(image1)
                self.pictureVertical2.update_pixmap(image2)
                self.pictureVertical3.update_pixmap(image3)
            except Exception as error:
                print('Error while update_pixmap portrait:')
                print(error)

        # Forget what the status of these were
        # self.pictureVertical1 = UIImage(self.picture.camera1)
        # self.pictureVertical2 = UIImage(self.picture.camera2)
        # self.pictureVertical3 = UIImage(self.picture.camera3)

        # Just sets the picture, no blending
        # self.pictureVertical1.update_image(image1)
        # self.pictureVertical2.update_image(image2)
        # self.pictureVertical3.update_image(image3)

    def _new_picture_loaded(self, picture: Picture):
        '''ImageBlender passes a Picture (row) back to MainWindow and updates the UI'''
        self.picture = picture

        # Update the pixmap for the mode that currently isn't being used
        # Upon orientation change, the images are already there and ready
        # if Status().get_orientation() == StatusOrientation.LANDSCAPE:
        #     self.imageBlender.changeToPortrait()
        # elif Status().get_orientation() == StatusOrientation.PORTRAIT:
        #     self.imageBlender.changeToLandscape()

        self.updateScreen()

    def _finished_image_blend(self):
        '''New image finished blending, now fade out the UI components.
        Currently only used for printing the blend count'''

        # REMOVE - Remove this testing setup for checking the number of blends
        # print('\ndef finished_image_blend() -- result emitted')
        # print('FINISHED Blending')

        print('Blended {b}xs\n'.format(b=self.blendCount))
        self.blendCount = 0

        # HACK - that almost works. However the widget is still being wiped off the screen,
        # then reapinted after the fading
        # self.palette.setCanRepaint()

        # Allows another image to be blended onto the current image
        # HACK - sorta works, but this is the safe (but ugly) base case
        # global isReadyForNewPicture
        # isReadyForNewPicture = True

        # TODO - testing moving this to updateUI
        # self.timerFadeOutUI.start(1000)  # wait 1s until you fade out top UI

    # Called when timerFadeOutUI finishes. This is bound in setupUI()
    # The timer is stopped when there is a keyboard / hardware interaction
    def _fadeOutUI(self):
        time_ms = 1000
        self.topUnderlay.fadeOut(time_ms)
        self.rightLabel.fadeOut(time_ms)
        self.leftLabel.fadeOut(time_ms)
        self.centerLabel.fadeOut()

        # self.timebar.fadeOut(time_ms)
        # self.colorbar.fadeOut(time_ms)
        # self.palette.fadeOut(time_ms)

    # UI Interactions
    # -------------------------------------------------------------------------

    def changeMode(self):
        print('changeMode()')
        Status().next_mode()

        mode = Status().get_mode()
        if mode == StatusMode.TIME:
            self.modeOverlay.setTime()
            self.ledWhite.set_time_mode()
        elif mode == StatusMode.COLOR:
            self.modeOverlay.setColor()
            self.ledWhite.set_color_mode()
        elif mode == StatusMode.ALTITUDE:
            self.modeOverlay.setAltitude()
            self.ledWhite.set_altitude_mode()

    def setLandscape(self):
        print('setLandscape()')
        Status().set_orientation_landscape()
        self.imageBlender.loadLandscapeImages()

        self.stacklayout.setCurrentIndex(Status().get_orientation())

        # self.pictureLandscape.update_image(self.picture.cameraf)

        self.portraitUIContainerTop.hide()
        self.bottomUIContainer.show()

        self.leftLabel.show()
        self.centerLabel.show()
        self.rightLabel.show()

    def setVertical(self):
        print('setVertical()')
        Status().set_orientation_vertical()
        self.imageBlender.loadPortraitImages()

        self.stacklayout.setCurrentIndex(Status().get_orientation())

        # self.pictureVertical1.update_image(self.picture.camera1)
        # self.pictureVertical2.update_image(self.picture.camera2)
        # self.pictureVertical3.update_image(self.picture.camera3)

        self.portraitUIContainerTop.show()
        self.bottomUIContainer.hide()

        self.leftLabel.hide()
        self.centerLabel.hide()
        self.rightLabel.hide()

    # Update the Screen
    # -------------------------------------------------------------------------
    # A slow and inefficient, but good base case for updating the UI on the screen
    # TODO - JRW I'm quite certain that this is the bottleneck of the program!
    def updateScreen(self):
        # self.picture.print_obj()
        # self.printCurrentMemoryUsage()
        # self.updateImages()  # Only for the Mac App

        self.updateUITop()
        self.updateUIBottom()

    # TODO - still need to have multiple blending images
    def updateImages(self):
        # Somewhere along this chain, all the paintEvents are called
        # self.imageBlender.set_next_images(self.picture.camera1, self.picture.camera2, self.picture.camera3, self.picture.cameraf)

        # TODO on Pi -  tes to see if not having the imageBlender makes it refresh faster
        # self.nextf_raw = Image.open(self.picture.cameraf, 'r')
        self._load_new_images(self.picture.camera1, self.picture.camera2, self.picture.camera3, self.nextf_raw)  # JRW

        # TODO - check on memory usage on Pi & Mac
        # self.printCurrentMemoryUsage()

    # TODO -- Might be more resource efficient to have all the objects faded out
    # in 1 method, instead of having the fade attached to each individual class
    # Animations
    def updateUITop(self):
        self.timerFadeOutUI.stop()  # stops timer which calls _fadeOutUI()

        # Do the visualization
        self.topUnderlay.show()  # semi-transparent background

        mode = Status().get_mode()
        scope = Status().get_scope()

        if scope == StatusScope.HIKE:
            self.leftLabel.setPrimaryText("Hikes")
        elif scope == StatusScope.GLOBAL:
            self.leftLabel.setPrimaryText("Archive")
        self.leftLabel.show()

        if mode == StatusMode.TIME:
            self.centerLabel.setPrimaryText(self.picture.uitime_hrmm)
            self.centerLabel.setSecondaryText(self.picture.uitime_sec)
            self.vlabelCenter.setText(f'{self.picture.uitime_hrmm}{self.picture.uitime_sec}')
        elif mode == StatusMode.ALTITUDE:
            self.centerLabel.setPrimaryText(self.picture.uialtitude)
            self.centerLabel.setSecondaryText('M')
            self.vlabelCenter.setText(f'{self.picture.uialtitude} M')
        elif mode == StatusMode.COLOR:
            # TODO - eventually the color palette will be here, so it'll be blank
            # self.centerLabel.setPrimaryText(self.picture.uitime_hrmm)
            # self.centerLabel.setSecondaryText(self.picture.uitime_sec)
            # self.vlabelCenter.setText(self.picture.uitime_hrmm)
            self.centerLabel.setPrimaryText('')
            self.centerLabel.setSecondaryText('')
            self.vlabelCenter.setText(f'Color Mode')
        self.centerLabel.show()
        self.vlabelCenter.show()  # JAR - I think this might have been part of the issue

        self.rightLabel.setPrimaryText(f"{self.picture.uihike}\n{self.picture.uidate}")
        self.rightLabel.show()

        self.timerFadeOutUI.start(2500)  # wait 1s until you fade out top UI

    def updateUIBottom(self):
        scope = Status().get_scope()
        mode = Status().get_mode()

        if self.preload:
            print('use the preloaded UIData')
            if scope == StatusScope.HIKE:
                hike = self.picture.hike_id 
                rank_timebar = self.sql_controller.ui_get_percentage_in_hike_with_mode('time', self.picture)
                if mode == StatusMode.ALTITUDE:
                    altitudelist = self.uiData.altitudesSortByAltitudeForHike[hike]
                    colorlist = self.uiData.colorSortByAltitudeForHike[hike]
                    rank_colorbar_altgraph = self.sql_controller.ui_get_percentage_in_hike_with_mode('alt', self.picture)
                    self.timebar.trigger_refresh(rank_timebar, False)
                elif mode == StatusMode.COLOR:
                    altitudelist = self.uiData.altitudesSortByColorForHike[hike]
                    colorlist = self.uiData.colorSortByColorForHike[hike]
                    rank_colorbar_altgraph = self.sql_controller.ui_get_percentage_in_hike_with_mode('color', self.picture)
                    self.timebar.trigger_refresh(rank_timebar, False)
                elif mode == StatusMode.TIME:
                    altitudelist = self.uiData.altitudesSortByTimeForHike[hike]
                    colorlist = self.uiData.colorSortByTimeForHike[hike]
                    rank_colorbar_altgraph = rank_timebar
                    self.timebar.trigger_refresh(rank_timebar, True)
            elif scope == StatusScope.GLOBAL:
                rank_timebar = self.sql_controller.ui_get_percentage_in_archive_with_mode('time', self.picture)
                if mode == StatusMode.ALTITUDE:
                    altitudelist = self.uiData.altitudesSortByAltitudeForArchive
                    colorlist = self.uiData.colorSortByAltitudeForArchive
                    rank_colorbar_altgraph = self.sql_controller.ui_get_percentage_in_archive_with_mode('alt', self.picture)
                    self.timebar.trigger_refresh(rank_timebar, False)
                elif mode == StatusMode.COLOR:
                    altitudelist = self.uiData.altitudesSortByColorForArchive
                    colorlist = self.uiData.colorSortByColorForArchive
                    rank_colorbar_altgraph = self.sql_controller.ui_get_percentage_in_archive_with_mode('color', self.picture)
                    self.timebar.trigger_refresh(rank_timebar, False)
                if mode == StatusMode.TIME:
                    altitudelist = self.uiData.altitudesSortByTimeForArchive
                    colorlist = self.uiData.colorSortByTimeForArchive
                    rank_colorbar_altgraph = rank_timebar
                    self.timebar.trigger_refresh(rank_timebar, True)

            self.palette.trigger_refresh(self.picture.colors_rgb, self.picture.colors_conf, True)
            self.colorbar.trigger_refresh(colorlist, True, rank_colorbar_altgraph, self.picture.color_rgb)
            self.altitudegraph.trigger_refresh(altitudelist, True, rank_colorbar_altgraph, self.picture.altitude)

        else:
            print('directly call SQL for the ui data')
            if scope == StatusScope.HIKE:
                rank_timebar = self.sql_controller.ui_get_percentage_in_hike_with_mode('time', self.picture)
                if mode == StatusMode.TIME:
                    self.altitudelist = self.sql_controller.ui_get_altitudes_for_hike_sortby('time', self.picture)
                    self.colorlist = self.sql_controller.ui_get_colors_for_hike_sortby('time', self.picture)
                    rank_colorbar_altgraph = rank_timebar
                    self.timebar.trigger_refresh(rank_timebar, True)
                elif mode == StatusMode.ALTITUDE:
                    self.altitudelist = self.sql_controller.ui_get_altitudes_for_hike_sortby('alt', self.picture)
                    self.colorlist = self.sql_controller.ui_get_colors_for_hike_sortby('alt', self.picture)
                    rank_colorbar_altgraph = self.sql_controller.ui_get_percentage_in_hike_with_mode('alt', self.picture)
                    self.timebar.trigger_refresh(rank_timebar, False)
                elif mode == StatusMode.COLOR:
                    self.altitudelist = self.sql_controller.ui_get_altitudes_for_hike_sortby('color', self.picture)
                    self.colorlist = self.sql_controller.ui_get_colors_for_hike_sortby('color', self.picture)
                    rank_colorbar_altgraph = self.sql_controller.ui_get_percentage_in_hike_with_mode('color', self.picture)
                    self.timebar.trigger_refresh(rank_timebar, False)
            elif scope == StatusScope.GLOBAL:
                rank_timebar = self.sql_controller.ui_get_percentage_in_archive_with_mode('time', self.picture)
                if mode == StatusMode.TIME:
                    self.altitudelist = self.sql_controller.ui_get_altitudes_for_archive_sortby('time')
                    self.colorlist = self.sql_controller.ui_get_colors_for_archive_sortby('time')
                    rank_colorbar_altgraph = rank_timebar
                    self.timebar.trigger_refresh(rank_timebar, True)
                elif mode == StatusMode.ALTITUDE:
                    self.altitudelist = self.sql_controller.ui_get_altitudes_for_archive_sortby('alt')
                    self.colorlist = self.sql_controller.ui_get_colors_for_archive_sortby('alt')
                    rank_colorbar_altgraph = self.sql_controller.ui_get_percentage_in_archive_with_mode('alt', self.picture)
                    self.timebar.trigger_refresh(rank_timebar, False)
                elif mode == StatusMode.COLOR:
                    self.altitudelist = self.sql_controller.ui_get_altitudes_for_archive_sortby('color')
                    self.colorlist = self.sql_controller.ui_get_colors_for_archive_sortby('color')
                    rank_colorbar_altgraph = self.sql_controller.ui_get_percentage_in_archive_with_mode('color', self.picture)
                    self.timebar.trigger_refresh(rank_timebar, False)

            self.palette.trigger_refresh(self.picture.colors_rgb, self.picture.colors_conf, True)
            self.colorbar.trigger_refresh(self.colorlist, True, rank_colorbar_altgraph, self.picture.color_rgb)
            self.altitudegraph.trigger_refresh(self.altitudelist, True, rank_colorbar_altgraph, self.picture.altitude)

    # Hardware Button Presses
    # -------------------------------------------------------------------------

    # Change Scope - Scrollwheel press
    def pressed_encoder(self, result):
        print('Encoder button was pressed: %d' % result)
        self.control_scope()

    # Change Mode - Time, Altitude, Color
    def pressed_mode(self, result):
        print('Mode button was pressed: %d' % result)
        self.control_mode()

    # Skip Buttons
    def pressed_next(self, result):
        print('Next button was pressed: %d' % result)
        self.control_skip_next()

    def pressed_prev(self, result):
        print('Previous button was pressed: %d' % result)
        self.control_skip_previous()

    # Play / Pause
    def pressed_play_pause(self, result):
        print('Play Pause button was pressed: %d' % result)
        self.control_play_pause()

    # Accelerometer
    def changed_accelerometer(self, result):
        print('Result from accelerometer mate: %d' % result)
        if result == StatusOrientation.LANDSCAPE:
            self.control_landscape()
        elif result == StatusOrientation.PORTRAIT:
            self.control_vertical()

    # Hall Effect
    def pressed_hall_effect(self, result):
        print('Hall Effect was pressed: %d' % result)

    # Keyboard Presses
    # -------------------------------------------------------------------------
    def keyPressEvent(self, event):
        # Closing App
        if event.key() == Qt.Key_Escape:
            self.close()

        # Scroll Wheel
        elif event.key() == Qt.Key_Right:
            self.control_next()
        elif event.key() == Qt.Key_Left:
            self.control_previous()

        # Skip Buttons
        elif event.key() == Qt.Key_Up:
            self.control_skip_next()
        elif event.key() == Qt.Key_Down:
            self.control_skip_previous()

        # Change Mode - Time, Altitude, Color
        elif event.key() == Qt.Key_M:
            self.control_mode()

        # Change Scope - Scrollwheel press
        elif event.key() == Qt.Key_Shift:
            self.control_scope()

        # Play/Pause
        elif event.key() == Qt.Key_Space:
            self.control_play_pause()

        # Change Orientation
        elif event.key() == Qt.Key_L:
            self.control_landscape()
        elif event.key() == Qt.Key_V:
            self.control_vertical()

        # Increase/Decrease speed
        elif event.key() == Qt.Key_Equal:
            self.control_speed_faster()
        elif event.key() == Qt.Key_Minus:
            self.control_speed_slower()

        # Testing
        elif event.key() == Qt.Key_F:
            print(f"Id: {self.picture.picture_id} | Hike: {self.picture.hike_id}")
            # print('time to fade!')
            # self.vlabelCenter.fadeOut(1000)
            # self.palette.fadeOut(2000)
            # self.timebar.fadeOut(2500)
            # self.colorbar.fadeOut(2000)
        elif event.key() == Qt.Key_W:
            print('W')
            self.loopThroughAllPictures()
        else:
            print(event.key())

    # Helper Functions for keyboard / hardware controls
    # -------------------------------------------------------------------------
    def control_mode(self):
        '''Changes the mode: Time -> Color -> Altitude ->'''
        print('Mode change')
        self.changeMode()
        self.updateScreen()

    def control_scope(self):
        '''Changes the scope: Hike -> Archive ->'''
        print('Shift Archive / Hike')
        Status().change_scope()
        self.updateScreen()

    def control_next(self):
        '''Mac App only: move to next photo (arrow keys)'''
        pass
        # TODO - see how this affects the Mac App
        # The logic in here was moved to ImageBlender. Will likely need to update
        # rotaryCount from the keyboard input
        # self.updateScreen()

    def control_previous(self):
        '''Mac App only: move to previous photo (arrow keys)'''
        pass
        # TODO - see how this affects the Mac App
        # The logic in here was moved to ImageBlender. Will likely need to update
        # rotaryCount from the keyboard input
        # self.updateScreen()

    def control_skip_next(self):
        '''Tells the ImageBlender thread to skip next'''
        Status().set_pause()  # Causes the PlayPause thread to not increment the rotary counter
        self.imageBlender.skipNext()
        # self.updateScreen()

    def control_skip_previous(self):
        '''Tells the ImageBlender thread to skip previous'''
        Status().set_pause()  # Causes the PlayPause thread to not increment the rotary counter
        self.imageBlender.skipPrev()
        # self.updateScreen()

    def control_play_pause(self):
        '''Changes StatusPlayPause(). PlayPauseThread continually checks this status'''
        print('Space - Play/Pause')
        Status().change_playpause()

    def control_landscape(self):
        '''Changes the orientation to landscape'''
        print('setLandscape')
        self.setLandscape()

    def control_vertical(self):
        '''Changes the orientation to vertical'''
        print('setVertical')
        self.setVertical()

    def control_speed_slower(self):
        '''Mac App only: decreases skip size for keyboard'''
        print('-- Scroll Speed')
        self.scrollspeed = int(self.scrollspeed / 2)
        if self.scrollspeed < 1:
            self.scrollspeed = 1
        self.scrollSpeedLabel.setText(f'{self.scrollspeed}x')
        # print(self.scrollspeed)

    def control_speed_faster(self):
        '''Mac App only: increases skip size for keyboard'''
        print('++ Scroll Speed')
        self.scrollspeed = int(self.scrollspeed * 2)
        if self.scrollspeed > 256:
            self.scrollspeed = 256
        self.scrollSpeedLabel.setText(f'{self.scrollspeed}x')
        # print(self.scrollspeed)

    # Testing
    # -------------------------------------------------------------------------
    def loopThroughAllPictures(self):
        while True:
            self.control_next()
            # time.sleep(2.0)

    # Memory usage in kB
    def printCurrentMemoryUsage(self):
        process = psutil.Process(os.getpid())
        print('Memory Used:')
        print(process.memory_info().rss / 1024 ** 2)  # in bytes


if __name__ == '__main__':
    app = QApplication(sys.argv)

    # screen = app.primaryScreen()
    # print('Screen: %s' % screen.name())
    # size = screen.size()
    # print('Size: %d x %d' % (size.width(), size.height()))
    # rect = screen.availableGeometry()
    # print('Available: %d x %d' % (rect.width(), rect.height()))

    window = MainWindow()

    if platform.system() == 'Darwin' or platform.system() == 'Windows':
        window.show()
    elif platform.system() == 'Linux':
        # window.showFullScreen()
        window.show()

    sys.exit(app.exec_())
