import RPi.GPIO as gpio
import board
import neopixel
import time
import math

PIXEL_AMOUNT = 25       # The amount of NeoPixels on the strip
ORDER = neopixel.GRB
PIXEL_PIN = board.D18
HUE = (200, 30, 0)

pixels = neopixel.NeoPixel(PIXEL_PIN, PIXEL_AMOUNT, brightness=0.2, auto_write=False, pixel_order=ORDER)
pos = 8

def cap_intensity(val):
    if(val > 255):
        val = 255
    if(val < 0):
        val = 0
    return val

def reset_pixels():
    pixels.fill((0, 0, 0))
    pixels.show()

def print_pixel_info(_pixel, _dist, _intensity, _second, _marker):
    stats ="{le}\t{di}\t{inte}\t{se}\t{marker}"
    print(stats.format(le=str(_pixel), di=str(_dist), inte=str(_intensity), se=str(_second), marker=_marker))

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
    head ="led\tdist\tintns\tsec"
    print("======================")
    print(head)
    for p in range(PIXEL_AMOUNT):
        distance = round(float(p) - position, 3)
        if(abs(distance) < spread):
            intensity = cap_intensity(int(brightstep * (spread - int(abs(pow(distance, 1.7) )))))
            pixels[p] = (intensity, intensity, 0)
            print_pixel_info(p, distance, intensity, 0, "<<<")
        else:
            pixels[p] = (0, 0, 0)
            print_pixel_info(p, distance, 0, 0, "")
    pixels.show()

# bright light at position and exponential fade out to either side
def indicator3(position: float):
    spread = 5.0
    brightstep = 255 / spread
    head ="led\tdist\tintns\tsec"
    print("======================")
    print(head)
    for p in range(PIXEL_AMOUNT):
        distance = round(float(p) - position, 3)
        if(abs(distance) < spread):
            intensity = cap_intensity( int(brightstep * (spread - int(pow(abs(distance), 1.7)))) )
            pixels[p] = (0, intensity, intensity)
            print_pixel_info(p, distance, intensity, 0, "<<<")
        else:
            pixels[p] = (0, 0, 0)
            print_pixel_info(p, distance, 0, 0, "")
    pixels.show()

# bright light at position and exponential fade out to either side; brighter, less saturated
# light at center through secondary_intensity
def indicator4(position: float):
    spread = 3.0
    brightstep = 100 / spread
    head ="led\tdist\tintns\tsec"
    mrk = ""
    print("======================")
    print(round(position, 3))
    print(head)
    for p in range(PIXEL_AMOUNT):
        distance = round(float(p) - position, 3)
        if(abs(distance) < spread):
            intensity = cap_intensity( int(brightstep * (spread - pow(abs(distance), 0.7))))
            secondary_intensity = 0
            mrk = "<"
            if(intensity > 50):
                secondary_intensity = int(intensity/1.5)
                mrk = "<<<"
            pixels[p] = (secondary_intensity, intensity, secondary_intensity)
            print_pixel_info(p, distance, intensity, secondary_intensity, mrk)
        else:
            pixels[p] = (0, 0, 0)
            print_pixel_info(p, distance, 0, 0, "")

    pixels.show()


while(1):
    while(int(pos) < PIXEL_AMOUNT):
        indicator1(pos)
        #time.sleep(0.1)
        pos += 0.05
    pos = 0
    reset_pixels()

    while(int(pos) < PIXEL_AMOUNT):
        indicator2(pos)
        time.sleep(0.1)
        #pos += 0.05
    pos = 0
    reset_pixels()
    pos = PIXEL_AMOUNT

    while(int(pos) > 0):
        indicator2(pos)
        #time.sleep(0.1)
        pos -= 0.05
    pos = 0
    reset_pixels()


    while(int(pos) < PIXEL_AMOUNT):
        indicator4(pos)
        #time.sleep(0.1)
        pos += 0.05
    pos = 0
    reset_pixels()
    pos = PIXEL_AMOUNT

    while(int(pos) > 0):
        indicator4(pos)
        #time.sleep(0.1)
        pos -= 0.05
    pos = 0
    reset_pixels()


    while(int(pos) < 256):
        color = (int(pos), int(pos), int(pos))
        pixels.fill(color)
        pixels.show()
        print("FILL:", pos)
        #time.sleep(0.05)
        pos += 1
    reset_pixels()
    pos = 0

    while(int(pos) < 256):
        color = ((int(pos), 0, 0))
        pixels.fill(color)
        pixels.show()
        print("FILL:", pos)
        #time.sleep(0.05)
        pos += 1
    reset_pixels()
    pos = 0

    while(int(pos) < 256):
        color = (0, int(pos), 0)
        pixels.fill(color)
        pixels.show()
        print("FILL:", pos)
        #time.sleep(0.05)
        pos += 1
    reset_pixels()
    pos = 0
