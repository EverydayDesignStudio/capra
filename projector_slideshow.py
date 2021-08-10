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
# from lsm303d import LSM303D
from datetime import datetime
from enum import IntEnum, unique, auto

from classes.capra_data_types import Picture, Hike
from classes.sql_controller import SQLController
# from classes.sql_statements import SQLStatements
from classes.ui_components import *
from classes.singleton import Singleton

# PIN and Settings values are stored here
import globals as g
g.init()
print('projector_slideshow.py running...')


# Filewide Statuses
# ----- Hardware -----
rotaryCounter = 0
rotaryCounterLast = 0
isReadyForNewPicture = True


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
    __order__ = 'TIME ALTITUDE COLOR'
    TIME = 0
    ALTITUDE = 1
    COLOR = 2


# Singleton Status class
class Status(Singleton):
    """
    Singleton class containing all status variables for the slideshow
    • orientation, playpause, scope, mode
    """

    # Class variables, not instance variables
    _orientation = StatusOrientation.LANDSCAPE
    _playpause = StatusPlayPause.PAUSE
    _scope = StatusScope.HIKE
    _mode = StatusMode.TIME

    # Eventually maybe we would need to setup this with input from the database
    def __init__(self):
        super().__init__()

    # Mode
    def get_mode(self) -> StatusMode:
        return Status()._mode

    def next_mode(self):
        Status()._mode = StatusMode((Status()._mode + 1) % 3)

    # Scope
    def get_scope(self) -> StatusScope:
        return Status()._scope

    def change_scope(self):
        Status()._scope = StatusScope((Status()._scope + 1) % 2)

    # Play Pause
    def get_playpause(self) -> StatusPlayPause:
        return Status()._playpause

    def change_playpause(self):
        Status()._playpause = StatusPlayPause((Status()._playpause + 1) % 2)

    # Orientation
    def get_orientation(self) -> StatusOrientation:
        return Status()._orientation

    def change_orientation(self):
        Status()._orientation = StatusOrientation((Status()._orientation + 1) % 2)

    def set_orientation_landscape(self):
        Status()._orientation = StatusOrientation.LANDSCAPE

    def set_orientation_vertical(self):
        Status()._orientation = StatusOrientation.PORTRAIT


# Global status values -- they need to have global file scope due to the modification by the hardware
orientation = StatusOrientation.LANDSCAPE
scope = StatusScope.HIKE
mode = StatusMode.TIME
playpause = StatusPlayPause.PLAY


# Threads
# -----------------------------------------------------------------------------

# Threading Infrastructure
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


# Custom Hardware Controls
class RotaryEncoder(QRunnable):
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
                rotaryCounter = rotaryCounter + 1 * self.multFactor
            else:
                rotaryCounter = rotaryCounter - 1 * self.multFactor

            self.Last_Direction = self.Current_Direction
            print('rotaryCounter: {g}, diff_time: {d:.4f}, speed: {s:.2f}, MultFactor: {a:.2f} ({st})'.format(g=rotaryCounter, d=self.dt, s=speed, a=self.multFactor, st=self.speedText))

            # TODO -- remove both of these lines
            # Resetting counter will happen in Main UI Thread
            # rotaryCounter = 0

            self.signals.result.emit(rotaryCounter)

    def clear(self, ev=None):
        global rotaryCounter
        rotaryCounter = 0
        print('rotaryCounter = {g}'.format(g=rotaryCounter))
        time.sleep(1)

    def run(self):
        while True:
            self.rotaryTurn()


# Uses global status variable to ensure there are no double presses for hardware buttons
class HardwareButton(QRunnable):
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


