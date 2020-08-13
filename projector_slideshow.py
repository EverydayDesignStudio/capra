#!/usr/bin/env python3

# Slideshow application for the Capra Explorer
# Allows passing through photos with a smooth fading animation

from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from RPi import GPIO
from datetime import datetime

import sys
import time
import traceback

# Filewide Hardware Status
rotaryCounter = 0


# Threading Infrastructure
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


'''
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
'''


# Custom Hardware Controls
class RotaryEncoder(QRunnable):
    def __init__(self, PIN_A: int, PIN_B: int, *args, **kwargs):
        super(RotaryEncoder, self).__init__()

        self.RoAPin = PIN_A
        self.RoBPin = PIN_B

        GPIO.setup(self.RoAPin, GPIO.IN)
        GPIO.setup(self.RoBPin, GPIO.IN)

        self.flag = 0
        self.Last_RoB_Status = 0
        self.Current_RoB_Status = 0
        self.Last_Direction = 0         # 0 for backward, 1 for forward
        self.Current_Direction = 0      # 0 for backward, 1 for forward

        self.PERIOD = 500
        self.MAXQUEUE = 5
        self.lst = list()
        self.last_time = datetime.now().timestamp()
        self.speedText = ""
        self.average = 0
        self.dt = 0
        self.multFactor = 1

    def calculate_speed(self):
        self.dt = round(datetime.now().timestamp() - self.last_time, 5)
        # data sanitation: clean up random stray values that are extremely low
        if self.dt < .001:
            self.dt = .1

        if len(self.lst) > self.MAXQUEUE:
            self.lst.pop()
        self.lst.insert(0, self.dt)
        self.average = sum(self.lst) / len(self.lst)

        self.last_time = datetime.now().timestamp()

        #   .3   .07   .02
        if self.average >= .3:
            self.speedText = "slow"
        elif self.average >= .07 and self.average < .3:
            self.speedText = "medium"
        elif self.average >= .02 and self.average < .07:
            self.speedText = "fast"
        else:
            self.speedText = "super-duper fast"

        return self.average, self.speedText, self.dt

    # Starting logic comes from the following project:
    # https://www.sunfounder.com/learn/Super_Kit_V2_for_RaspberryPi/lesson-8-rotary-encoder-super-kit-for-raspberrypi.html
    def rotaryTurn(self):
        global rotaryCounter

        self.Last_RoB_Status = GPIO.input(self.RoBPin)

        while(not GPIO.input(self.RoAPin)):
            self.Current_RoB_Status = GPIO.input(self.RoBPin)
            self.flag = 1
        if self.flag == 1:
            self.flag = 0

            if (self.Last_RoB_Status == 0) and (self.Current_RoB_Status == 1):
                self.Current_Direction = 1
            if (self.Last_RoB_Status == 1) and (self.Current_RoB_Status == 0):
                self.Current_Direction = 0

            if (self.Current_Direction != self.Last_Direction):
                self.lst.clear()

            self.average, self.speedText, self.dt = self.calculate_speed()

            speed = 1 / self.dt
            self.multFactor = int(1 / self.average)
            if (self.multFactor < 1 or self.Current_Direction != self.Last_Direction):
                self.multFactor = 1
            # elif (multFactor):

            if (self.Current_Direction == 1):
                rotaryCounter = rotaryCounter + 1 * self.multFactor
            else:
                rotaryCounter = rotaryCounter - 1 * self.multFactor

            self.Last_Direction = self.Current_Direction
            print('rotaryCounter: {g}, diff_time: {d:.4f}, speed: {s:.2f}, MultFactor: {a:.2f} ({st})'.format(g=rotaryCounter, d=self.dt, s=speed, a=self.multFactor, st=self.speedText))

    def clear(self, ev=None):
        global rotaryCounter
        rotaryCounter = 0
        print('rotaryCounter = {g}'.format(g=rotaryCounter))
        time.sleep(1)

    def run(self):
        while True:
            self.rotaryTurn()


