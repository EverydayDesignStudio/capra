# https://docs.python.org/3/library/threading.html
# https://stackoverflow.com/questions/190010/daemon-threads-explanation
# https://stackoverflow.com/questions/23100704/running-infinite-loops-using-threads-in-python

import time
import threading
import datetime
from random import randint
# import globals as g
# g.init()

TEST_VAR = 0


class capraUpdateThread(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        # deploy this as a background process
        self.daemon = True
        self.start()

    def run(self):
        while True:
            # g.TEST_VAR = time.ctime(time.time())
            TEST_VAR = time.ctime(time.time())


def timenow():
    return str(datetime.datetime.now()).split('.')[0]


def update():
    while True:
        # g.TEST_VAR = time.ctime(time.time())
        TEST_VAR = time.ctime(time.time())


print("Starting Main Thread")
count = 10
print("Starting Daemon Thread")
capraUpdateThread()

print("Starting Main Loop")
# main capra loop for slideshow
while count:
    # print(g.TEST_VAR)
    print(TEST_VAR)
    time.sleep(randint(1, 5))

    # do stuff

    count -= 1

print("Exiting Main Thread")