# Continually tries blending the next image into the current image
class ImageBlender(QRunnable):
    def __init__(self, sql_cntrl, current1_path, current2_path, current3_path, currentf_path, *args, **kwargs):
        super(ImageBlender, self).__init__()

        # TODO - a SQLCntrl is needed in this thread to properly work for Raspberry Pi
        # self.sql_controller2 = SQLController(database=DB, system=platform.system())
        # self.picture = self.sql_controller2.get_first_time_picture()
        # self.picture = self.sql_controller2.get_picture_with_id(9000)
        # self.picture.print_obj_mvp()

        # TODO - verify on Pi that this works instead of the above version
        self.sql_controller2 = sql_cntrl
        print(f'in ImageBlender: {self.sql_controller2}')
        # test_pic = self.sql_controller2.get_picture_with_id(9000)
        # print(test_pic)

        # Needed setup
        self.alpha = 0
        self.signals = WorkerSignals()
        self.currentf_raw = Image.open(currentf_path, 'r')
        self.nextf_raw = Image.open(currentf_path, 'r')
        # self.current1_raw = Image.open(current1_path, 'r')
        # self.next1_raw = Image.open(current1_path, 'r')
        # self.current2_raw = Image.open(current2_path, 'r')
        # self.next2_raw = Image.open(current2_path, 'r')
        # self.current3_raw = Image.open(current3_path, 'r')
        # self.next3_raw = Image.open(current3_path, 'r')

        self.p1 = current1_path
        self.p2 = current2_path
        self.p3 = current3_path

        # print(self.currentf_raw)
        # print(self.current1_raw)
        # print(self.current2_raw)
        # print(self.current3_raw)

        # REMOVE - this is just for testing
        self.text_current = 'currently'
        self.text_next = 'nextly'
        self.next_value = 0
        self.inside_data = 'shhhh, it is a secret'

    def increment_next(self):
        self.next_value += 1

    # Receives a new "next image" which is consequently blended into the current
    # image. If this process happens in the middle of a blend, then the new image
    # will be blended into this already blended together photo
    def set_next_images(self, path1, path2, path3, pathf):
        global isReadyForNewPicture

        # nextf_raw = Image.open(pathf, 'r')
        # try:
        #     print('try:')
        #     isReadyForNewPicture = True
        #     self.nextf_raw = nextf_raw
        # finally:
        #     print('finally:')

        self.nextf_raw = Image.open(pathf, 'r')
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
        self.p1 = path1
        self.p2 = path2
        self.p3 = path3

        self.alpha = 0.25

    # Continually runs blending together
    def run(self):
        while True:
            global rotaryCounter
            global rotaryCounterLast

            change = rotaryCounter - rotaryCounterLast
            # print(change)

            # NOTE: this local version of SQLController will only be called if the rotary encoder 
            # is changing, otherwise it simply blends the image if alpha is < 0.75
            if change > 0:
                print('POSITIVE')
                print(change)
                rotaryCounterLast = rotaryCounter
                self.picture = self.sql_controller2.get_next_time_in_hikes(self.picture, change)
                self.signals.result.emit(self.picture)
                print(self.picture.cameraf)
                self.nextf_raw = Image.open(self.picture.cameraf, 'r')
                self.alpha = 0.25
            elif change < 0:
                print('NEGATIVE')
                print(change)
                rotaryCounterLast = rotaryCounter
                self.picture = self.sql_controller2.get_previous_time_in_hikes(self.picture, abs(change))
                self.signals.result.emit(self.picture)
                print(self.picture.cameraf)
                self.nextf_raw = Image.open(self.picture.cameraf, 'r')
                self.alpha = 0.25

            if self.alpha < 0.75:
                self.currentf_raw = Image.blend(self.currentf_raw, self.nextf_raw, self.alpha)

                # TODO
                # self.current1_raw = Image.blend(self.current1_raw, self.next1_raw, self.alpha)
                # self.current2_raw = Image.blend(self.current2_raw, self.next2_raw, self.alpha)
                # self.current3_raw = Image.blend(self.current3_raw, self.next3_raw, self.alpha)

                # Increments the alpha, so the image will slowly blend
                # self.alpha += 0.1
                self.alpha += 0.025  # Rougly 20 frames until the old picture is blurred out
                # self.alpha += 0.04

                # BUG - This is causing the issues around paintEvent() being over called
                # Anytime a widget is updated, all widgets update, and this will emit 20-30xs
                # Which causes a repaint of all widgets each time
                self.signals.results.emit(self.p1, self.p2, self.p3, self.currentf_raw)

                # self.signals.results.emit(self.current1_raw, self.current2_raw, self.current3_raw, self.currentf_raw)
                if self.alpha >= 0.75:
                    self.signals.finished.emit()
            time.sleep(0.1)  # 1/20frames = 0.05


