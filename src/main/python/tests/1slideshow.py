#!/usr/bin/env python3


# Continually adds numbers on a background thread and 
# passes it up to the mainloop once every 1 second


from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from RPi import GPIO

import sys
import time
import traceback

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

        GPIO.setmode(GPIO.BCM)
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
                    self.signals.result.emit(self.count)
                else:
                    self.count -= 1
                    self.signals.result.emit(self.count)
                # print(counter)
            self.clkLastState = self.clkState

    '''
    def run(self):
        while True:
            # print('Worker.count: %d' % self.count)
            self.count += 1
            time.sleep(1)
            self.signals.result.emit(self.count)
    '''

class MainWindow(QMainWindow):
    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)
        self.threadpool = QThreadPool()

        self.index = 0
        self.seconds = 0

        # Layout
        layout = QVBoxLayout()

        self.title = QLabel("Background Thread Test")
        self.indexLabel = QLabel("Count: 0")
        self.timerLabel = QLabel("Timer: 0")
        self.workerThreadLabel = QLabel("Worker: 0")

        self.button = QPushButton("Increment Count")
        self.button.pressed.connect(self.increment_label)

        layout.addWidget(self.title)
        layout.addWidget(self.indexLabel)
        layout.addWidget(self.timerLabel)
        layout.addWidget(self.button)
        layout.addWidget(self.workerThreadLabel)

        # Widget
        w = QWidget()
        w.setLayout(layout)
        self.setCentralWidget(w)
        self.show()

        # Timer
        self.timer = QTimer()
        self.timer.setInterval(1000)
        self.timer.timeout.connect(self.recurring_timer)
        self.timer.start()

        # Start the bg Thread
        self.worker = Worker()
        self.worker.signals.result.connect(self.thread_result)
        self.threadpool.start(self.worker)
        # self.worker.run()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape:
            self.close()
        elif event.key() == Qt.Key_Left:
            print('left')
            # self.updatePrev()
        elif event.key() == Qt.Key_Right:
            print('right')
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
        self.workerThreadLabel.setText('Worker: %d' % result)

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
