#!/usr/bin/env python3

import board
import getch
import neopixel
import time
import math
import RPi.GPIO as GPIO      # For interfacing with the pins of the Raspberry Pi

from classes.capra_data_types import Picture, Hike
from classes.sql_controller import SQLController  # For interacting with the DB

DB = '/home/pi/capra-storage/capra_projector_clean.db'
modes = ('time', 'altitude', 'color')


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

    def set_strip_color_percentage(self, r: int, g: int, b: int, percent: float):
        if percent > 1 or percent < 0:
            raise Exception('Percent was [{p}]  |  Must be  in range [0.00 - 1.00].'.format(p=percent))

        self.turn_off()
        # Set globals
        self.PERCENT_ON = percent
        power = 0.2

        # Set local variables
        pixels_to_lite = int(self.NEOPIXEL_LENGTH * percent)
        pr = int(r * power)
        pg = int(g * power)
        pb = int(b * power)

        # Iterate through the entire list
        for i in range(pixels_to_lite):
            self.pixel_values[i] = (pr, pg, pb)
            # self._set_pixel(i)
            self.pixels[i] = (pr, pg, pb)

    def set_strip_white_percentage(self, percent: float):
        if percent > 1 or percent < 0:
            raise Exception('Percent was [{p}]  |  Must be  in range [0.00 - 1.00].'.format(p=percent))

        self.turn_off()
        # Set globals
        self.PERCENT_ON = percent
        power = 0.2

        # Set local variables
        pixels_to_lite = int(self.NEOPIXEL_LENGTH * percent)
        pr = int(255 * power)
        pg = int(255 * power)
        pb = int(255 * power)

        # Iterate through the entire list
        for i in range(pixels_to_lite):
            self.pixel_values[i] = (pr, pg, pb)
            # self._set_pixel(i)
            self.pixels[i] = (pr, pg, pb)

    def set_strip_blue_percentage(self, percent: float):
        if percent > 1 or percent < 0:
            raise Exception('Percent was [{p}]  |  Must be  in range [0.00 - 1.00].'.format(p=percent))

        self.turn_off()
        # Set globals
        self.PERCENT_ON = percent
        power = 0.2

        # Set local variables
        pixels_to_lite = int(self.NEOPIXEL_LENGTH * percent)
        pr = int(10 * power)
        pg = int(10 * power)
        pb = int(255 * power)

        # Iterate through the entire list
        for i in range(pixels_to_lite):
            self.pixel_values[i] = (pr, pg, pb)
            # self._set_pixel(i)
            self.pixels[i] = (pr, pg, pb)

    def set_strip_red_percentage(self, percent: float):
        if percent > 1 or percent < 0:
            raise Exception('Percent was [{p}]  |  Must be  in range [0.00 - 1.00].'.format(p=percent))

        # Set globals
        self.PERCENT_ON = percent
        power = 0.3

        # Set local variables
        pixels_to_lite = int(self.NEOPIXEL_LENGTH * percent)
        pr = int(255 * power)
        pg = int(10 * power)
        pb = int(10 * power)

        # Iterate through the entire list
        for i in range(pixels_to_lite):
            self.pixel_values[i] = (pr, pg, pb)
            # self._set_pixel(i)
            self.pixels[i] = (pr, pg, pb)

    def set_strip_yellow_percentage(self, percent: float):
        if percent > 1 or percent < 0:
            raise Exception('Percent was [{p}]  |  Must be  in range [0.00 - 1.00].'.format(p=percent))

        # Set globals
        self.PERCENT_ON = percent
        power = 0.3

        # Set local variables
        pixels_to_lite = int(self.NEOPIXEL_LENGTH * percent)
        pr = int(255 * power)
        pg = int(255 * power)
        pb = int(10 * power)

        # Iterate through the entire list
        for i in range(pixels_to_lite):
            self.pixel_values[i] = (pr, pg, pb)
            # self._set_pixel(i)
            self.pixels[i] = (pr, pg, pb)

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

    def update_strip_percentage(self, percent: float, power: float):
        if percent > 1 or percent < 0:
            raise Exception('Percent was [{p}]  |  Must be  in range [0.00 - 1.00].'.format(p=percent))
        if power > 1 or power < 0:
            raise Exception('Power was [{p}]  |  Must be in range [0.00 - 1.00]'.format(p=power))

        self.PERCENT_ON = percent

    def small_range(self):
        self.pixel_values[5] = [4, 4, 4]
        self.pixel_values[6] = [6, 6, 6]
        self.pixel_values[7] = [12, 12, 12]
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

# class NeoPixelController:
#     def __init__(self):

