#!/usr/bin/env python3

# Various helper UI classes for easier development of PyQt5 applications

# Imports
# from projector_slideshow import *

from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PIL import Image, ImageQt  # Pillow image functions
# from PIL.ImageQt import ImageQt

import sys
import time


# Add a single color widget, great for testing purposes
class UIColor(QWidget):
    def __init__(self, color, *args, **kwargs):
        super(Color, self).__init__(*args, **kwargs)
        self.setAutoFillBackground(True)

        palette = self.palette()
        palette.setColor(QPalette.Window, QColor(color))
        self.setPalette(palette)


# Simple wrapper of QLabel, for easier image loading
class UIImage(QLabel):
    def __init__(self, path: str, *args, **kwargs):
        super(QLabel, self).__init__(*args, **kwargs)
        # QLabel.__init__(self)
        pixmap = QPixmap(path)
        self.setPixmap(pixmap)

    def update_image(self, path: str):
        self.pixmap = QPixmap(path)
        print('Is this a Pixmap?: {t}'.format(t=type(self.pixmap)))
        self.setPixmap(self.pixmap)

    def update_pixmap(self, im):
        im = im.convert("RGB")
        data = im.tobytes("raw", "RGB")
        # qim = QImage(data, im.size[0], im.size[1], QImage.Format_ARGB32)  # give weird color distortion
        qim = QImage(data, im.size[0], im.size[1], QImage.Format_RGB888)
        self.pixmap = QPixmap.fromImage(qim)
        self.setPixmap(self.pixmap)

        # Collection of things that didn't work but it is helpful to remember
        '''
        qim = ImageQt(im)
        pix = QPixmap.fromImage(qim)
        # pix = QPixmap.fromImage(qim, flags=Qt.AutoColor)
        self.setPixmap(pix)
        '''

        '''
        # fromImage() doesn't seem to be working; the other function just builds it from path
        qim = ImageQt(image)
        qim2 = QImage(qim)
        pix = QPixmap.fromImage(qim2)
        self.setPixmap(pix)
        '''

        '''
        # self.pixmap = QPixmap(ImageQt.ImageQt(image))
        print('update_pixmpa()')
        print('Parameter input is: {t}'.format(t=type(image)))

        qtimg = ImageQt.ImageQt(image)
        print('Is this a QT Image?: {t}'.format(t=type(qtimg)))

        self.pixmap = QPixmap.fromImage(qtimg)
        print('Is this a Pixmap?: {t}'.format(t=type(self.pixmap)))

        self.setPixmap(QPixmap(self.pixmap))
        '''


class UIImageOverlay(QLabel):
    def __init__(self, window, path: str, *args, **kwargs):
        super(QLabel, self).__init__(window, *args, **kwargs)
        # QLabel.__init__(self, window)
        self.resize(1280, 720)
        # self.move(0, 0)
        self.setAlignment(Qt.AlignCenter)
        pixmap = QPixmap(path)
        self.setPixmap(pixmap)


class UIModeOverlay(QLabel):
    def __init__(self, window, path: str, mode, *args, **kwargs):
        super(QLabel, self).__init__(window, *args, **kwargs)
        # QLabel.__init__(self, window)

        self.resize(1280, 720)
        # self.move(0, 0)
        self.setAlignment(Qt.AlignCenter)
        # self.setStyleSheet("border: 3px solid pink; background-color: rgba(0, 0, 0, 100);")
        self.setStyleSheet("background-color: rgba(0, 0, 0, 50);")

        # TODO - remove this because its so janky
        fadeEffect = QGraphicsOpacityEffect()
        self.setGraphicsEffect(fadeEffect)
        anim1 = QPropertyAnimation(fadeEffect, b"opacity")
        anim1.setEasingCurve(QEasingCurve.InCubic)
        anim1.setStartValue(0)
        anim1.setEndValue(0)
        anim1.setDuration(50)
        anim1.start()

        # pixmap = QPixmap('assets/Time@1x.png')
        # self.setPixmap(pixmap)

        # self.hide()

    def setTime(self):
        print('time')
        pixmap = QPixmap('assets/Time@1x.png')
        self.setPixmap(pixmap)
        self._doAnimation()

    def setAltitude(self):
        print('alt')
        pixmap = QPixmap('assets/Altitude@1x.png')
        self.setPixmap(pixmap)
        self._doAnimation()

    def setColor(self):
        print('color')
        pixmap = QPixmap('assets/Color@1x.png')
        self.setPixmap(pixmap)
        self._doAnimation()

    def _doAnimation(self):
        fadeEffect = QGraphicsOpacityEffect()
        self.setGraphicsEffect(fadeEffect)

        anim1 = QPropertyAnimation(fadeEffect, b"opacity")
        anim1.setEasingCurve(QEasingCurve.InCubic)
        anim1.setStartValue(0)
        anim1.setEndValue(1)
        anim1.setDuration(750)

        anim2 = QPropertyAnimation(fadeEffect, b"opacity")
        anim2.setEasingCurve(QEasingCurve.OutCubic)
        anim2.setStartValue(1)
        anim2.setEndValue(0)
        anim2.setDuration(750)

        group = QSequentialAnimationGroup(self)
        group.addAnimation(anim1)
        group.addPause(2000)
        group.addAnimation(anim2)
        # group.addAnimation(anim1)
        group.start()

        # self.anim = QPropertyAnimation(self.label, b"geometry")
        # self.anim.setDuration(400)
        # self.anim.setStartValue(QRect(0, 720, 1280, 110))
        # self.anim.setEndValue(QRect(0, 610, 1280, 110))
        # self.anim.start()
