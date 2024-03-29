#!/usr/bin/env python3

import platform, sys, math, time
from sqlite3.dbapi2 import connect
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *

from classes.capra_data_types import Picture, Hike
from classes.sql_controller import SQLController
from classes.ui_components import *

import globals as g
g.init()

global globalPicture


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
    '''
    finished = pyqtSignal()
    error = pyqtSignal(tuple)
    result = pyqtSignal(object)
    '''
    Defines status which is checked for in infinite loop
    By setting to True, the thread will quit,
    and closing of the program won't hang
    '''
    terminate = False


class NewPictureThread(QRunnable):
    '''Thread to continually get a new Picture from the database; simulates the transfer script'''
    def __init__(self, sql_cntrl: SQLController, *args, **kwargs):
        super(NewPictureThread, self).__init__()
        self.signals = WorkerSignals()  # Holds a terminate status, used to kill thread

        # Holds an instance of the SQLController
        self.sql_controller = sql_cntrl

        # TODO - could also use WorkerSignals as a way to tell MainWindow about new Picture
        # self.signals = WorkerSignals()

    def run(self):
        while True:
            if self.signals.terminate:  # Garbage collection
                break

            global globalPicture
            globalPicture = self.sql_controller.get_random_picture()
            time.sleep(3)  # TODO - test options; maybe 30s in real program


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Capra Transfer Animation")
        self.setGeometry(0, 0, 1280, 720)

        # Setups up database connection depending on the system
        self.setupSQLController()

        # Setup Bg Thread for getting picture from Database
        self.threadpool = QThreadPool()
        self.threadpool.setMaxThreadCount(1)
        self.newPictureThread = NewPictureThread(self.sql_controller)
        self.threadpool.start(self.newPictureThread)

        # Setup BG color
        # c1 = QColor(9, 24, 94, 255)
        self.bgcolor = BackgroundColor(self, QVBoxLayout(), Qt.AlignBottom, self.picture.color_rgb)

        self.setupColorWidgets(self.picture)
        self.setupAltitudeLabel(self.picture)
        self.setupTimeLabelAndBar(self.picture)

        self.superCenterImg = TransferCenterImage(self, self.picture)

        self.setupAltitudeGraphAndLine(self.picture)
        self.altitudegraph.hide()
        self.centerLabel.opacityHide()
        self.line.hide()

        # Setup QTimer for checking for new Picture
        self.handlerCounter = 1
        self.timerAnimationHandler = QTimer()
        self.timerAnimationHandler.timeout.connect(self.animationHandler)
        self.timerAnimationHandler.start(7000)

    def animationHandler(self):
        self.fadeOutTimer = QTimer()
        self.fadeOutTimer.setSingleShot(True)

        if self.handlerCounter % 4 == 1:  # Color
            self.fadeMoveInColorWidgets()
            self.fadeOutTimer.timeout.connect(self.fadeMoveOutColorWidgets)
        elif self.handlerCounter % 4 == 2:  # Altitude
            self.fadeMoveInAltitudeEverything()
            self.fadeOutTimer.timeout.connect(self.fadeMoveOutAltitudeEverything)
        elif self.handlerCounter % 4 == 3:  # Time
            self.fadeMoveInTime()
            self.fadeOutTimer.timeout.connect(self.fadeMoveOutTime)
        elif self.handlerCounter % 4 == 0:  # New Picture: image, bg color, ui elements
            global globalPicture
            self.picture = globalPicture

            # Update UI Elements
            self.updateColorWidgets(self.picture)
            self.updateTimeLabelAndBar(self.picture)
            self.updateAltitudeLabelAndGraph(self.picture)
            # self.setupTimeLabelAndBar(self.picture)
            # self.setupAltitudeLabel(self.picture)

            # Change Image and Background
            self.superCenterImg.fadeNewImage(self.picture)
            self.bgcolor.changeColor(self.picture.color_rgb)

        self.fadeOutTimer.start(3500)
        self.handlerCounter += 1

    # Database connection - previous db with UI data
    def setupSQLController(self):
        '''Initializes the database connection.\n
        If on Mac/Windows give dialog box to select database,
        otherwise it will use the global defined location for the database'''

        # Mac/Windows: select the location
        if platform.system() == 'Darwin' or platform.system() == 'Windows':
            # filename = QFileDialog.getOpenFileName(self, 'Open file', '', 'Database (*.db)')
            # self.database = filename[0]
            # self.directory = os.path.dirname(self.database)

            self.database = '/Users/Jordan/Dropbox/Everyday Design Studio/A Projects/100 Ongoing/Capra/capra-storage/capra-storage-jordan-projector/capra_projector_jun2021_min_test_0708.db'
            self.directory = '/Users/Jordan/Dropbox/Everyday Design Studio/A Projects/100 Ongoing/Capra/capra-storage/capra-storage-jordan-projector'
        else:  # Raspberry Pi: preset location
            self.database = g.DATAPATH_PROJECTOR + g.DBNAME_MASTER
            self.directory = g.DATAPATH_PROJECTOR

        print(self.database)
        print(self.directory)
        self.sql_controller = SQLController(database=self.database, directory=self.directory)

        # self.picture = self.sql_controller.get_picture_with_id(20000) # 28300
        self.picture = self.sql_controller.get_random_picture()

        # self.picture2 = self.sql_controller.get_picture_with_id(27500)
        # self.picture3 = self.sql_controller.get_picture_with_id(12000)
        # self.picture4 = self.sql_controller.get_picture_with_id(10700)
        # 10700, 11990, 12000, 15000, 20000, 27100, 27200, 27300, 27500, 28300

        # TODO - should we preload all the UI Data?
        # self.uiData = self.sql_controller.preload_ui_data()
        # self.preload = True

    # Time Mode
    def setupTimeLabelAndBar(self, picture: Picture):
        self.timeLabel = UILabelTopCenter(self, '', '')
        self.timeLabel.setPrimaryText(picture.uitime_hrmm)
        self.timeLabel.setSecondaryText(picture.uitime_ampm)

        percent_rank = self.sql_controller.ui_get_percentage_in_archive_with_mode('time', self.picture)
        self.timebar = TimeBarTransfer(self, percent_rank)

        self.timeLabel.opacityHide()
        self.timebar.hide()

    def updateTimeLabelAndBar(self, picture: Picture):
        self.timeLabel.setPrimaryText(picture.uitime_hrmm)
        self.timeLabel.setSecondaryText(picture.uitime_ampm)

        percent_rank = self.sql_controller.ui_get_percentage_in_archive_with_mode('time', self.picture)
        self.timebar.trigger_refresh(percent_rank)

    def fadeMoveInTime(self):
        self.timeLabel.show()
        self.timebar.show()

        # Move in top label
        self.animMoveInTimeLabel = QPropertyAnimation(self.timeLabel, b"geometry")
        self.animMoveInTimeLabel.setDuration(2000)
        self.animMoveInTimeLabel.setStartValue(QRect(0, 360, 1280, 110))
        self.animMoveInTimeLabel.setEndValue(QRect(0, 15, 1280, 110))
        self.animMoveInTimeLabel.start()

        # Fade in the timebar
        fadeTimebar = QGraphicsOpacityEffect()
        self.timebar.setGraphicsEffect(fadeTimebar)
        self.animFadeInAltitudeGraph = QPropertyAnimation(fadeTimebar, b"opacity")
        self.animFadeInAltitudeGraph.setStartValue(0)
        self.animFadeInAltitudeGraph.setEndValue(1)
        self.animFadeInAltitudeGraph.setDuration(2000)
        self.animFadeInAltitudeGraph.start()

        self.update()

    def fadeMoveOutTime(self):
        # Move out time label
        self.animMoveOutTimeLabel = QPropertyAnimation(self.timeLabel, b"geometry")
        self.animMoveOutTimeLabel.setDuration(2000)
        self.animMoveOutTimeLabel.setStartValue(QRect(0, 15, 1280, 110))
        self.animMoveOutTimeLabel.setEndValue(QRect(0, 360, 1280, 110))
        self.animMoveOutTimeLabel.start()

        # Fade out time label - issue with interferring with other effects
        # fadeOutTimeLabel = QGraphicsOpacityEffect()
        # self.timeLabel.setGraphicsEffect(fadeOutTimeLabel)
        # self.animFadeOutTimeLabel = QPropertyAnimation(fadeOutTimeLabel, b"opacity")
        # self.animFadeOutTimeLabel.setStartValue(1)
        # self.animFadeOutTimeLabel.setEndValue(0)
        # self.animFadeOutTimeLabel.setDuration(2000)
        # self.animFadeOutTimeLabel.start()

        # Fade out the timebar
        fadeTimebar = QGraphicsOpacityEffect()
        self.timebar.setGraphicsEffect(fadeTimebar)
        self.animFadeOutAltitudeGraph = QPropertyAnimation(fadeTimebar, b"opacity")
        self.animFadeOutAltitudeGraph.setStartValue(1)
        self.animFadeOutAltitudeGraph.setEndValue(0)
        self.animFadeOutAltitudeGraph.setDuration(2000)
        self.animFadeOutAltitudeGraph.start()

        self.update()

    # Altitude Mode
    def setupAltitudeLabel(self, picture: Picture):
        self.centerLabel = UILabelTopCenter(self, '', 'M')
        self.centerLabel.setPrimaryText(picture.uialtitude)

    def setupAltitudeGraphAndLine(self, picture: Picture):
        archiveSize = self.sql_controller.get_archive_size()
        idxList = self.sql_controller.chooseIndexes(int(archiveSize), 1280.0)
        altitudelist = self.sql_controller.ui_get_altitudes_for_archive_sortby('alt', idxList)

        currentAlt = picture.altitude

        altitudelist.insert(0, currentAlt)  # Append the new altitude at the start of the list
        altitudelist = sorted(altitudelist)  # Sorts so the altitude will fit within the correct spot on the graph

        self.altitudegraph = AltitudeGraphTransferQWidget(self, True, altitudelist, currentAlt)
        self.altitudegraph.setGraphicsEffect(UIEffectDropShadow())

        MINV = min(altitudelist)
        MAXV = max(altitudelist)
        H = 500
        self.linePosY = 108 + H - ( ((currentAlt - MINV)/(MAXV-MINV)) * (H-3) )
        # print(self.linePosY)

        self.line = QLabel("line", self)
        bottomImg = QPixmap("assets/line.png")
        self.line.setPixmap(bottomImg)
        self.line.setAlignment(Qt.AlignCenter)

        self.line.setGeometry(0, int(self.linePosY), 1280, 3)

    def updateAltitudeLabelAndGraph(self, picture: Picture):
        self.centerLabel.setPrimaryText(picture.uialtitude)
        self.setupAltitudeGraphAndLine(picture)

    def fadeMoveInAltitudeEverything(self):
        self.altitudegraph.show()
        self.centerLabel.show()
        self.line.show()

        # Alt Line
        self.animMoveInLine = QPropertyAnimation(self.line, b"geometry")
        self.animMoveInLine.setDuration(3000)
        self.animMoveInLine.setStartValue(QRect(0, 360, 1280, 3))
        self.animMoveInLine.setEndValue(QRect(0, self.linePosY, 1280, 3))
        self.animMoveInLine.start()

        fadeEffect = QGraphicsOpacityEffect()
        self.line.setGraphicsEffect(fadeEffect)
        self.animFadeInLine = QPropertyAnimation(fadeEffect, b"opacity")
        # self.anim2 = QPropertyAnimation(self.label, b"windowOpacity")
        self.animFadeInLine.setStartValue(0)
        self.animFadeInLine.setEndValue(1)
        self.animFadeInLine.setDuration(1500)
        self.animFadeInLine.start()

        # Move in top label
        self.animMoveInAltitudeValue = QPropertyAnimation(self.centerLabel, b"geometry")
        self.animMoveInAltitudeValue.setDuration(2000)
        self.animMoveInAltitudeValue.setStartValue(QRect(0, 360, 1280, 110))
        self.animMoveInAltitudeValue.setEndValue(QRect(0, 15, 1280, 110))
        self.animMoveInAltitudeValue.start()

        # Fade in AltitudeGraphTransferQWidget
        fadeEffect2 = QGraphicsOpacityEffect()
        self.altitudegraph.setGraphicsEffect(fadeEffect2)
        self.animFadeInAltitudeGraph = QPropertyAnimation(fadeEffect2, b"opacity")
        self.animFadeInAltitudeGraph.setStartValue(0)
        self.animFadeInAltitudeGraph.setEndValue(1)
        self.animFadeInAltitudeGraph.setDuration(2000)
        self.animFadeInAltitudeGraph.start()

        self.update()

    def fadeMoveOutAltitudeEverything(self):
        # Label
        self.animMoveOutAltitudeValue = QPropertyAnimation(self.centerLabel, b"geometry")
        self.animMoveOutAltitudeValue.setDuration(2000)
        self.animMoveOutAltitudeValue.setStartValue(QRect(0, 30, 1280, 110))
        self.animMoveOutAltitudeValue.setEndValue(QRect(0, 360, 1280, 110))
        self.animMoveOutAltitudeValue.start()

        # Fade Out - Line
        fadeOutLine = QGraphicsOpacityEffect()
        self.line.setGraphicsEffect(fadeOutLine)
        self.animFadeOutLine = QPropertyAnimation(fadeOutLine, b"opacity")
        self.animFadeOutLine.setStartValue(1)
        self.animFadeOutLine.setEndValue(0)
        self.animFadeOutLine.setDuration(2000)
        self.animFadeOutLine.start()

        # Fade Out - Graph
        fadeOutGraph = QGraphicsOpacityEffect()
        self.altitudegraph.setGraphicsEffect(fadeOutGraph)
        self.animFadeOutGraph = QPropertyAnimation(fadeOutGraph, b"opacity")
        self.animFadeOutGraph.setStartValue(1)
        self.animFadeOutGraph.setEndValue(0)
        self.animFadeOutGraph.setDuration(2000)
        self.animFadeOutGraph.start()

        self.update()

    # Color Mode
    def setupColorWidgets(self, picture: Picture):
        self.colorpalette = ColorPaletteNew(self, True, picture.colors_rgb, picture.colors_conf)
        self.colorpalette.setGraphicsEffect(UIEffectDropShadow())

        archiveSize = self.sql_controller.get_archive_size()
        idxList = self.sql_controller.chooseIndexes(int(archiveSize), 1280.0)

        colorlist = self.sql_controller.ui_get_colors_for_archive_sortby('color', idxList)
        self.colorbar = ColorBarTransfer(self, True, colorlist)

        self.hideColorWidgets()

    def updateColorWidgets(self, picture: Picture):
        self.colorpalette.trigger_refresh(True, picture.colors_rgb, picture.colors_conf)

    def showColorWidgets(self):
        self.colorpalette.show()
        self.colorbar.show()

    def hideColorWidgets(self):
        self.colorpalette.hide()
        self.colorbar.hide()

    def fadeMoveInColorWidgets(self):
        self.colorpalette.show()
        self.colorbar.show()

        # Move in ColorPalette
        self.animMoveInColor = QPropertyAnimation(self.colorpalette, b"geometry")
        self.animMoveInColor.setDuration(2000)
        self.animMoveInColor.setStartValue(QRect(0, 360, 0, 0))
        self.animMoveInColor.setEndValue(QRect(0, 15, 0, 0))
        self.animMoveInColor.start()

        # Fade in ColorBar
        fadeEffect = QGraphicsOpacityEffect()
        self.colorbar.setGraphicsEffect(fadeEffect)
        self.animFadeInColor = QPropertyAnimation(fadeEffect, b"opacity")
        self.animFadeInColor.setStartValue(0)
        self.animFadeInColor.setEndValue(1)
        self.animFadeInColor.setDuration(2000)
        self.animFadeInColor.start()

        # This will overwrite the dropshadow effect
        # fadeEffect = QGraphicsOpacityEffect()
        # self.colorpalette.setGraphicsEffect(fadeEffect)
        # self.anim2 = QPropertyAnimation(fadeEffect, b"opacity")
        # self.anim2.setStartValue(0)
        # self.anim2.setEndValue(1)
        # self.anim2.setDuration(2000)
        # self.anim2.start()

        self.update()

    def fadeMoveOutColorWidgets(self):
        # Move out ColorPalette
        self.animMoveOutColor = QPropertyAnimation(self.colorpalette, b"geometry")
        self.animMoveOutColor.setDuration(2000)
        self.animMoveOutColor.setStartValue(QRect(0, 30, 0, 0))
        self.animMoveOutColor.setEndValue(QRect(0, 360, 0, 0))
        self.animMoveOutColor.start()

        # Fade out ColorBar
        fadeEffect = QGraphicsOpacityEffect()
        self.colorbar.setGraphicsEffect(fadeEffect)
        self.animFadeOutColor = QPropertyAnimation(fadeEffect, b"opacity")
        self.animFadeOutColor.setStartValue(1)
        self.animFadeOutColor.setEndValue(0)
        self.animFadeOutColor.setDuration(2000)
        self.animFadeOutColor.start()

        self.update()

    # Keyboard Input
    def keyPressEvent(self, event):
        # Closing App
        if event.key() == Qt.Key_Escape:
            self.close()
        elif event.key() == Qt.Key_1:
            print('1')
            # self.bgcolor.changeColor(self.picture.color_rgb)
        elif event.key() == Qt.Key_2:
            print('2')
            # self.fadeMoveInColorWidgets()
        elif event.key() == Qt.Key_3:
            print('3')
            # self.fadeMoveOutColorWidgets()
        elif event.key() == Qt.Key_4:
            print('4')
            # self.fadeMoveInAltitudeEverything()
        elif event.key() == Qt.Key_5:
            print('5')
            # self.fadeMoveOutAltitudeEverything()
        elif event.key() == Qt.Key_6:
            print('6')
            # self.fadeMoveInTime()
        elif event.key() == Qt.Key_7:
            print('7')
            # self.fadeMoveOutTime()
        elif event.key() == Qt.Key_8:
            print('8')
        elif event.key() == Qt.Key_9:
            print('9')
        elif event.key() == Qt.Key_0:
            print('0')

    def closeEvent(self, event):
        print('User has clicked the red X')
        self.garbageCollection()

    def garbageCollection(self):
        self.newPictureThread.signals.terminate = True


app = QApplication(sys.argv)
window = MainWindow()
window.show()
app.exec_()