class MainWindow(QMainWindow):
    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)

        # Test counter variable to see the frame rate
        self.blendCount = 0

        self.setupDB()  # Mac or Windows shows the database dialog
        self.setupWindowLayout()
        self.setupUI()
        self.setupSoftwareThreads()

        if platform.system() == 'Linux':
            self.setupGPIO()
            self.setupHardwareThreads()

        # REVIEW - not having this may cause a crash
        # Updates the UI's picture for the first time
        # self.updateImages()

    # Setup Helpers
    # -------------------------------------------------------------------------

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
        self.picture = self.sql_controller.get_picture_with_id(1)

        self.scrollspeed = 1

    # Setup the window size, title, and container layout
    def setupWindowLayout(self):
        self.setWindowTitle("Capra Explorer Slideshow")
        self.setGeometry(0, 300, 1280, 720)
        # self.setStyleSheet("background-color: gray;")

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
        self.modeOverlay = UIModeOverlay(self, 'assets/Time@1x.png', mode)

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

        # ImageFader, sends 2 callbacks
        # results()    : at ever frame that finished a blend
        # finished()  : when blending has finished blending two the two images,
        #               sends callback to notify the fade out of UI elements
        self.imageBlender = ImageBlender(self.sql_controller, self.picture.camera1, self.picture.camera2, self.picture.camera3, self.picture.cameraf)

        # TODO - figure out the fading of vertical images
        # self.imageBlender.signals.result.connect(self._load_new_row)

        # TODO - paintEvent issue: following the path
        self.imageBlender.signals.results.connect(self._load_new_images)
        # self.imageBlender.signals.results.connect(self._poop)

        self.imageBlender.signals.finished.connect(self._finished_image_blend)
        self.threadpoolSoftware.start(self.imageBlender)

    def _poop(self):
        pass
        # print('poop')

    # Setup hardware pins
    def setupGPIO(self):
        # Set the GPIO mode, alternative is GPIO.BOARD
        GPIO.setmode(GPIO.BCM)

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
        self.PIN_NEOPIXELS = g.NEO1

        # LED indicators
        self.PIN_LED_WHITE1 = g.WHITE_LED1
        self.PIN_LED_WHITE2 = g.WHITE_LED2
        self.PIN_LED_WHITE3 = g.WHITE_LED3

        self.PIN_LED_RGB_RED = g.RGB2_RED
        self.PIN_LED_RGB_GREEN = g.RGB2_GREEN
        self.PIN_LED_RGB_BLUE = g.RGB2_BLUE

        self.PIN_LED_TEST_RED = g.RGB1_RED
        self.PIN_LED_TEST_GREEN = g.RGB1_GREEN
        # self.PIN_LED_TEST_BLUE = 0

    # Setup threads to check for hardware changes
    def setupHardwareThreads(self):
        self.threadpool = QThreadPool()
        self.threadpool.setMaxThreadCount(7)  # TODO - change if more threads are needed

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

    # UI Callbacks from bg threads
    # -------------------------------------------------------------------------

    # Loads the newly blended image from the background thread into the UIImages on the MainWindow
    def _load_new_images(self, image1, image2, image3, imagef):
        """image 1, 2, 3 are strings to the path location
        imagef is an raw Image.open()"""

        # Test variable to show how many times it blends the two images
        # not necessarily in 1 second though
        self.blendCount += 1

        # BUG - paintEvent issue: following the path. Does this change it?
        # Adjusting any Widget (even a QLabel) is causing all the widgets to repaint
        self.pictureLandscape.update_pixmap(imagef)

        # Forget what the status of these were
        # self.pictureVertical1 = UIImage(self.picture.camera1)
        # self.pictureVertical2 = UIImage(self.picture.camera2)
        # self.pictureVertical3 = UIImage(self.picture.camera3)

        # Just sets the picture, no blending
        self.pictureVertical1.update_image(image1)
        self.pictureVertical2.update_image(image2)
        self.pictureVertical3.update_image(image3)

        # TODO - get it so the blending works for vertical pictures as well
        # FIXME - there is an issue with how update_pixmap is loading the images
        #         for some weird reason, when it is vertical, it ends up with that distortion
        # self.pictureVertical1.update_pixmap(image1)
        # self.pictureVertical2.update_pixmap(image2)
        # self.pictureVertical3.update_pixmap(image3)

    def _load_new_row(self, picture: Picture):
        """Receives a new picture from the database"""
        # print(picture)
        self.picture = picture
        print(self.picture.picture_id)

    # The new image has finished blending; now fade out the UI components
    def _finished_image_blend(self):
        # REMOVE - Remove this testing setup for checking the number of blends
        # print('\ndef finished_image_blend() -- result emitted')
        # print('FINISHED Blending')

        print('Blended {b}xs\n'.format(b=self.blendCount))
        self.blendCount = 0

        # HACK - that almost works. However the widget is still being wiped off the screen, 
        # then reapinted after the fading
        self.palette.setCanRepaint()

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
        elif mode == StatusMode.ALTITUDE:
            self.modeOverlay.setAltitude()
        elif mode == StatusMode.COLOR:
            self.modeOverlay.setColor()

    def changeScope(self):
        # print('changeScope()')
        Status().change_scope()
        # print(Status().get_scope())

    def setLandscape(self):
        print('setLandscape()')
        Status().set_orientation_landscape()
        self.stacklayout.setCurrentIndex(Status().get_orientation())

        self.portraitUIContainerTop.hide()
        self.bottomUIContainer.show()

        self.leftLabel.show()
        self.centerLabel.show()
        self.rightLabel.show()

    def setVertical(self):
        print('setVertical()')
        Status().set_orientation_vertical()
        self.stacklayout.setCurrentIndex(Status().get_orientation())

        self.portraitUIContainerTop.show()
        self.bottomUIContainer.hide()

        self.leftLabel.hide()
        self.centerLabel.hide()
        self.rightLabel.hide()

    # Update the Screen
    # -------------------------------------------------------------------------
    # A slow and inefficient, but good base case for updating the UI on the screen
    def updateScreen(self):
        # self.picture.print_obj()
        # self.printCurrentMemoryUsage()
        self.updateImages()
        self.updateUITop()
        self.updateUIBottom()

    # TODO - still need to have multiple blending images
    def updateImages(self):
        # Somewhere along this chain, all the paintEvents are called
        # self.imageBlender.set_next_images(self.picture.camera1, self.picture.camera2, self.picture.camera3, self.picture.cameraf)

        # TODO on Pi -  tes to see if not having the imageBlender makes it refresh faster
        self.nextf_raw = Image.open(self.picture.cameraf, 'r')
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

    # NOTE: - currently not used!
    def updateUIIndicatorsBottom(self):
        # TODO 
        # self.timerFadeOutUI.stop()  # stops timer which calls _fadeOutUI()

        scope = Status().get_scope()
        mode = Status().get_mode()


        # rank_time = int(self.picture.index_in_hike)/self.sql_controller.get_hike_size(self.picture)
        # rank_alt = int(self.picture.altrank_hike)/self.sql_controller.get_hike_size(self.picture)
        # rank_color = int(self.picture.colorrank_hike)/self.sql_controller.get_hike_size(self.picture)

        # if mode == StatusMode.TIME:
        #     rank = int(self.picture.index_in_hike)/self.sql_controller.get_hike_size(self.picture)
        # elif mode == StatusMode.ALTITUDE:
        #     rank = int(self.picture.altrank_hike)/self.sql_controller.get_hike_size(self.picture)
        # elif mode == StatusMode.COLOR:
        #     rank = int(self.picture.colorrank_hike)/self.sql_controller.get_hike_size(self.picture)

        # TODO - have a function to only update the indicators, not redraw the entire widget!
        self.palette.trigger_refresh(self.picture.colors_rgb, self.picture.colors_conf, True)
        self.timebar.trigger_refresh(rank_time, True)
        self.colorbar.trigger_refresh(self.colorlist, True, rank_color, self.picture.color_rgb)

        # self.palette.show()
        # self.timebar.show()
        # self.colorbar.show()

        # TODO -- I might need to put all the UI fading stuff in 1 single function
        # self.timerFadeOutUI.start(2500)  # wait 1s until you fade out top UI

    def updateUIBottom(self):
        scope = Status().get_scope()
        mode = Status().get_mode()

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

    # TODO - test this code on the Pi
    # REMOVE & NOTE: this is where the bottleneck was occuring
    # Was spawning a new instance of the method each time the rotary changed
    def rotary_changed(self, result):
        print('rotary_changed() result: {r}'.format(r=result))
        # self.picture.print_obj()

        global isReadyForNewPicture

        if isReadyForNewPicture:
            # HACK Only allow this image to be blended
            isReadyForNewPicture = True

            # print('ready for new picture')
            if result > 0:
                # print('Next: %d' % result)
                self.picture = self.sql_controller.get_next_time_in_hikes(self.picture, result)
            elif result < 0:
                # print('Previous: %d' % result)
                self.picture = self.sql_controller.get_previous_time_in_hikes(self.picture, abs(result))

            # HACK - Clears the rotaryEncoder thread's counter since the count has
            # been used in a database call. Otherwise, we want the count to be maintained
            print('about to call clear()')
            self.rotaryEncoder.clear()

            global rotaryCounter
            print(rotaryCounter)

            self.updateImages()
            self.updateUITop()

        # TODO - add check to see if moved to a new hike during rotary turn

        # change = rotaryCounter - rotaryCounterLast
        # print(change)
        # print('\n')

    def pressed_encoder(self, result):
        print('Encoder button was pressed: %d' % result)

    def pressed_mode(self, result):
        print('Mode button was pressed: %d' % result)
        self.control_mode()

    def pressed_next(self, result):
        print('Next button was pressed: %d' % result)

    def pressed_prev(self, result):
        print('Previous button was pressed: %d' % result)

    def pressed_play_pause(self, result):
        print('Play Pause button was pressed: %d' % result)

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
        print('Mode change')
        self.changeMode()
        self.updateScreen()

    def control_scope(self):
        print('Shift Archive / Hike')
        self.changeScope()
        self.updateScreen()

    def control_next(self):
        mode = Status().get_mode()
        scope = Status().get_scope()
        currentHike = self.picture.hike_id
        if scope == StatusScope.HIKE:
            if mode == StatusMode.TIME:
                self.picture = self.sql_controller.get_next_time_in_hikes(self.picture, self.scrollspeed)
            elif mode == StatusMode.ALTITUDE:
                self.picture = self.sql_controller.get_next_altitude_in_hikes(self.picture, self.scrollspeed)
            elif mode == StatusMode.COLOR:
                self.picture = self.sql_controller.get_next_color_in_hikes(self.picture, self.scrollspeed)

            if self.picture.hike_id != currentHike:
                print('🧨🧨🧨 NEXT - NEW HIKE! 🧨🧨🧨')
                # self.updateScreenHikesNewHike()
            # else:
                # self.updateScreenHikesNewPictures()
        elif scope == StatusScope.GLOBAL:
            if mode == StatusMode.TIME:
                self.picture = self.sql_controller.get_next_time_in_global(self.picture, self.scrollspeed)
            elif mode == StatusMode.ALTITUDE:
                self.picture = self.sql_controller.get_next_altitude_in_global(self.picture, self.scrollspeed)
            elif mode == StatusMode.COLOR:
                self.picture = self.sql_controller.get_next_color_in_global(self.picture, self.scrollspeed)

            # self.updateScreenArchive()  # TODO - function still needs to be coded
        self.updateScreen()

    def control_previous(self):
        mode = Status().get_mode()
        scope = Status().get_scope()
        currentHike = self.picture.hike_id
        if scope == StatusScope.HIKE:
            if mode == StatusMode.TIME:
                self.picture = self.sql_controller.get_previous_time_in_hikes(self.picture, self.scrollspeed)
            elif mode == StatusMode.ALTITUDE:
                self.picture = self.sql_controller.get_previous_altitude_in_hikes(self.picture, self.scrollspeed)
            elif mode == StatusMode.COLOR:
                self.picture = self.sql_controller.get_previous_color_in_hikes(self.picture, self.scrollspeed)

            if self.picture.hike_id != currentHike:
                print('🧨🧨🧨 PREVIOUS - NEW HIKE! 🧨🧨🧨')
                # self.updateScreenHikesNewHike()
            # else:
                # self.updateScreenHikesNewPictures()
        elif scope == StatusScope.GLOBAL:
            if mode == StatusMode.TIME:
                self.picture = self.sql_controller.get_previous_time_in_global(self.picture, self.scrollspeed)
            elif mode == StatusMode.ALTITUDE:
                self.picture = self.sql_controller.get_previous_altitude_in_global(self.picture, self.scrollspeed)
            elif mode == StatusMode.COLOR:
                self.picture = self.sql_controller.get_previous_color_in_global(self.picture, self.scrollspeed)

            # self.updateScreenArchive()  # TODO - still needs to be coded
        self.updateScreen()

    def control_skip_next(self):
        # print('Next Button')
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
        self.updateScreen()

    def control_skip_previous(self):
        # print('Previous Button')
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
        self.updateScreen()

    def control_play_pause(self):
        print('Space - Play/Pause')
        Status().change_playpause()
        status = Status().get_playpause()

        if status == StatusPlayPause.PLAY:
            print('Start Playing')
        elif status == StatusPlayPause.PAUSE:
            print('Pause the Program')

    def control_landscape(self):
        print('setLandscape')
        self.setLandscape()

    def control_vertical(self):
        print('setVertical')
        self.setVertical()

    def control_speed_slower(self):
        print('-- Scroll Speed')
        self.scrollspeed = int(self.scrollspeed / 2)
        if self.scrollspeed < 1:
            self.scrollspeed = 1
        self.scrollSpeedLabel.setText(f'{self.scrollspeed}x')
        # print(self.scrollspeed)

    def control_speed_faster(self):
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
        window.showFullScreen()
        # window.show()

    sys.exit(app.exec_())
