#!/usr/bin/env python3

# Various helper UI classes for easier development of PyQt5 applications

# Imports
# from projector_slideshow import *

from sqlite3.dbapi2 import Error
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PIL import Image, ImageQt  # Pillow image functions
# from PIL.ImageQt import ImageQt

import math
import sys
import time

# TODO - add rotatable widget container

# UI Super Classes
# -----------------------------------------------------------------------------


class UIWidget(QWidget):
    """Super class for universal animations of QWidgets"""
    def __init__(self) -> None:
        super().__init__()

        self.anim = QPropertyAnimation()
        self.fadeEffect = QGraphicsOpacityEffect()

    def fadeOut(self, duration: int):
        """Fades out the label over passed in duration (milliseconds)"""
        self.setGraphicsEffect(self.fadeEffect)
        self.anim = QPropertyAnimation(self.fadeEffect, b"opacity")
        self.anim.setStartValue(1)
        self.anim.setEndValue(0)
        self.anim.setDuration(duration)
        self.anim.start()
        self.update()

    def show(self):
        self.anim.stop()
        self.fadeEffect.setOpacity(1.0)

    def myHide(self):
        self.fadeEffect.setOpacity(0.0)


class UILabel(QLabel):
    """Super class for universal animations of
    QLabels that are placed directly onto the window"""
    def __init__(self, window):
        super().__init__(window)

        self.anim = QPropertyAnimation()
        self.fadeEffect = QGraphicsOpacityEffect()

    def fadeOut(self, duration: int):
        """Fades out the label over passed in duration (milliseconds)"""
        self.setGraphicsEffect(self.fadeEffect)
        self.anim = QPropertyAnimation(self.fadeEffect, b"opacity")
        self.anim.setStartValue(1)
        self.anim.setEndValue(0)
        self.anim.setDuration(duration)
        self.anim.start()
        self.update()

    def show(self):
        self.anim.stop()
        self.fadeEffect.setOpacity(1.0)


# UI Text & Image Components
# -----------------------------------------------------------------------------

# Labels for the information at the top of the screen
# Inherits from UILabel so it comes ready for animation
class UILabelTop(UILabel):
    def __init__(self, window, text: str, alignment):
        UILabel.__init__(self, window)  # works
        # super().__init__(window)  # works

        self._text = text
        self.setText(self._text)

        self.resize(1280, 200)
        # self.setAlignment(Qt.AlignLeft)
        self.setAlignment(alignment)
        self.setMargin(65)
        # self.setIndent(100)

        self.setFont(QFont('Atlas Grotesk', 24, 400))
        self.setStyleSheet("color: rgba(255,255,255,255)")
        self.setGraphicsEffect(UIEffectTextDropShadow())

    def setPrimaryText(self, text):
        self.setText(str(text))


# Compound QWidget that holds two QLabels for the middle UI
class UILabelTopCenter(QWidget):
    def __init__(self, window, primaryText: str, secondaryText: str, *args, **kwargs):
        # super(QWidget, self).__init__(window, *args, **kwargs)
        super().__init__(window, *args, **kwargs)

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
        self._label1_opacity = QGraphicsOpacityEffect()
        self._label1_opacity.setOpacity(1.0)
        self.label1.setGraphicsEffect(self._label1_opacity)

        self.label2 = QLabel(secondaryText)
        self.label2.setFont(QFont('Atlas Grotesk', 30, 400))
        self.label2.setStyleSheet("color: rgba(255,255,255,225)")
        self.label2.setGraphicsEffect(UIEffectTextDropShadow())
        self._label2_opacity = QGraphicsOpacityEffect()
        self._label2_opacity.setOpacity(1.0)
        self.label2.setGraphicsEffect(self._label2_opacity)

        self.animGroupFadeOut = QParallelAnimationGroup(self)
        self._setupHideAnimation()

        # TESTING - uncomment to see clear background on the components
        # palette = self.palette()
        # palette.setColor(QPalette.Window, QColor('pink'))
        # self.label1.setAutoFillBackground(True)
        # self.label1.setPalette(palette)
        # self.label2.setAutoFillBackground(True)
        # self.label2.setPalette(palette)

        layout.addWidget(self.label1)
        layout.addWidget(self.label2)
        self.setLayout(layout)

    def setPrimaryText(self, text):
        self.label1.setText(str(text))

    def setSecondaryText(self, text):
        self.label2.setText(text)

    def show(self):
        self.animGroupFadeOut.stop()
        self._label1_opacity.setOpacity(1.0)
        self._label2_opacity.setOpacity(1.0)

    def fadeIn(self):
        print('UILabelTopCenter.fadeIn() -- NO YET IMPLEMENTED')

    def fadeOut(self):
        self.animGroupFadeOut.start()

    def _setupHideAnimation(self):
        anim1 = QPropertyAnimation(self._label1_opacity, b"opacity")
        anim1.setStartValue(1)  # opaque
        anim1.setEndValue(0)  # transparent
        anim1.setDuration(1000)

        anim2 = QPropertyAnimation(self._label2_opacity, b"opacity")
        anim2.setStartValue(1)
        anim2.setEndValue(0)
        anim2.setDuration(1000)

        self.animGroupFadeOut.addAnimation(anim1)
        self.animGroupFadeOut.addAnimation(anim2)


