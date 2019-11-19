
import globals
import datetime

RETRY_MAX = 3;

# DB connection
conn = fn.getDBConn(globals.dbname_)
cur = conn.cursor()

retry = 0;

### How to keep track of a subprocess
# https://docs.python.org/3/library/subprocess.html
# https://stackoverflow.com/questions/43274476/is-there-a-way-to-check-if-a-subprocess-is-still-running

#   *** Transfer Animation: show warning if the file is not updating for ~5/10 mins
#
#
#   *** Should we check the internet connection?
#       >> TODO: check and align the timestamp
#
#   *** Do we want logging?
#
#
# Code flow
#
# while(true)
#   if (hall-effect-is-on)
#       if (not transfer)
#           try
#               turn the transfer flag on
#               start transfer script as a subprocess
#               start transfer-animation script as a subprocess
#           catch
#               retry in x secs
#                   >> ** shouldn't retry be in the transfer script? --> NO, subprocess dies whan the main dies
#                   // Parallel rsync is not ideal - https://stackoverflow.com/questions/24058544/speed-up-rsync-with-simultaneous-concurrent-file-transfers
#   else
#       if (transfer)
#           if (timeout)
#               stop transfering
#               gently stop transfer-animation
#
#       try
#           run explorer.py
#       catch
#           retry in x secs

#
#   def main():
#       try
#           mainLoop()
#       catch
#           if (retry < retry count)
#               retry
#           else
#               restart the script


################## Create Logger ##################
from logging.handlers import TimedRotatingFileHandler

logger = logging.getLogger("Main Log")
logger.setLevel(logging.INFO)

if os.name == 'nt':
    log_file = "C:\tmp\main.log"
else:
    log_file = "/home/pi/Desktop/olo/log_main/main.log"
    directory = "/home/pi/Desktop/olo/log_main/"
    if not os.path.exists(directory):
        os.makedirs(directory, exist_ok=True)

open(log_file, 'a')

handler = TimedRotatingFileHandler(log_file, when="midnight", interval=1)
logger.addHandler(handler)
###################################################

################################### Auxiliary Functions ###################################
current_milli_time = lambda: int(round(time.time() * 1000))
timenow = lambda: str(datetime.datetime.now()).split('.')[0]
############################### Initialize Global Variables ###############################

def capraMainLoop():
    while (True):


# -------------------------
def main():
    globals.init();

    while True:
        try:
        #    print("[{}]: ### Main is starting..".format(timenow()))
        #    logger.info("[{}]: ### Main is starting..".format(timenow()))
            capraMainLoop()
        except:
            retry += 1;
            if (retry >= RETRY_MAX):
                print("[{}]: !!!!   Couldn't retry,, restarting the script..".format(timenow()))
                logger.info("[{}]: !!!!   Couldn't retry,, restarting the script..".format(timenow()))
                # restart the program
                python = sys.executable
                os.execl(python, python, * sys.argv)

            conn.close()
            conn = None
            cur = None

        #    print("[{}]: !! Sleeping for 3 seconds,, Retry: {}".format(timenow(), retry))
        #    logger.info("[{}]: !! Sleeping for 3 seconds,, Retry: {}".format(timenow(), retry))
            time.sleep(3)

            continue;

if __name__ == "__main__": main()
