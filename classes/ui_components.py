#!/usr/bin/env python3

# Various helper UI classes for easier development of PyQt5 applications

from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *

import sys


# Add a single color widget, great for testing purposes
class Color(QWidget):
    def __init__(self, color, *args, **kwargs):
        super(Color, self).__init__(*args, **kwargs)
        self.setAutoFillBackground(True)

        palette = self.palette()
        palette.setColor(QPalette.Window, QColor(color))
        self.setPalette(palette)


# Simple wrapper of QLabel, for easier image loading
class Image(QLabel):
    def __init__(self, path: str, *args, **kwargs):
        super(QLabel, self).__init__(*args, **kwargs)
        # QLabel.__init__(self)
        pixmap = QPixmap(path)
        self.setPixmap(pixmap)


class ImageOverlay(QLabel):
    def __init__(self, window, path: str, *args, **kwargs):
        super(QLabel, self).__init__(window, *args, **kwargs)
        # QLabel.__init__(self, window)
        self.resize(1280, 720)
        # self.move(0, 0)
        self.setAlignment(Qt.AlignCenter)
        pixmap = QPixmap(path)
        self.setPixmap(pixmap)
