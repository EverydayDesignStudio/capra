from envirophat import weather
from time import sleep
while(True):
    altitude = weather.altitude() + 90
    print altitude
    sleep(1)
