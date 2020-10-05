#!/usr/bin/env python3

# Example of fading between 2 images in Python

from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

import sys
import time


class FaderWidget(QWidget):
    def __init__(self, old_widget, new_widget):
        QWidget.__init__(self, new_widget)

        self.old_pixmap = QPixmap(new_widget.size())
        old_widget.render(self.old_pixmap)
        self.pixmap_opacity = 1.0

        self.timeline = QTimeLine()
        self.timeline.valueChanged.connect(self.animate)
        self.timeline.finished.connect(self.close)
        self.timeline.setDuration(300)
        self.timeline.start()

        self.resize(new_widget.size())
        self.show()

    def paintEvent(self, event):
        painter = QPainter()
        painter.begin(self)
        painter.setOpacity(self.pixmap_opacity)
        painter.drawPixmap(0, 0, self.old_pixmap)
        painter.end()

    def animate(self, value):
        print('animate...')
        self.pixmap_opacity = 1.0 - value
        self.repaint()


class StackedWidget(QStackedWidget):
    def __init__(self, parent=None):
        QStackedWidget.__init__(self, parent)
        self.lastIndex = 0

    def setCurrentIndex(self, index):
        self.fader_widget = FaderWidget(self.currentWidget(), self.widget(index))
        QStackedWidget.setCurrentIndex(self, index)

    def flipPage(self):
        if self.lastIndex == 0:
            self.setCurrentIndex(1)
            self.lastIndex = 1
        else:
            self.setCurrentIndex(0)
            self.lastIndex = 0

        return self.lastIndex

    def setPage1(self):
        self.setCurrentIndex(0)

    def setPage2(self):
        self.setCurrentIndex(1)


class MainWindow(QMainWindow):
    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)

        # Images
        self.currentIndex = 1

        self.imgCurrent = QPixmap(self.buildFile(self.currentIndex))
        self.imgNext = QPixmap(self.buildFile(self.currentIndex + 1))

        self.labelCurrent = QLabel()
        self.labelCurrent.setPixmap(self.imgCurrent)
        self.labelNext = QLabel()
        self.labelNext.setPixmap(self.imgNext)

        # Stack - TODO testing it out
        self.stack = StackedWidget()
        self.stack.addWidget(self.labelCurrent)
        self.stack.addWidget(self.labelNext)

        # Grid
        self.grid = QGridLayout()
        self.grid.setSpacing(0)
        self.grid.setContentsMargins(0, 0, 0, 0)
        self.grid.addWidget(self.stack, 1, 1)

        # Widget
        w = QWidget()
        w.setLayout(self.grid)
        self.setCentralWidget(w)

        # Show the Qt app
        self.setWindowTitle("Capra Explorer")
        self.setStyleSheet("background-color: yellow;")
        self.setGeometry(350, 100, 1215, 720)  # posX, posY, w, h
        self.show()

    # Listens to key presses
    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape:
            self.close()
        elif event.key() == Qt.Key_Left:
            print('left')
            self.updatePrev()
        elif event.key() == Qt.Key_Right:
            print('right')
            self.updateNext()
        else:
            print('other key pressed')

    #TODO - think it might be one off
    def updateNext(self):
        val = self.stack.flipPage()
        print(val)

        self.currentIndex += 1

        if val == 0:
            self.imgCurrent = QPixmap(self.buildFile(self.currentIndex))
            self.labelCurrent.setPixmap(self.imgCurrent)
        else:
            self.imgNext = QPixmap(self.buildFile(self.currentIndex))
            self.labelNext.setPixmap(self.imgNext)

    def updatePrev(self):
        val = self.stack.flipPage()
        print(val)

        self.currentIndex -= 1

        if val == 0:
            self.imgCurrent = QPixmap(self.buildFile(self.currentIndex))
            self.labelCurrent.setPixmap(self.imgCurrent)
        else:
            self.imgNext = QPixmap(self.buildFile(self.currentIndex))
            self.labelNext.setPixmap(self.imgNext)


    def buildFile(self, num) -> str:
        # return '~/capra-storage/images/{n}_cam3.jpg'.format(n=num)
        return '/home/pi/capra-storage/images/{n}_cam3.jpg'.format(n=num)

# app manages the event loop
app = QApplication([])
window = MainWindow()
app.exec_()
