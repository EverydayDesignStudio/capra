#!/usr/bin/env python3

import platform, sys, math, time
from sqlite3.dbapi2 import connect
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PIL import Image

from classes.capra_data_types import Picture, Hike
from classes.sql_controller import SQLController
from classes.ui_components import *

import globals as g
g.init()


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Capra Transfer Animation")
        self.setGeometry(0, 0, 1280, 720)

        # Selects 4 pictures: self.picture, self.picture2, self.picture3, self.picture4
        self.setupDBGetPictures()

        # Setup BG color
        c1 = QColor(9, 24, 94, 255)
        # self.bgcolor = BackgroundColor(self, QVBoxLayout(), Qt.AlignBottom, c1)
        self.bgcolor = BackgroundColor(self, QVBoxLayout(), Qt.AlignBottom, self.picture.color_rgb)

        self.setupColorWidgets(self.picture)
        self.setupAltitudeLabel(self.picture)
        self.setupTimeLabelAndBar(self.picture)

        self.setupCenterImage(self.picture)
        # self.fadeMoveInColorWidgets()
        # self.fadeMoveOutColorWidgets()

        self.setupAltitudeGraphAndLine(self.picture, 500)
        self.altitudegraph.hide()
        self.centerLabel.opacityHide()
        self.line.hide()

    # Database connection - previous db with UI data
    def setupDBGetPictures(self):
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
        self.picture = self.sql_controller.get_picture_with_id(28300)
        self.picture2 = self.sql_controller.get_picture_with_id(27500)
        self.picture3 = self.sql_controller.get_picture_with_id(12000)
        self.picture4 = self.sql_controller.get_picture_with_id(10700)
        # 10700, 11990, 12000, 15000, 20000, 27100, 27200, 27300, 27500, 28300

        # TESTING - comment out to speed up program load time
        # self.uiData = self.sql_controller.preload_ui_data()
        # self.preload = True

    # Center Image
    def setupCenterImage(self, picture: Picture):
        '''Setup the window size, title, and container layout'''
        pagelayout = QVBoxLayout()
        pagelayout.setAlignment(Qt.AlignCenter)
        # pagelayout.setContentsMargins(0, 0, 0, 0)

        # old bg Color
        # self.setStyleSheet("background-color: #440100;")
        # self.setStyleSheet("background-color:rgb(255, 100, 75, 0);")
        # rgb = self.picture.color_rgb.getRgb()
        # style = "background-color:rgb{val};".format(val=rgb)
        # self.setStyleSheet(style)

        self.centerImg = CenterImage(self, picture.cameraf)
        pagelayout.addWidget(self.centerImg)

        # Add central widget
        centralWidget = QWidget()
        centralWidget.setLayout(pagelayout)
        self.setCentralWidget(centralWidget)

    def updateCenterImage(self, picture: Picture):
        # self.centerImg = CenterImage(self, picture.cameraf)
        self.centerImg.updateImage(picture.cameraf)

    def fadeInCenterImage(self):
        # CenterImg
        fadeEffect2 = QGraphicsOpacityEffect()
        self.centerImg.setGraphicsEffect(fadeEffect2)
        self.anim3 = QPropertyAnimation(fadeEffect2, b"opacity")
        self.anim3.setStartValue(0)
        self.anim3.setEndValue(1)
        self.anim3.setDuration(2000)
        self.anim3.start()

    # Time Mode
    def setupTimeLabelAndBar(self, picture: Picture):
        self.timeLabel = UILabelTopCenter(self, '', '')
        self.timeLabel.setPrimaryText(picture.uitime_hrmm)
        self.timeLabel.setSecondaryText(picture.uitime_sec)

        percent_rank = self.sql_controller.ui_get_percentage_in_hike_with_mode('time', self.picture)
        self.timebar = TimeBarTransfer(self, percent_rank)

        self.timeLabel.opacityHide()
        self.timebar.hide()

    def fadeInTime(self):
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

    def fadeOutTime(self):
        # Move in top label
        self.animMoveOutTimeLabel = QPropertyAnimation(self.timeLabel, b"geometry")
        self.animMoveOutTimeLabel.setDuration(2000)
        self.animMoveOutTimeLabel.setStartValue(QRect(0, 15, 1280, 110))
        self.animMoveOutTimeLabel.setEndValue(QRect(0, 360, 1280, 110))
        self.animMoveOutTimeLabel.start()

        # Fade in the timebar
        fadeTimebar = QGraphicsOpacityEffect()
        self.timebar.setGraphicsEffect(fadeTimebar)
        self.animFadeOutAltitudeGraph = QPropertyAnimation(fadeTimebar, b"opacity")
        self.animFadeOutAltitudeGraph.setStartValue(1)
        self.animFadeOutAltitudeGraph.setEndValue(0)
        self.animFadeOutAltitudeGraph.setDuration(2000)
        self.animFadeOutAltitudeGraph.start()

    # Altitude Mode
    def setupAltitudeLabel(self, picture: Picture):
        self.centerLabel = UILabelTopCenter(self, '', 'M')
        self.centerLabel.setPrimaryText(picture.uialtitude)

        colorlist = self.sql_controller.ui_get_colors_for_archive_sortby('color')
        self.colorbar = ColorBarTransfer(self, True, colorlist)

        self.hideColorWidgets()

    def setupAltitudeGraphAndLine(self, picture: Picture, currentAlt):
        altitudelist = self.sql_controller.ui_get_altitudes_for_archive_sortby('alt')

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

    def fadeInAltitudeEverything(self):
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

    def fadeOutAltitudeEverything(self):
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

        colorlist = self.sql_controller.ui_get_colors_for_archive_sortby('color')
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
            self.bgcolor.changeColor(self.picture.color_rgb)
            self.bgcolor = BackgroundColor(self, QVBoxLayout(), Qt.AlignBottom, self.picture.color_rgb)
        elif event.key() == Qt.Key_2:
            print('2')
            self.fadeMoveInColorWidgets()
        elif event.key() == Qt.Key_3:
            print('3')
            self.fadeMoveOutColorWidgets()
        elif event.key() == Qt.Key_4:
            print('4')
            self.fadeInAltitudeEverything()
        elif event.key() == Qt.Key_5:
            print('5')
            self.fadeOutAltitudeEverything()
        elif event.key() == Qt.Key_6:
            print('6')
            self.fadeInTime()
        elif event.key() == Qt.Key_7:
            print('7')
            self.fadeOutTime()
        elif event.key() == Qt.Key_8:
            print('8')
            self.updateColorWidgets(self.picture3)
            self.updateCenterImage(self.picture3)
            self.bgcolor.changeColor(self.picture.color_rgb)
            # self.showColorWidgets(self.picture3)
            # self.showCenterImage(self.picture3)
        elif event.key() == Qt.Key_9:
            print('9')
            self.fadeInCenterImage()
            # self.showColorWidgets(self.picture4)
            # self.updateColorWidgets(self.picture4)
        elif event.key() == Qt.Key_0:
            print('0')
            self.colorpalette.hide()

        elif event.key() == Qt.Key_A:
            print('A')

        elif event.key() == Qt.Key_T:
            print('T')

    def closeEvent(self, event):
        print('User has clicked the red X')


app = QApplication(sys.argv)
window = MainWindow()
window.show()
app.exec_()
