import RPi.GPIO as gpio
import board
import neopixel
import time
import math

PIXEL_AMOUNT = 10       # The amount of NeoPixels on the strip
ORDER = neopixel.GRB
PIXEL_PIN = board.D18
HUE = (200, 30, 0)

pixels = neopixel.NeoPixel(PIXEL_PIN, PIXEL_AMOUNT, brightness=0.2, auto_write=False, pixel_order=ORDER)
pos = 8

def reset_pixels():
    pixels.fill((0, 0, 0))

# progression of intense pixels followed by a last fade in pixel
def indicator1(position: float):
    brights = int(position)

    for p in range(brights):
        pixels[p] = HUE

    intensity = int(255 * (position % 1) )
    print("pos:", position, "  b:", brights, "  i", intensity)

    # colour of LED (has to be in integers)
    red = HUE[0]
    green = int(0.3* math.sin((3.14/2) * (position % 1)) * HUE[1])
    blue = int(0 * HUE[2])

    pixels[brights] = (red, green, blue)
    pixels.show()

# bright light at position and linear fade out to either side.
def indicator2(position: float):
    spread = 3.0
    brightstep = 255 / spread
    for p in range(PIXEL_AMOUNT):
        distance = float(p) - position
        if(abs(distance) < spread):
            intensity = int(brightstep * int(abs(distance)))
            pixels[p] = (0, intensity, intensity)
    pixels.show()

# bright light at position and exponential fade out to either side
def indicator3(position: float):
    spread = 3.0
    brightstep = 255 / spread
    for p in range(PIXEL_AMOUNT):
        distance = float(p) - position
        if(abs(distance) < spread):
            intensity = int(brightstep * int(pow(abs(distance)), 1.7))
            pixels[p] = (0, intensity, intensity)
    pixels.show()

# bright light at position and exponential fade out to either side; brighter, less saturated
# light at center through secondary_intensity
def indicator4(position: float):
    spread = 3.0
    brightstep = 255 / spread
    for p in range(PIXEL_AMOUNT):
        distance = float(p) - position
        if(abs(distance) < spread):
            intensity = int(brightstep * int(pow(abs(distance)), 1.7))
            secondary_intensity = 0
            if(intensity > 170):
                secondary_intensity = intensity/3
            pixels[p] = (secondary_intensity, intensity, secondary_intensity)
    pixels.show()


while(1):
    while(int(pos) < PIXEL_AMOUNT):
        indicator1(pos)
        time.sleep(0.1)
        pos += 0.05
    pos = 0
    reset_pixels

    while(int(pos) < PIXEL_AMOUNT):
        indicator2(pos)
        time.sleep(0.1)
        pos += 0.05
    pos = 0
    reset_pixels

    while(int(pos) < PIXEL_AMOUNT):
        indicator3(pos)
        time.sleep(0.1)
        pos += 0.05
    pos = 0
    reset_pixels

    while(int(pos) < PIXEL_AMOUNT):
        indicator4(pos)
        time.sleep(0.1)
        pos += 0.05
    pos = 0
    reset_pixels
    
