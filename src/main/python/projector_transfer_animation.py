#!/usr/bin/env python3

import platform, sys, math, time, os
from sqlite3.dbapi2 import connect
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *

from classes.capra_data_types import Picture, Hike
from classes.sql_controller import SQLController
from classes.ui_components import *


TIME_FOR_UI_MODE = 8000  # Miliseconds before next UI element moves onto screen
SECONDS_UNTIL_NEXT_PICTURE = 30  # Seconds before next picture is queried from database
                                 # current Picture will finish going through the 3 UI modes before changing
                                 # 8s is the time between each UI mode (new photo, color, altitude, time)
                                 # 8s x 4 = 32s
                                 # 30s is 2s before that

numPreviousHikes = 0


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

    def run(self):
        while True:
            if self.signals.terminate:
                break  # Garbage collection

            # Old way -- holding a global Picture
            # global globalPicture
            # globalPicture = self.sql_controller.get_random_picture()

            # New way -- using a signal to pass back the Picture
            # newPicture = self.sql_controller.get_random_picture()
            global numPreviousHikes
            print(f'In the thread numPreviousHikes = {numPreviousHikes}')
            newPicture = self.sql_controller.get_random_picture_from_previous_hikes(numPreviousHikes)
            print(f'Thread Picture Hike ID is: {newPicture.hike_id}')
            print(f'Thread Picture Picture ID is: {newPicture.picture_id}')
            self.signals.result.emit(newPicture)

            # Frequency that a new Picture will be selected from database
            # However, this Picture will be held by MainWindow in self.newPicture until the UI is ready for it
            # MainWindow will always go through the 3 UI modes (color, altitude, time) before showing the next Picture
            # All the presentation timing is controlled in animationHandler() and other animation methods further down
            time.sleep(SECONDS_UNTIL_NEXT_PICTURE)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Capra Transfer Animation")
        self.setGeometry(0, 0, 1280, 720)

        # Setups up database connection depending on the system
        self.setupSQLController()

        # Selects intial Picture from the database
        global numPreviousHikes
        self.picture = self.sql_controller.get_random_picture_from_previous_hikes(numPreviousHikes)
        print(f'Picture Hike: {self.picture.hike_id}')
        print(f'Picture ID: {self.picture.picture_id}\n')

        # Setup Bg Thread for continually getting new Pictures from database
        self.threadpool = QThreadPool()
        self.threadpool.setMaxThreadCount(1)
        self.newPictureThread = NewPictureThread(self.sql_controller)
        self.newPictureThread.signals.result.connect(self.updateNewPicture)
        self.threadpool.start(self.newPictureThread)

        # Setup UI
        self.bgcolor = BackgroundColor(self, QVBoxLayout(), Qt.AlignBottom, self.picture.color_rgb)
        # c1 = QColor(9, 24, 94, 255)

        self.setupColorWidgets(self.picture)
        self.setupAltitudeLabel(self.picture)
        self.setupTimeLabelAndBar(self.picture)

        self.superCenterImg = TransferCenterImage(self, self.picture)

        self.setupAltitudeGraphAndLine(self.picture)

        # Setup QTimer for checking for new Picture
        self.handlerCounter = 1
        self.timerAnimationHandler = QTimer()
        self.timerAnimationHandler.timeout.connect(self.animationHandler)
        self.timerAnimationHandler.start(TIME_FOR_UI_MODE)  # Miliseconds before next UI element moves onto screen

    def updateNewPicture(self, picture: Picture):
        '''Updates the newPicture from the Database / Transfer Script
        newPicture is a temporary holder for keeping the latest Picture until UI is ready'''
        self.newPicture = picture

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
            # Old
            # global globalPicture
            # self.picture = globalPicture

            # New
            self.picture = self.newPicture
            print(f'Picture Hike: {self.picture.hike_id}')
            print(f'Picture ID: {self.picture.picture_id}\n')

            # Update UI Elements
            self.updateColorWidgets(self.picture)
            self.updateTimeLabelAndBar(self.picture)
            self.updateAltitudeLabelAndGraph(self.picture)

            # Change Image and Background
            self.superCenterImg.fadeNewImage(self.picture)
            self.bgcolor.changeColor(self.picture.color_rgb)

        self.fadeOutTimer.start(int(TIME_FOR_UI_MODE / 2))  # Miliseconds til UI elements fade out; 1/2 animation time
        self.handlerCounter = (self.handlerCounter + 1) % 4

    # Database connection - previous db with UI data
    def setupSQLController(self):
        '''Initializes the database connection.\n
        If on Mac/Windows give dialog box to select database,
        otherwise it will use the global defined location for the database'''

        # Mac/Windows: select the location
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

        # How many previous hikes to select from
        totalHikes = self.sql_controller.get_hike_count()
        if platform.system() == 'Darwin' or platform.system() == 'Windows':
            # Dialog receiving input for how many previous hikes to select from
            i, okay = QInputDialog.getInt(self, "Select Previous Hikes",
            f"Total Hikes: {totalHikes}\n\nEnter how many previous hikes you want\nto use for the Transfer Animation",
            1, 0, totalHikes, 1)

            # Okay or Cancel
            global numPreviousHikes
            if okay:
                numPreviousHikes = i
                print(f"Inputted Previous Hikes: {numPreviousHikes}\n")
            else:  # Cancel was pressed
                self.close()

        else:  # Raspberry Pi:
            # TODO - this could change based in input from the transfer script
            numPreviousHikes = totalHikes

        # Preload the UI Data
        # (In corresponding methods, there's a commented out way of not preloading UI data)
        self.uiData = self.sql_controller.preload_ui_data()

    # Time Mode
    def setupTimeLabelAndBar(self, picture: Picture):
        self.timeLabel = TransferLabel(self, '', '')
        self.timeLabel.setPrimaryText(picture.uitime_hrmm)
        self.timeLabel.setSecondaryText(picture.uitime_ampm)

        # Hacky way to keep this hidden behind the center image
        self.animMoveInAltitudeValue = QPropertyAnimation(self.timeLabel, b"geometry")
        self.animMoveInAltitudeValue.setDuration(2000)
        self.animMoveInAltitudeValue.setStartValue(QRect(0, 360, 1280, 110))
        self.animMoveInAltitudeValue.setEndValue(QRect(0, 350, 1280, 110))
        self.animMoveInAltitudeValue.start()

        percent_rank = self.sql_controller.ui_get_percentage_in_archive_with_mode('time', self.picture)
        self.timebar = TimeBarTransfer(self, percent_rank)
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
        self.altitudeLabel = TransferLabel(self, '', 'M')
        self.altitudeLabel.setPrimaryText(picture.uialtitude)

        # Hacky way to keep this hidden behind the center image
        self.animMoveInAltitudeValue = QPropertyAnimation(self.altitudeLabel, b"geometry")
        self.animMoveInAltitudeValue.setDuration(2000)
        self.animMoveInAltitudeValue.setStartValue(QRect(0, 360, 1280, 110))
        self.animMoveInAltitudeValue.setEndValue(QRect(0, 350, 1280, 110))
        self.animMoveInAltitudeValue.start()

        # self.altitudeLabel.setGraphicsEffect(UIEffectDropShadow())

    def setupAltitudeGraphAndLine(self, picture: Picture):
        # Method for getting UI data without preloading
        # archiveSize = self.sql_controller.get_archive_size()
        # idxList = self.sql_controller.chooseIndexes(int(archiveSize), 1280.0)
        # altitudelist = self.sql_controller.ui_get_altitudes_for_archive_sortby('alt', idxList)

        altitudelist = self.uiData.altitudesSortByAltitudeForArchive
        currentAlt = picture.altitude
        altitudelist.insert(0, currentAlt)  # Append the new altitude at the start of the list
        altitudelist = sorted(altitudelist)  # Sorts so the altitude will fit within the correct spot on the graph

        self.altitudegraph = AltitudeGraphTransferWidget(self, altitudelist, currentAlt)
        self.altitudegraph.setGraphicsEffect(UIEffectDropShadow())

        minv = min(altitudelist)
        maxv = max(altitudelist)
        self.linePosY = self._calculateLinePosY(minv, maxv, currentAlt)

        self.line = QLabel("line", self)
        bottomImg = QPixmap("assets/line.png")
        self.line.setPixmap(bottomImg)
        self.line.setAlignment(Qt.AlignCenter)
        self.line.setGeometry(0, int(self.linePosY), 1280, 3)  # self.linePosY just calculated above

        self.altitudegraph.hide()
        self.line.hide()

    def _calculateLinePosY(self, minv: float, maxv: float, currentAlt: float):
        H = 500
        return 108 + H - ( ((currentAlt - minv)/(maxv-minv)) * (H-3) )

    def updateAltitudeLabelAndGraph(self, picture: Picture):
        self.altitudeLabel.setPrimaryText(picture.uialtitude)

        altitudelist = self.uiData.altitudesSortByAltitudeForArchive
        currentAlt = picture.altitude
        altitudelist.insert(0, currentAlt)  # Append the new altitude at the start of the list
        altitudelist = sorted(altitudelist)  # Sorts so the altitude will fit within the correct spot on the graph

        self.altitudegraph.trigger_refresh(altitudelist, currentAlt)  # Trigger refresh of the widget
        minv = min(altitudelist)
        maxv = max(altitudelist)
        self.linePosY = self._calculateLinePosY(minv, maxv, currentAlt)  # Trigger refresh of the Y line position

    def fadeMoveInAltitudeEverything(self):
        self.altitudegraph.show()
        self.altitudeLabel.show()
        self.line.show()

        # Alt Line
        self.animMoveInLine = QPropertyAnimation(self.line, b"geometry")
        self.animMoveInLine.setDuration(3000)
        self.animMoveInLine.setStartValue(QRect(0, 360, 1280, 3))
        # self.linePosY is calulated in updateAltitudeLabelAndGraph()
        self.animMoveInLine.setEndValue(QRect(0, int(self.linePosY), 1280, 3))
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
        self.animMoveInAltitudeValue = QPropertyAnimation(self.altitudeLabel, b"geometry")
        self.animMoveInAltitudeValue.setDuration(2000)
        self.animMoveInAltitudeValue.setStartValue(QRect(0, 360, 1280, 110))
        self.animMoveInAltitudeValue.setEndValue(QRect(0, 15, 1280, 110))
        self.animMoveInAltitudeValue.start()

        # Fade in AltitudeGraphTransferWidget
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
        self.animMoveOutAltitudeValue = QPropertyAnimation(self.altitudeLabel, b"geometry")
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

        # Method for getting UI data without preloading
        # archiveSize = self.sql_controller.get_archive_size()
        # idxList = self.sql_controller.chooseIndexes(int(archiveSize), 1280.0)
        # colorlist = self.sql_controller.ui_get_colors_for_archive_sortby('color', idxList)

        colorlist = self.uiData.colorSortByColorForArchive
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
        print('User has clicked the Red X or pressed Escape')
        self.garbageCollection()

    def garbageCollection(self):
        self.newPictureThread.signals.terminate = True


app = QApplication(sys.argv)
window = MainWindow()
window.show()
app.exec_()
