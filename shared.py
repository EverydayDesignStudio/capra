# Shared variables for use between interrupts and main code
# =================================================

def init():
    print("Initializing shared variables")
    global pause
    pause = True

    global shutdown
    shutdown = False