# Simple wrapper of QLabel, for easier image loading
class UIImage(QLabel):
    def __init__(self, path: str, *args, **kwargs):
        super(QLabel, self).__init__(*args, **kwargs)
        # QLabel.__init__(self)
        pixmap = QPixmap(path)
        self.setPixmap(pixmap)

    def update_image(self, path: str):
        """Loads new image from local storage path"""
        self.pixmap = QPixmap(path)
        # print('Is this a Pixmap?: {t}'.format(t=type(self.pixmap)))
        self.setPixmap(self.pixmap)

    # TODO - see how processing consumption for this, compares to saving locally
    def update_pixmap(self, im):
        """Accepts a raw image and utilizes image conversion to load it"""
        im = im.convert("RGB")
        data = im.tobytes("raw", "RGB")
        # qim = QImage(data, im.size[0], im.size[1], QImage.Format_ARGB32)  # give weird color distortion
        qim = QImage(data, im.size[0], im.size[1], QImage.Format_RGB888)
        self.pixmap = QPixmap.fromImage(qim)
        self.setPixmap(self.pixmap)


# Semi-transparent underlay that inherits from UILabel
class UIUnderlay(UILabel):
    def __init__(self, window):
        # UILabel.__init__(self, window)  # works
        super().__init__(window)  # works
        # super(UILabel, self).__init__(window) # doesn't work

        # self.resize(1280, 720)
        # self.move(0, 0)
        self.setAlignment(Qt.AlignCenter)
        self.setGeometry(0, 0, 1280, 187)
        pixmap = QPixmap('assets/Underlay@1x.png')
        self.setPixmap(pixmap)


class UIModeOverlay(QLabel):
    def __init__(self, window, path: str, mode, *args, **kwargs):
        super(QLabel, self).__init__(window, *args, **kwargs)
        # QLabel.__init__(self, window)

        self.resize(1280, 720)
        # self.move(0, 0)
        self.setAlignment(Qt.AlignCenter)
        # self.setStyleSheet("border: 3px solid pink; background-color: rgba(0, 0, 0, 100);")
        self.setStyleSheet("background-color: rgba(0, 0, 0, 25);")

        # TODO - remove this because its so janky
        fadeEffect = QGraphicsOpacityEffect()
        self.setGraphicsEffect(fadeEffect)
        anim1 = QPropertyAnimation(fadeEffect, b"opacity")
        anim1.setEasingCurve(QEasingCurve.InCubic)
        anim1.setStartValue(0)
        anim1.setEndValue(0)
        anim1.setDuration(50)
        anim1.start()

    def setTime(self):
        # print('UIModeOverlay.setTime()')
        pixmap = QPixmap('assets/Time@1x.png')
        self.setPixmap(pixmap)
        self._doAnimation()

    def setAltitude(self):
        # print('UIModeOverlay.setAltitude()')
        pixmap = QPixmap('assets/Altitude@1x.png')
        self.setPixmap(pixmap)
        self._doAnimation()

    def setColor(self):
        # print('UIModeOverlay.setColor()')
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


# UI Time, Color, Altitude Components
# -----------------------------------------------------------------------------
class UIContainer(QWidget):
    def __init__(self, window, layout, alignment, *args, **kwargs):
        super().__init__(window, *args, **kwargs)

        self.resize(window.width(), window.height())
        self.layout = layout
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setAlignment(alignment)

        # layout.setSpacing(5)
        # self.timebar = TimeBar(QColor(62, 71, 47), 75, True)
        # self.timebar.setGraphicsEffect(UIEffectDropShadow())
        # self.layout.addWidget(self.timebar)

        self.setLayout(self.layout)

    def paintEvent(self, e):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.HighQualityAntialiasing)
        brush = QBrush()
        brush.setStyle(Qt.SolidPattern)

        # grab width & height of the whole painter
        w = painter.device().width()
        h = painter.device().height()

        # bg - for testing
        # brush.setColor(QColor(9, 24, 94, 150))
        # rect = QRect(0, 0, w, h)
        # painter.fillRect(rect, brush)


class PortraitTopLabel(UIWidget):
    def __init__(self, text: str) -> None:
        super().__init__()
        self.text = text
        self.setFixedHeight(720)
        self.setFixedWidth(250)

    def setText(self, str):
        self.text = str
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.HighQualityAntialiasing)

        # bg
        brush = QBrush()
        brush.setStyle(Qt.SolidPattern)

        painter.translate(painter.device().width(), 0)
        painter.rotate(90)

        # text
        pen = QPen()
        pen.setColor(QColor('white'))
        painter.setPen(pen)
        font = QFont()
        font.setFamily('Atlas Grotesk')
        font.setBold(True)
        font.setPointSize(24)
        painter.setFont(font)

        rec = QRect(QPoint(300, 50), QSize(100, 25))
        painter.drawText(rec, 0, self.text)
        # painter.drawText(pt, "Starting")
        # painter.drawText(200, 20, 0, "Starting")

        painter.end()


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


# Drop shadow for bottom UI elements
class UIEffectDropShadow(QGraphicsDropShadowEffect):
    def __init__(self):
        super(QGraphicsDropShadowEffect, self).__init__()
        self.setBlurRadius(20)
        color = QColor(0, 0, 0, 150)  # r,g,b,a | opaque = 255
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
