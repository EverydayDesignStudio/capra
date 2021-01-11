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


# UI Components
# -----------------------------------------------------------------------------

class UILabelTop(QLabel):
    def __init__(self, window, text: str, alignment, *args, **kwargs):
        super(QLabel, self).__init__(window, *args, **kwargs)

        self.setText(text)

        self.resize(1280, 200)
        # self.setAlignment(Qt.AlignLeft)
        self.setAlignment(alignment)
        self.setMargin(65)
        # self.setIndent(100)

        self.setFont(QFont('Atlas Grotesk', 28, 400))
        self.setStyleSheet("color: rgba(255,255,255,255)")
        self.setGraphicsEffect(UIEffectTextDropShadow())

    def setPrimaryText(self, text):
        self.setText(str(text))


class UILabelTopCenter(QWidget):
    def __init__(self, window, primaryText: str, secondaryText: str, *args, **kwargs):
        super(QWidget, self).__init__(window, *args, **kwargs)

        self.resize(1280, 150)
        layout = QHBoxLayout()
        layout.setAlignment(Qt.AlignHCenter)
        # layout.setAlignment(Qt.AlignTop)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(5)

        self.label1 = QLabel(primaryText)
        self.label1.setFont(QFont('Atlas Grotesk', 48, 500))
        self.label1.setStyleSheet("color: rgba(255,255,255,255)")
        self.label1.setGraphicsEffect(UIEffectTextDropShadow())

        self.label2 = QLabel(secondaryText)
        self.label2.setFont(QFont('Atlas Grotesk', 30, 400))
        self.label2.setStyleSheet("color: rgba(255,255,255,225)")
        self.label2.setGraphicsEffect(UIEffectTextDropShadow())

        # TESTING
        # palette = self.palette()
        # palette.setColor(QPalette.Window, QColor('gray'))
        # label1.setAutoFillBackground(True)
        # label1.setPalette(palette)
        # label2.setAutoFillBackground(True)
        # label2.setPalette(palette)

        layout.addWidget(self.label1)
        layout.addWidget(self.label2)
        self.setLayout(layout)

    def setPrimaryText(self, text):
        self.label1.setText(str(text))

    def setSecondaryText(self, text):
        self.label2.setText(text)


# Simple wrapper of QLabel, for easier image loading
class UIImage(QLabel):
    def __init__(self, path: str, *args, **kwargs):
        super(QLabel, self).__init__(*args, **kwargs)
        # QLabel.__init__(self)
        pixmap = QPixmap(path)
        self.setPixmap(pixmap)

    # Utilizes local storage
    def update_image(self, path: str):
        self.pixmap = QPixmap(path)
        print('Is this a Pixmap?: {t}'.format(t=type(self.pixmap)))
        self.setPixmap(self.pixmap)

    # Utilizes image conversion
    # TODO - see how this compares to saving locally
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


# UI Effects
# -----------------------------------------------------------------------------

# Text effect used for the text at the top of the interface
class UIEffectTextDropShadow(QGraphicsDropShadowEffect):
    def __init__(self):
        super(QGraphicsDropShadowEffect, self).__init__()
        self.setBlurRadius(20)
        color = QColor(0, 0, 0, 50)  # r,g,b,a | opaque = 255
        self.setColor(color)
        self.setOffset(0, 2)


# UI Testing
# -----------------------------------------------------------------------------

# Add a single color widget, great for testing purposes
class UIColor(QWidget):
    def __init__(self, color, *args, **kwargs):
        super(Color, self).__init__(*args, **kwargs)

        self.setAutoFillBackground(True)
        palette = self.palette()
        palette.setColor(QPalette.Window, QColor(color))
        self.setPalette(palette)