# Uses global status variable to ensure there are no double presses for hardware buttons
class HardwareButton(QRunnable):
    def __init__(self, PIN: int, *args, **kwargs):
        super(HardwareButton, self).__init__()

        self.status = False
        self.PIN = PIN
        GPIO.setup(self.PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        self.signals = WorkerSignals()

    def run(self):
        while True:
            if GPIO.input(self.PIN) == False:         # Button press detected
                if self.status == False:              # Button was just OFF
                    self.signals.result.emit(True)
                    self.status = True              # Update the status to ON
            else:                                   # Button is not pressed
                self.status = False
            time.sleep(0.05)


# Custom Widgets & UI Elements
# TODO - add rotatable widget container

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

        self.setupWindowUI()
        self.setupLandscapeUI()

        self.setupThreads()

        self.show()
        # self.showFullScreen()

    def setupGPIO(self):
        # Set the GPIO mode, alternative is GPIO.BOARD
        GPIO.setmode(GPIO.BCM)

        # Hardware Pins
        self.PIN_ROTARY_A = 23
        self.PIN_ROTARY_B = 24
        self.PIN_ROTARY_BUTT = 25

        self.PIN_MODE = 20
        self.PIN_PREV = 6
        self.PIN_PLAY_PAUSE = 5
        self.PIN_NEXT = 13

        # Accelerometer

        # NeoPixels

        # LED indicators

    def setupWindowUI(self):
        # Window
        self.setWindowTitle("Capra Slideshow")
        self.setStyleSheet("background-color: blue;")

        # Grid - add all elements to the grid
        self.grid = QGridLayout()
        self.grid.setSpacing(0)
        self.grid.setContentsMargins(0, 0, 0, 0)

        # Widget
        w = QWidget()
        w.setLayout(self.grid)
        self.setCentralWidget(w)

    def setupLandscapeUI(self):
        # Image
        img = QPixmap(self.buildLandscape(2561))
        # self.img = self.img.scaled(640, 300)
        self.imgLabel = QLabel()
        self.imgLabel.setPixmap(img)
        self.grid.addWidget(self.imgLabel)

        # Label overlay
        testLabel = QLabel('Time Mode', self)
        testLabel.move(1100, 15)

        # Icon overlay
        modeBg = QLabel(self)
        modeBg.setStyleSheet("background-color: rgba(0, 0, 0, 0.3)")
        modeBg.setGeometry(0, 0, 1280, 720)

        modeImg = QPixmap('/home/pi/capra/icons/time.png')
        modeLabel = QLabel(self)  # need the self to set position absolutely
        modeLabel.setPixmap(modeImg)
        modeLabel.setGeometry(540, 260, 350, 200)  # left,top,w,h

    def setupVerticalUI(self):
        print('vertical')
        # img = QPixmap(self.buildFile(2561))

        # self.grid.addWidget(self.indexLabel, 3, 1)
        # self.grid.addWidget(self.button, 4, 1)
        # self.grid.addWidget(self.timerLabel, 2, 1)
        # self.grid.addWidget(self.workerThreadLabel, 5, 1)

        # self.addWidget(self.modeLabel)

    # Setup threads that check for changes to the hardware
    def setupThreads(self):
        self.threadpool = QThreadPool()
        self.threadpool.setMaxThreadCount(7)  # TODO - change if more threads are needed
        print(self.threadpool.maxThreadCount())

        # Rotary Encoder
        rotaryEncoder = RotaryEncoder(self.PIN_ROTARY_A, self.PIN_ROTARY_B)
        self.threadpool.start(rotaryEncoder)

        buttonEncoder = HardwareButton(self.PIN_ROTARY_BUTT)
        buttonEncoder.signals.result.connect(self.pressed_encoder)
        self.threadpool.start(buttonEncoder)

        # Buttons
        buttonMode = HardwareButton(self.PIN_MODE)
        buttonMode.signals.result.connect(self.pressed_mode)
        self.threadpool.start(buttonMode)

        buttonPrev = HardwareButton(self.PIN_PREV)
        buttonPrev.signals.result.connect(self.pressed_prev)
        self.threadpool.start(buttonPrev)

        buttonPlayPause = HardwareButton(self.PIN_PLAY_PAUSE)
        buttonPlayPause.signals.result.connect(self.pressed_play_pause)
        self.threadpool.start(buttonPlayPause)

        buttonNext = HardwareButton(self.PIN_NEXT)
        buttonNext.signals.result.connect(self.pressed_next)
        self.threadpool.start(buttonNext)

    # Keyboard presses
    def keyPressEvent(self, event):
        global rotaryCounter
        if event.key() == Qt.Key_Escape:
            self.close()
        elif event.key() == Qt.Key_Left:
            print('left')
            print(rotaryCounter)
            # self.updatePrev()
        elif event.key() == Qt.Key_Right:
            print('right')
            print(rotaryCounter)
            # self.updateNext()
        elif event.key() == Qt.Key_Space:
            print('space bar')
        else:
            print('other key pressed')

    # Hardware Button Presses
    def pressed_encoder(self, result):
        print('Encoder button was pressed: %d' % result)

    def pressed_mode(self, result):
        print('Mode button was pressed: %d' % result)

    def pressed_prev(self, result):
        print('Previous button was pressed: %d' % result)

    def pressed_play_pause(self, result):
        print('Play Pause button was pressed: %d' % result)

    def pressed_next(self, result):
        print('Next button was pressed: %d' % result)

    # def thread_result(self, result):
    #     print('From MainLoop: %d' % result)
    #     # self.workerThreadLabel.setText('Worker: %d' % result)

    #     img = QPixmap(self.buildFile(result))
    #     self.imgLabel.setPixmap(img)

    # UI Work
    def increment_label(self):
        self.index += 1
        self.indexLabel.setText('Count: %d' % self.index)

    # def recurring_timer(self):
    #     self.seconds += 1
    #     self.timerLabel.setText('Timer: %d' % self.seconds)

    # Helper Methods
    def buildLandscape(self, num) -> str:
        return '/home/pi/capra-storage/images/{n}_fullscreen.jpg'.format(n=num)

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
