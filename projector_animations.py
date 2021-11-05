#!/usr/bin/env python3
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
import sys


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Animation")
        self.setGeometry(0, 0, 1280, 720)

        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # imgLabel = QLabel(self)
        # imgLabel.resize(1280, 720)
        # imgLabel.move(10, 10)
        # pixmap = QPixmap("person.jpg")
        # imgLabel.setPixmap(pixmap)

        img = Image(self, "assets/cam2f.jpg")
        # img.setGeometry(0, 720, 1280, 110)
        # layout.addWidget(img)

        self.lab = QLabel("HO HO HO")
        self.lab.setStyleSheet("border: 3px solid blue; background-color: rgba(0, 0, 0, 100);")

        self.InitWindow()

    def InitWindow(self):
        # self.setWindowIcon(QIcon("assets/icon.png"))

        self.button = QPushButton("Start", self)
        self.button.move(30, 30)
        self.button.clicked.connect(self.doAnimation)

        self.label = QLabel("HOWDY", self)
        bottomImg = QPixmap("assets/test-animation-bottom.png")
        self.label.setPixmap(bottomImg)
        self.label.setAlignment(Qt.AlignCenter)
        self.label.setGeometry(0, 610, 1280, 110)
        # self.label.setStyleSheet("border: 3px solid blue; background-color: rgba(0, 0, 0, 100);")

        # self.frame = QFrame(self)
        # self.frame.setFrameStyle(QFrame.Panel | QFrame.Raised)
        # self.frame.setGeometry(150, 30, 100, 100)

        self.showFullScreen()

    def paintRectangle(self, event):
        width = self.pos2[0]-self.pos1[0]
        height = self.pos2[1] - self.pos1[1]

        qp = QPainter()
        qp.begin(self)
        qp.drawRect(self.pos1[0], self.pos1[1], width, height)
        qp.drawRect(50, 50, 100, 50)
        qp.end()

    def doAnimation(self):
        self.anim = QPropertyAnimation(self.label, b"geometry")
        self.anim.setDuration(400)
        self.anim.setStartValue(QRect(0, 720, 1280, 110))
        self.anim.setEndValue(QRect(0, 610, 1280, 110))
        self.anim.start()

        fadeEffect = QGraphicsOpacityEffect()
        self.label.setGraphicsEffect(fadeEffect)
        self.anim2 = QPropertyAnimation(fadeEffect, b"opacity")
        # self.anim2 = QPropertyAnimation(self.label, b"windowOpacity")
        self.anim2.setStartValue(0)
        self.anim2.setEndValue(1)
        self.anim2.setDuration(400)
        self.anim2.start()

        self.update()

    def keyPressEvent(self, event):
        global rotaryCounter
        if event.key() == Qt.Key_Escape:
            self.close()


# Simple wrapper of QLabel, for easier image loading
class Image(QLabel):
    def __init__(self, mainWindow, path: str, *args, **kwargs):
        # super(QLabel, self).__init__(*args, **kwargs)
        super().__init__(mainWindow)

        # QLabel.__init__(self, mainWindow)
        self.resize(1280, 720)
        pixmap = QPixmap(path)
        self.setPixmap(pixmap)

app = QApplication(sys.argv)
window = MainWindow()
window.show()
app.exec_()