#!/usr/bin/env python3

# Slideshow application for the Explorer. 
# Allows passing through photos with a smooth fading animation.

from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from RPi import GPIO

import sys
import time
import traceback

fileWideCounter = 0

class WorkerSignals(QObject):
    '''
    Defines the signals available from a running worker thread.
    Supported signals are:

    finished
        No data
    error
        `tuple` (exctype, value, traceback.format_exc() )
    result
        `object` data returned from processing, anything
    progress
        `int` indicating % progress
    '''
    finished = pyqtSignal()
    error = pyqtSignal(tuple)
    result = pyqtSignal(object)
    progress = pyqtSignal(int)


class Worker(QRunnable):
    def __init__(self, *args, **kwargs):
        super(Worker, self).__init__()

        self.clk = 23
        self.cnt = 24

        GPIO.setup(self.clk, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
        GPIO.setup(self.cnt, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

        self.clkLastState = GPIO.input(self.clk)

        self.count = 0
        self.signals = WorkerSignals()

    def run(self):
        while True:
            self.clkState = GPIO.input(self.clk)
            self.cntState = GPIO.input(self.cnt)
            if self.clkState != self.clkLastState:
                if self.cntState != self.clkState:
                    self.count += 1
                    # self.signals.result.emit(self.count)
                else:
                    self.count -= 1
                    # self.signals.result.emit(self.count)
            self.clkLastState = self.clkState
            # print(self.count)


# https://www.sunfounder.com/learn/Super_Kit_V2_for_RaspberryPi/lesson-8-rotary-encoder-super-kit-for-raspberrypi.html
class RotaryEncoder(QRunnable):
    def __init__(self, PIN_A: int, PIN_B: int, *args, **kwargs):
        super(RotaryEncoder, self).__init__()

        self.RoAPin = PIN_A
        self.RoBPin = PIN_B

        self.globalCounter = 0
        self.flag = 0
        self.Last_RoB_Status = 0
        self.Current_RoB_Status = 0

        GPIO.setup(self.RoAPin, GPIO.IN)    # input mode
        GPIO.setup(self.RoBPin, GPIO.IN)

    def rotaryTurn(self):
        global fileWideCounter
        Last_RoB_Status = GPIO.input(self.RoBPin)

        while(not GPIO.input(self.RoAPin)):
            self.Current_RoB_Status = GPIO.input(self.RoBPin)
            self.flag = 1
        if self.flag == 1:
            self.flag = 0
            if (Last_RoB_Status == 0) and (self.Current_RoB_Status == 1):
                self.globalCounter = self.globalCounter + 1
                fileWideCounter = self.globalCounter
                # print('globalCounter = {g}'.format(g=self.globalCounter))
            if (Last_RoB_Status == 1) and (self.Current_RoB_Status == 0):
                self.globalCounter = self.globalCounter - 1
                fileWideCounter = self.globalCounter
                # print('globalCounter = {g}'.format(g=self.globalCounter))

    def run(self):
        while True:
            self.rotaryTurn()


class MainWindow(QMainWindow):
    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)

        '''
        app = QtWidgets.QApplication(sys.argv)
        screen = app.primaryScreen()
        print('Screen: %s' % screen.name())
        size = screen.size()
        print('Size: %d x %d' % (size.width(), size.height()))
        rect = screen.availableGeometry()
        print('Available: %d x %d' % (rect.width(), rect.height()))
        '''
        
        self.index = 1
        self.seconds = 0

        self.setupGPIO()
        self.setupUI()
        self.setupThreads()

    def setupGPIO(self):
        # set the mode, alternative is GPIO.BOARD
        GPIO.setmode(GPIO.BCM)

        # define all of the hardware pins
        self.PIN_ROTARY_A = 23
        self.PIN_ROTARY_B = 24
        self.PIN_ROTARY_BUTT = 25

        self.PIN_MODE = 0
        self.PIN_PREV = 0
        self.PIN_PLAY_PAUSE = 0
        self.PIN_NEXT = 0

        # Accelerometer

        # NeoPixels

        # LED indicators
        
    def setupUI(self):
        # Layout
        layout = QVBoxLayout()

        # self.indexLabel = QLabel("Count: 0")
        # self.timerLabel = QLabel("Timer: 0")
        # self.workerThreadLabel = QLabel("Worker: 0")

        # self.button = QPushButton("Increment Count")
        # self.button.pressed.connect(self.increment_label)

        self.img = QPixmap(self.buildFile(self.index))
        # self.img = self.img.scaled(640, 300)
        self.imgView = QLabel()
        self.imgView.setPixmap(self.img)

        # Grid - layout
        self.grid = QGridLayout()
        self.grid.setSpacing(0)
        self.grid.setContentsMargins(0, 0, 0, 0)
        self.grid.addWidget(self.imgView)
        # self.grid.addWidget(self.indexLabel, 3, 1)
        # self.grid.addWidget(self.button, 4, 1)
        # self.grid.addWidget(self.timerLabel, 2, 1)
        # self.grid.addWidget(self.workerThreadLabel, 5, 1)

        # Widget
        w = QWidget()
        w.setLayout(self.grid)
        self.setCentralWidget(w)

        # Show the Qt app
        self.setWindowTitle("Capra Slideshow")
        self.setStyleSheet("background-color: yellow;")
        # self.setGeometry(350, 100, 1215, 720)  # posX, posY, w, h
        # self.showFullScreen()
        self.show()

        # Timer
        # self.timer = QTimer()
        # self.timer.setInterval(1000)
        # self.timer.timeout.connect(self.recurring_timer)
        # self.timer.start()

    def setupThreads(self):
        self.threadpool = QThreadPool()

        # self.worker = Worker()
        # self.worker.signals.result.connect(self.thread_result)
        # self.threadpool.start(self.worker)

        self.rotaryEncoder = RotaryEncoder(self.PIN_ROTARY_A, self.PIN_ROTARY_B)
        self.threadpool.start(self.rotaryEncoder)

    def keyPressEvent(self, event):
        global fileWideCounter
        if event.key() == Qt.Key_Escape:
            self.close()
        elif event.key() == Qt.Key_Left:
            print('left')
            # self.updatePrev()
        elif event.key() == Qt.Key_Right:
            print('right')
            print(fileWideCounter)
            # self.updateNext()
        else:
            print('other key pressed')

    def increment_label(self):
        self.index += 1
        self.indexLabel.setText('Count: %d' % self.index)

    def recurring_timer(self):
        self.seconds += 1
        self.timerLabel.setText('Timer: %d' % self.seconds)

    def thread_result(self, result):
        print('From MainLoop: %d' % result)
        # self.workerThreadLabel.setText('Worker: %d' % result)

        self.img = QPixmap(self.buildFile(result))
        self.imgView.setPixmap(self.img)

    def buildFile(self, num) -> str:
        # return '~/capra-storage/images/{n}_cam3.jpg'.format(n=num)
        return '/home/pi/capra-storage/images/{n}_cam3.jpg'.format(n=num)

    # def oh_no(self):
    #     # Pass in the function
    #     worker = Worker(self.execute_this_fn)  # Any other args, kwargs are passed to the run function
    #     worker.signals.result.connect(self.print_output)
    #     worker.signals.finished.connect(self.thread_complete)
    #     worker.signals.progress.connect(self.progress_fn)

    #     # Execute
    #     self.threadpool.start(worker)

    #     # Thread count
    #     print('Active threads: {ct}/{mx}'.format(mx=self.threadpool.maxThreadCount(), ct=self.threadpool.activeThreadCount()))

    # def progress_fn(self, n):
    #     print('%d%% done' % n)

    # def execute_this_fn(self, progress_callback):
    #     for n in range(0, 5):
    #         time.sleep(1)
    #         progress_callback.emit(n*100/4)
    #     return "Done"

    # def print_output(self, s):
    #     print(s)

    # def thread_complete(self):
    #    print("THREAD COMPLETE!")


app = QApplication([])
window = MainWindow()
app.exec_()
