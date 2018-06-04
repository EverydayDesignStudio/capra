import os

target = raw_input("target: ")
target = '../' + target
if (os.path.exists(target)):
    print 'hello'