def main():
    NEOPIXEL_P = board.D18
    NEOPIXEL_L = 23
    neopixel_player = NeoPixelPlayer(NEOPIXEL_P, NEOPIXEL_L)

    print('Starting NeoPixel / SQLite3 program')
    mode_index = 0
    sql_controller = SQLController(DB)
    current_picture = sql_controller.get_first_time_picture()

    # TODO - add starting animation
    # neopixel_player.set_strip_percentage_smooth(.2, .05, .04)
    # neopixel_player.set_strip_percentage_smooth(.75, 0.05, 0)

    '''
    SELECT PERCENT_RANK() OVER(ORDER BY time) time_percent
    FROM pictures WHERE hike=5 ORDER BY index_in_hike=80 DESC LIMIT 1;

    -- Altitude
    SELECT PERCENT_RANK() OVER(ORDER BY altitude) altitude_percent
    FROM pictures WHERE hike=5 ORDER BY index_in_hike=80 DESC LIMIT 1;
    '''

    '''
    Red         - Hikes
    Yellow      - Time
    Blue        - Altitude
    '''

    while True:
        keycode = ord(getch.getch())
        if keycode == 61:  # + key
            print('Next Hike')
            current_picture = sql_controller.first_picture_in_next_hike(current_picture)
            current_picture.print_obj_short()
            percent = sql_controller.get_percentage_of_hikes(current_picture)
            # print(percent)
            neopixel_player.turn_off()
            neopixel_player.set_strip_red_percentage(percent)
            time.sleep(1.0)
        elif keycode == 45:  # - key
            print('Previous Hike')
            current_picture = sql_controller.first_picture_in_previous_hike(current_picture)
            current_picture.print_obj_short()
            percent = sql_controller.get_percentage_of_hikes(current_picture)
            # print(percent)
            neopixel_player.turn_off()
            neopixel_player.set_strip_red_percentage(percent)

        if keycode == 67:  # Next
            print('NEXT in hike')
            if mode_index % 3 == 0:     # Time
                current_picture = sql_controller.next_time_picture_in_hike(current_picture)
                percent = sql_controller.get_percent_time_in_hike(current_picture)
                # neopixel_player.set_strip_white_percentage(percent)
                neopixel_player.set_strip_color_percentage(255, 255, 100, percent)  # yellowish

            elif mode_index % 3 == 1:   # Altitude
                current_picture = sql_controller.next_altitude_picture_in_hike(current_picture)
                percent = sql_controller.get_percent_altitude_in_hike(current_picture)
                # neopixel_player.set_strip_white_percentage(percent)
                neopixel_player.set_strip_color_percentage(150, 150, 255, percent)  # blueish

            elif mode_index % 3 == 2:   # Color
                print('color')
            current_picture.print_obj_short()

        elif keycode == 68:  # Previous
            print('PREVIOUS in hike')
            if mode_index % 3 == 0:     # Time
                current_picture = sql_controller.previous_time_picture_in_hike(current_picture)
                percent = sql_controller.get_percent_time_in_hike(current_picture)
                # neopixel_player.set_strip_white_percentage(percent)
                neopixel_player.set_strip_color_percentage(255, 255, 100, percent)  # yellowish

            elif mode_index % 3 == 1:   # Altitude
                current_picture = sql_controller.previous_altitude_picture_in_hike(current_picture)
                percent = sql_controller.get_percent_altitude_in_hike(current_picture)
                # neopixel_player.set_strip_white_percentage(percent)
                neopixel_player.set_strip_color_percentage(150, 150, 255, percent)  # blueish

            elif mode_index % 3 == 2:   # Color
                print('color')
            current_picture.print_obj_short()

        elif keycode == 65:  # Next across hikes
            print('NEXT across hikes')
            if mode_index % 3 == 0:     # Time
                current_picture = sql_controller.next_time_picture_across_hikes(current_picture)
                percent = sql_controller.get_percent_time_across_hikes(current_picture)
                neopixel_player.set_strip_color_percentage(255, 255, 10, percent)  # yellow

            elif mode_index % 3 == 1:   # Altitude
                current_picture = sql_controller.next_altitude_picture_across_hikes(current_picture)
                percent = sql_controller.get_percent_altitude_across_hikes(current_picture)
                neopixel_player.set_strip_color_percentage(50, 50, 255, percent)  # blue

            elif mode_index % 3 == 2:   # Color
                print('color')
            else:
                raise Exception('Error on changing modes')
            current_picture.print_obj_short()

        elif keycode == 66:  # Previous across hikes
            print('PREVIOUS across hikes')
            if mode_index % 3 == 0:     # Time
                current_picture = sql_controller.previous_time_picture_across_hikes(current_picture)
                percent = sql_controller.get_percent_time_across_hikes(current_picture)
                neopixel_player.set_strip_color_percentage(255, 255, 10, percent) # yellow

            elif mode_index % 3 == 1:   # Altitude
                current_picture = sql_controller.previous_altitude_picture_across_hikes(current_picture)
                percent = sql_controller.get_percent_altitude_across_hikes(current_picture)
                neopixel_player.set_strip_color_percentage(50, 50, 255, percent)  # blue

            elif mode_index % 3 == 2:   # Color
                print('color')
            else:
                raise Exception('Error on changing modes')
            current_picture.print_obj_short()

        elif keycode == 109:  # M - Change mode
            # print('MODE CHANGED')
            mode_index += 1
            print('CHANGE MODE to: ' + modes[mode_index % 3])

    # ------------------------ Example ------------------------
    # Hike position
    neopixel_player.set_strip_percentage_smooth(.85, .25, .03)
    time.sleep(50)
    neopixel_player.animate_out(0.02)

    # Hike altitude
    neopixel_player.set_strip_percentage_smooth(.25, .25, .03)
    time.sleep(2)
    neopixel_player.animate_out(0.02)

    # current_picture = sql_controller.get_greatest_altitude_picture()
    # current_picture = sql_controller.get_least_altitude_picture()

    # neopixel_player.set_strip_percentage(.6, .2, .05)
    # time.sleep(1)
    # neopixel_player.animate_out(0.02)

    # neopixel_player.turn_off()
    # time.sleep(1)

    # This sometimes doesn't work, but sometimes does
    # neopixel_player.set_strip_percentage_smooth(.75, .25, .04)

    # time.sleep(2)
    # neopixel_player.animate_out(0.02)



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
