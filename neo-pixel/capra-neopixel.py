#!/usr/bin/env python3

import board
import neopixel
import time
import math


# Never directly set the NeoPixels, instead set pixel_values, then call _set_pixels()
# This way the values are stored and more clever affects are easily achieved
class NeoPixelPlayer:
    PERCENT_ON = 0
    NEOPIXEL_LENGTH = 0

    # Set this list & call _set_pixels() of directly setting the hardware
    pixel_values = []

    def __init__(self, pin: board, length: int):
        self.NEOPIXEL_LENGTH = length

        self.pixels = neopixel.NeoPixel(pin, length)
        print('NeoPixelPlayer object created for pin: {p} with length {l}'
              .format(p=pin, l=length))

        # Create starting values of each pixel
        for i in range(self.NEOPIXEL_LENGTH):
            self.pixel_values.append([0, 0, 0])

    # Functions
    # --------------------------------------------------------------------------
    def turn_on(self):
        self.pixels.fill((255, 255, 255))

    def turn_off(self):
        # self.pixels.fill((0, 0, 0))
        for i in range(self.NEOPIXEL_LENGTH):
            self.pixel_values[i] = [0, 0, 0]
            self._set_pixel(i)

    # Set percentage of the strip
    def set_strip_percentage(self, percent: float, power: float, animation: float):
        if percent > 1 or percent < 0:
            raise Exception('Percent was [{p}]  |  Must be  in range [0.00 - 1.00].'.format(p=percent))
        if power > 1 or power < 0:
            raise Exception('Power was [{p}]  |  Must be in range [0.00 - 1.00]'.format(p=power))

        # Set globals
        self.PERCENT_ON = percent

        # Set local variables
        pixels_to_lite = int(self.NEOPIXEL_LENGTH * percent)
        pr = int(255 * power)
        pg = int(255 * power)
        pb = int(255 * power)

        # Iterate through the entire list
        for i in range(pixels_to_lite):
            self.pixel_values[i] = (pr, pg, pb)
            self._set_pixel(i)
            # self.pixels[i] = (pr, pg, pb)
            time.sleep(animation)

    # Set percentage of the strip with a smooth affect
    # Still needs work
    def set_strip_percentage_smooth(self, percent: float, power: float, animation: float):
        if percent > 1 or percent < 0:
            raise Exception('Percent was [{p}]  |  Must be  in range [0.00 - 1.00].'.format(p=percent))
        if power > 1 or power < 0:
            raise Exception('Power was [{p}]  |  Must be in range [0.00 - 1.00]'.format(p=power))

        # Set globals
        self.PERCENT_ON = percent

        # Set local variables
        pixels_to_lite = int(self.NEOPIXEL_LENGTH * percent)
        pr = int(255 * power)
        pg = int(255 * power)
        pb = int(255 * power)

        subrange = 1
        # Iterate through the entire list
        for i in range(pixels_to_lite):
            # Change the colors for only the front subrange at a time
            for j in range(subrange - 5, subrange):
                if (j >= 0):
                    # print(self._is_pixel_off(j))
                    if self._is_pixel_off(j):
                        self.pixel_values[j] = [2, 2, 2]

                    z = 1.8
                    self.pixel_values[j][0] *= z
                    self.pixel_values[j][1] *= z
                    self.pixel_values[j][2] *= z
                    self._set_pixel(j)

            subrange += 1
            time.sleep(animation)

    def test1(self):
        self.pixel_values[5] = [4, 4, 4]
        self.pixel_values[6] = [40, 40, 40]
        self.pixel_values[7] = [150, 150, 150]
        self.pixel_values[8] = [40, 40, 40]
        self.pixel_values[9] = [4, 4, 4]

        self._set_pixels()

    def animate_out(self, speed: float):
        # Iterate through the entire list
        i = self.NEOPIXEL_LENGTH - 1
        while i >= 0:
            self.pixel_values[i] = [0, 0, 0]
            self._set_pixel(i)
            i -= 1
            time.sleep(speed)

    # ------------------------ Privates ------------------------
    def _set_pixel(self, index: int):
        # Do not int protect
        # self.pixels[index] = self.pixel_values[index]

        # Round to int
        temp = [0, 0, 0]
        temp[0] = int(self.pixel_values[index][0])
        temp[1] = int(self.pixel_values[index][1])
        temp[2] = int(self.pixel_values[index][2])
        self.pixels[index] = temp

    # Sets values of the entire strip based on the array
    def _set_pixels(self):
        for i in range(self.NEOPIXEL_LENGTH):
            self.pixels[i] = self.pixel_values[i]
            # print(self.pixels[i])

    def _is_pixel_off(self, index: int) -> bool:
        pixel = self.pixel_values[index]
        for i in range(3):
            if pixel[i] != 0:
                return False
        return True

    # Non blocking wait for NeoPixels
    def _neo_sleep(self):
        print('NOT YET IMPLEMENTED')


    # bright light at position and linear fade out to either side.
    # def indicator2(position: float):
    #     spread = 3.0
    #     brightstep = 255 / spread
    #     head ="led\tdist\tintns\tsec"
    #     print("======================")
    #     print(head)
    #     for p in range(PIXEL_AMOUNT):
    #         distance = round(float(p) - position, 3)
    #         if(abs(distance) < spread):
    #             intensity = cap_intensity(int(brightstep * (spread - int(abs(pow(distance, 1.7) )))))
    #             pixels[p] = (intensity, intensity, 0)
    #             print_pixel_info(p, distance, intensity, 0, "<<<")
    #         else:
    #             pixels[p] = (0, 0, 0)
    #             print_pixel_info(p, distance, 0, 0, "")
    #     pixels.show()


def main():
    NEOPIXEL_P = board.D18
    NEOPIXEL_L = 23
    neopixel_player = NeoPixelPlayer(NEOPIXEL_P, NEOPIXEL_L)

    neopixel_player.test1()
    time.sleep(4)
    neopixel_player.animate_out(0.02)

    neopixel_player.set_strip_percentage(.9, .2, .05)
    time.sleep(5)

    neopixel_player.turn_off()
    # time.sleep(1)

    # This sometimes doesn't work, but sometimes does
    # neopixel_player.set_strip_percentage_smooth(.75, .25, .04)

    # time.sleep(2)
    # neopixel_player.animate_out(0.02)


    # ------------------------ Example ------------------------
    # Hike position
    neopixel_player.set_strip_percentage_smooth(.85, .25, .03)
    time.sleep(2)
    neopixel_player.animate_out(0.02)

    # Hike altitude
    neopixel_player.set_strip_percentage_smooth(.25, .25, .03)
    time.sleep(2)
    neopixel_player.animate_out(0.02)

    # Hike color
    # TODO

    


    # neopixels.turn_on()
    # time.sleep(2.0)
    # neopixels.turn_off()

    # pixels[0] = (0, 0, 0)
    # pixels.fill((100, 100, 100))
    # print('We are pixeling')

    # Won't be able to use any sleeps in the actual code
    # time.sleep(1.0)
    # pixels.fill((0, 0, 0))
    # time.sleep(1.0)
    # pixels[10] = (255, 60, 200)

    # time.sleep(2.0)

    # set_strip_percentage(.80, 1, 1)


if __name__ == "__main__":
    main()
