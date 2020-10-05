#!/usr/bin/env python3

# ------------------------------------------------------------------------------
#  Slideshow program for the Explorer projector unit. Displays pictures and
#  allows navigation through them based on 3 modes: time, altitude, and color
# ------------------------------------------------------------------------------

# Imports
from classes.capra_data_types import Picture, Hike
from classes.sql_controller import SQLController
from classes.sql_statements import SQLStatements

from adafruit_mcp3xxx.analog_in import AnalogIn  # Reading values from MCP3008
from gpiozero import Button             # Rotary encoder, detected as button
from PIL import ImageTk, Image          # Pillow image functions
from RPi import GPIO                    # GPIO pin detection for Raspberry Pi
from tkinter import Tk, Canvas, Label   # Tkinter, GUI framework in use
from time import sleep                  # Sleep

import adafruit_mcp3xxx.mcp3008 as MCP  # Interfacing with MCP3008
import board                            # Dependancy of MCP3008
import busio                            # Dependancy of MCP3008
import digitalio                        # Dependancy of MCP3008
import datetime
import math

# Database location
# DB = '/home/pi/Pictures/capra-projector.db'
# PATH = '/home/pi/Pictures'

# DB = '/media/pi/capra-hd/capra_projector.db'
# PATH = '/media/pi/capra-hd'

DB = '/media/pi/capra-hd/jordan/capra_projector.db'
PATH = '/media/pi/capra-hd/jordan'

OFFSET = int(input('Input offset in Hike 10: '))

# GPIO BCM PINS
ROTARY_ENCODER_CLOCKWISE = 23
ROTARY_ENCODER_COUNTER = 24
ROTARY_ENCODER_BUTTON = 26  # Was 25, but was causing interferance with ADC chip

BUTTON_PLAY_PAUSE = 5
BUTTON_NEXT = 6
BUTTON_PREVIOUS = 12

# These are connected to MCP3008 on the board
BUTTON_MODE = 19

SLIDER_SWITCH_MODE_0 = 16
SLIDER_SWITCH_MODE_1 = 20
SLIDER_SWITCH_MODE_2 = 21

# ADC - MCP 3008 Channels
ACCELEROMETER_X = MCP.P7
ACCELEROMETER_Y = MCP.P6
ACCELEROMETER_Z = MCP.P5

# BUTTON_MODE = MCP.P2
# SLIDER_SWITCH_MODE_0 = MCP.P2
# SLIDER_SWITCH_MODE_1 = MCP.P1
# SLIDER_SWITCH_MODE_2 = MCP.P0

# SETUP BCM PINS
GPIO.setmode(GPIO.BCM)

# Rotary encoder
clk = ROTARY_ENCODER_CLOCKWISE
cnt = ROTARY_ENCODER_COUNTER
rotary_button = ROTARY_ENCODER_BUTTON
GPIO.setup(clk, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(cnt, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(rotary_button, GPIO.IN, pull_up_down=GPIO.PUD_UP)

# Buttons
GPIO.setup(BUTTON_PLAY_PAUSE, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(BUTTON_NEXT, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(BUTTON_PREVIOUS, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(BUTTON_MODE, GPIO.IN, pull_up_down=GPIO.PUD_UP)  # Because it's wired differently

GPIO.setup(SLIDER_SWITCH_MODE_0, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(SLIDER_SWITCH_MODE_1, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(SLIDER_SWITCH_MODE_2, GPIO.IN, pull_up_down=GPIO.PUD_UP)

# SETUP ADC CHANNELS - MCP3008
spi = busio.SPI(clock=board.SCK, MISO=board.MISO, MOSI=board.MOSI)
cs = digitalio.DigitalInOut(board.D8)
mcp = MCP.MCP3008(spi, cs)


# Slideshow class which is the main class that runs and is listening for events
class Slideshow:
    # GLOBAL CLASS STATE VARIABLES (COUNTERS, BOOLS, ETC)
    MODE = 0                        # 0 = Time | 1 = Altitude | 2 = Color # TODO - make into struct
    TRANSITION_DELAY = 4000         # Autoplay time between pictures (in milliseconds)
    IS_TRANSITION_FORWARD = True    # Autoplay direction (forward or backward)
    PLAY = True                     # Autoplay (Play/Pause) bool
    IS_ACROSS_HIKES = False         # Is rotary encoder pressed down
    ROTARY_COUNT = 0                # Used exclusively for testing rotary encoder steps

    def __init__(self, win):
        # Setup the window
        self.window = win
        self.window.title("Capra Slideshow")
        self.window.geometry("1280x720")
        # self.window.geometry("720x1280")
        self.window.configure(background='purple')
        self.canvas = Canvas(root, width=1280, height=720, background="#888", highlightthickness=0)
        # self.canvas.configure(bg='#444')
        self.canvas.pack(expand='yes', fill='both')

        # Hardware control events
        self.window.bind(GPIO.add_event_detect(clk, GPIO.BOTH, callback=self.detected_rotary_change))
        self.window.bind('<Key>', self.keypress)
        self.clkLastState = GPIO.input(clk)

        # Using GPIO.BOTH and GPIO input state, however I have noticed glitches. This will need to be ironed out
        # May need to use an after loop
        self.rotary_button_state = GPIO.input(rotary_button)
        self.rotary_button_state = not self.rotary_button_state  # default is True, so set it to False
        self.window.bind(GPIO.add_event_detect(rotary_button, GPIO.BOTH, callback=self.rotary_button_pressed))

        self.window.bind(GPIO.add_event_detect(BUTTON_PLAY_PAUSE, GPIO.FALLING, callback=self.button_pressed_play_pause))
        self.window.bind(GPIO.add_event_detect(BUTTON_NEXT, GPIO.FALLING, callback=self.button_pressed_next))
        self.window.bind(GPIO.add_event_detect(BUTTON_PREVIOUS, GPIO.FALLING, callback=self.button_pressed_previous))

        # self.window.bind(GPIO.add_event_detect(SLIDER_SWITCH_MODE_0, GPIO.FALLING, callback=self.switch_mode_0))
        # self.window.bind(GPIO.add_event_detect(SLIDER_SWITCH_MODE_1, GPIO.BOTH, callback=self.switch_mode_1))
        # self.window.bind(GPIO.add_event_detect(SLIDER_SWITCH_MODE_2, GPIO.FALLING, callback=self.switch_mode_2))

        self.determine_switch_mode()
        self.window.bind(GPIO.add_event_detect(BUTTON_MODE, GPIO.FALLING, callback=self.button_mode))

        # Initialization for database implementation
        self.sql_controller = SQLController(database=DB)
        # self.picture_starter = self.sql_controller.get_first_time_picture_in_hike(10)
        self.picture_starter = self.sql_controller.get_first_time_picture_in_hike_with_offset(10, OFFSET)
        self.picture = self.sql_controller.next_time_picture_in_hike(self.picture_starter)

        # Initialization for images and associated properties
        self.alpha = 0

        # Initialize current and next images
        # self.current_raw_top = Image.open(self._build_filename(self.picture_starter.camera1), 'r')
        # self.next_raw_top = Image.open(self._build_filename(self.picture.camera1), 'r')
        self.current_raw_mid = Image.open(self._build_filename(self.picture_starter.camera2), 'r')
        self.next_raw_mid = Image.open(self._build_filename(self.picture.camera2), 'r')
        # self.current_raw_bot = Image.open(blank_path, 'r')
        # self.next_raw_bot = Image.open(blank_path, 'r')
        # self.current_raw_bot = Image.open(self._build_filename(self.picture_starter.camera3), 'r')
        # self.next_raw_bot = Image.open(self._build_filename(self.picture.camera3), 'r')

        # Display the first 3 images to the screen
        # self.display_photo_image_top = ImageTk.PhotoImage(self.current_raw_top)
        # self.image_label_top = Label(master=self.canvas, image=self.display_photo_image_top, borderwidth=0)
        # self.image_label_top.pack(side='right', fill='both', expand='yes')
        # self.image_label_top.place(x=20, rely=0.0, anchor='nw')

        self.display_photo_image_mid = ImageTk.PhotoImage(self.current_raw_mid)
        self.image_label_mid = Label(master=self.canvas, image=self.display_photo_image_mid, borderwidth=0)
        self.image_label_mid.pack(side='right', fill='both', expand='yes')
        # self.image_label_mid.place(x=20, y=405, anchor='nw')

        # self.display_photo_image_bot = ImageTk.PhotoImage(self.current_raw_bot)
        # self.image_label_bot = Label(master=self.canvas, image=self.display_photo_image_bot, borderwidth=0)
        # self.image_label_bot.pack(side='right', fill='both', expand='yes')
        # self.image_label_bot.place(x=20, y=810, anchor='nw')

        # Hike labels
        # self.label_mode = Label(self.canvas, text='Modes: ')
        # self.label_hike = Label(self.canvas, text='Hike: ')
        # self.label_index = Label(self.canvas, text='Index: ')
        # self.label_alt = Label(self.canvas, text='Altitude: ')
        # self.label_date = Label(self.canvas, text='Date: ')

        # self.label_mode.place(relx=1.0, y= 0, anchor='ne')
        # self.label_hike.place(relx=1.0, y=22, anchor='ne')
        # self.label_index.place(relx=1.0, y=44, anchor='ne')
        # self.label_alt.place(relx=1.0, y=66, anchor='ne')
        # self.label_date.place(relx=1.0, y=88, anchor='ne')

        # Start background threads which will continue for life of the class
        # root.after(0, func=self.check_accelerometer)
        # root.after(10, func=self.update_text)
        root.after(15, func=self.fade_image)
        root.after(self.TRANSITION_DELAY, func=self.auto_play_slideshow)
        # root.after(0, func=self.check_mode)

    def _build_next_raw_images(self, next_picture: Picture):
        # print('build images')
        # self.next_raw_top = Image.open(self._build_filename(next_picture.camera1), 'r')
        self.next_raw_mid = Image.open(self._build_filename(next_picture.camera2), 'r')
        # self.next_raw_mid = Image.open(self._build_filename(next_picture.camera3), 'r')
        # self.next_raw_bot = Image.open(blank_path, 'r')

    def _build_filename(self, end_of_path: str) -> str:
        # return '{p}{e}'.format(p=PATH, e=end_of_path)
        return '{e}'.format(p=PATH, e=end_of_path)

    # Loops for the life of the program, fading between the current image and the NEXT image
    def fade_image(self):
        # print('Fading the image at alpha of: ', self.alpha)
        # print(time.time())
        if self.alpha < 1.0:
            # Top image
            # self.current_raw_top = Image.blend(self.current_raw_top, self.next_raw_top, self.alpha)
            # self.current_raw_top = self.next_raw_top
            # self.display_photo_image_top = ImageTk.PhotoImage(self.current_raw_top)
            # self.image_label_top.configure(image=self.display_photo_image_top)

            # Middle image
            self.current_raw_mid = Image.blend(self.current_raw_mid, self.next_raw_mid, self.alpha)
            # self.current_raw_mid = self.next_raw_mid
            self.display_photo_image_mid = ImageTk.PhotoImage(self.current_raw_mid)
            self.image_label_mid.configure(image=self.display_photo_image_mid)

            # Bottom image
            # self.current_raw_bot = Image.blend(self.current_raw_bot, self.next_raw_bot, self.alpha)
            # self.current_raw_bot = self.next_raw_bot
            # self.display_photo_image_bot = ImageTk.PhotoImage(self.current_raw_bot)
            # self.image_label_bot.configure(image=self.display_photo_image_bot)

            self.alpha = self.alpha + 0.0417
            # self.alpha = self.alpha + 0.0209
        root.after(83, self.fade_image)

    def update_text(self):
        self.determine_switch_mode()
        if self.MODE == 0:
            mode = 'Mode: Time'
        elif self.MODE == 1:
            mode = 'Mode: Altitude'
        elif self.MODE == 2:
            mode = 'Mode: Color'
        else:
            mode = 'Mode: ERROR'

        hike = 'Hike {n}'.format(n=self.picture.hike_id)

        hike_sz = self.sql_controller.get_size_of_hike(self.picture)
        index = '{x} / {n}'.format(x=self.picture.index_in_hike, n=hike_sz)

        altitude = '{a}m'.format(a=self.picture.altitude)

        value = datetime.datetime.fromtimestamp(self.picture.time)
        date_time = value.strftime('%-I:%M:%S%p on %d %b, %Y')
        date = '{d}'.format(d=date_time)

        self.label_mode.configure(text=mode)
        self.label_hike.configure(text=hike)
        self.label_index.configure(text=index)
        self.label_alt.configure(text=altitude)
        self.label_date.configure(text=date)

        root.after(500, self.update_text)

    # TODO - track down where the random number being printed to the terminal is coming from
    def auto_play_slideshow(self):
        # print('Auto incremented slideshow')
        if (self.PLAY):
            if self.IS_TRANSITION_FORWARD:          # Advance forward on autoplay
                self.picture = self.sql_controller.get_next_picture(
                    current_picture=self.picture, mode=self.MODE, is_across_hikes=self.IS_ACROSS_HIKES)
                self._build_next_raw_images(self.picture)
                self.alpha = .2
                self.picture.print_obj()            # This is a print()
            else:                                   # Advance backward on autoplay
                self.picture = self.sql_controller.get_previous_picture(
                    current_picture=self.picture, mode=self.MODE, is_across_hikes=self.IS_ACROSS_HIKES)
                self._build_next_raw_images(self.picture)
                self.alpha = .2
                self.picture.print_obj()            # This is a print()

        root.after(self.TRANSITION_DELAY, self.auto_play_slideshow)

    # BCM HARDWARE CONTROLS
    def detected_rotary_change(self, event):
        clkState = GPIO.input(clk)
        cntState = GPIO.input(cnt)

        # The encoder has moved
        if clkState != self.clkLastState:
            self.determine_switch_mode()
            # Increment
            if cntState != clkState:
                # Next picture
                self.IS_TRANSITION_FORWARD = True   # For auto slideshow
                self.ROTARY_COUNT += 1
                print("Rotary +: ", self.ROTARY_COUNT)

                self.picture = self.sql_controller.get_next_picture(
                    current_picture=self.picture, mode=self.MODE, is_across_hikes=self.IS_ACROSS_HIKES)
                self._build_next_raw_images(self.picture)
                self.alpha = .2                     # Resets amount of fade between pictures
                self.picture.print_obj()            # This is a print()
            # Decrement
            else:
                # Previous picture
                self.IS_TRANSITION_FORWARD = False  # For auto slideshow
                self.ROTARY_COUNT -= 1
                print("Rotary -: ", self.ROTARY_COUNT)

                self.picture = self.sql_controller.get_previous_picture(
                    current_picture=self.picture, mode=self.MODE, is_across_hikes=self.IS_ACROSS_HIKES)
                self._build_next_raw_images(self.picture)
                self.alpha = .2                     # Resets amount of fade between pictures
                self.picture.print_obj()            # This is a print()
        self.clkLastState = clkState
        # TODO - try around with this in or out depending on the rotary encoder
        # sleep(0.1)

    def rotary_button_pressed(self, event):
        print('rotary pressed')
        self.IS_ACROSS_HIKES = not self.IS_ACROSS_HIKES
        print('Is across hikes: {i}'.format(i=self.IS_ACROSS_HIKES))

        # Another way to detect rotary encoder button press
        # self.rotary_button_state = not self.rotary_button_state
        # print('Rotary button state: {i}'.format(i=self.rotary_button_state))

        # sleep(0.1)

    def button_pressed_play_pause(self, event):
        self.PLAY = not self.PLAY
        if self.PLAY:
            print('Pressed Play')
        else:
            print('Pressed Pause')

    def button_pressed_next(self, event):
        print('Next pressed')

    def button_pressed_previous(self, event):
        print('Previous pressed')

    def button_mode(self, event):
        # self.MODE += 1
        # self.MODE = self.MODE % 3  # to loop count back to 0 from 3
        print('Mode button not incrementing | Current mode = {n}'.format(n=self.MODE))

    def determine_switch_mode(self):
        switch_mode_0_state = GPIO.input(SLIDER_SWITCH_MODE_0)
        switch_mode_1_state = GPIO.input(SLIDER_SWITCH_MODE_1)
        switch_mode_2_state = GPIO.input(SLIDER_SWITCH_MODE_2)

        # print(switch_mode_0_state)
        # print(switch_mode_1_state)
        # print(switch_mode_2_state)

        if switch_mode_0_state == 0:
            self.MODE = 0
        elif switch_mode_1_state == 0:
            self.MODE = 1
        elif switch_mode_2_state == 0:
            self.MODE = 2
        else:
            print("ERROR")
        # print('MODE: {m}'.format(m=self.MODE))

    def keypress(self, event):
        if event.keycode == 114:  # Right / Next
            # print('right')
            self.picture = self.sql_controller.get_next_picture(
                    current_picture=self.picture, mode=self.MODE, is_across_hikes=self.IS_ACROSS_HIKES)
            self._build_next_raw_images(self.picture)
            self.alpha = .2                     # Resets amount of fade between pictures
            self.picture.print_obj()            # This is a print()
        elif event.keycode == 113:  # Left / Previous
            # print('left')
            self.picture = self.sql_controller.get_previous_picture(
                    current_picture=self.picture, mode=self.MODE, is_across_hikes=self.IS_ACROSS_HIKES)
            self._build_next_raw_images(self.picture)
            self.alpha = .2                     # Resets amount of fade between pictures
            self.picture.print_obj()            # This is a print()
        else:
            print(event)

    # ADC HARDWARE CONTROLS
    # def check_accelerometer(self):
    #     ax = AnalogIn(mcp, ACCELEROMETER_X).value
    #     ay = AnalogIn(mcp, ACCELEROMETER_Y).value
    #     az = AnalogIn(mcp, ACCELEROMETER_Z).value

    #     pitch = 180 * math.atan(ax/math.sqrt(ay*ay + az*az))/math.pi
    #     roll = 180 * math.atan(ay/math.sqrt(ax*ax + az*az))/math.pi

    #     if pitch > 35 and roll < 34:
    #         orientation = 'correct vertical'
    #     elif pitch < 31 and roll > 34:
    #         orientation = 'upside down vertical'
    #     else:
    #         orientation = 'horizontal'
    #     # print(orientation)

        # TODO - calculate pitch and roll correctly
        # if roll > -45 and roll < 45:
        #    orientation = 'landscape'
        # elif roll >= 45 or roll <= -45:
        #    orientation = 'vertical'

        # root.after(500, self.check_accelerometer)

    # last_value = 65472
    # def check_mode(self):
        # sw1 = AnalogIn(mcp, SLIDER_SWITCH_MODE_0).value
        # sw2 = AnalogIn(mcp, SLIDER_SWITCH_MODE_1).value
        # sw3 = AnalogIn(mcp, SLIDER_SWITCH_MODE_2).value

        # value = AnalogIn(mcp, BUTTON_MODE).value
        # print(value)

        # if value < 35500 and self.last_value > 61500:
        #     print('press')
        #     self.last_value = value
        # elif value > 61500 and self.last_value < 35500:
        #     print('released')
        #     self.last_value = value

        #  = chan0.value
        # self.MODE += 1
        # self.MODE = self.MODE % 3       # to loop count back to 0 from 3
        # print('mode = {n}'.format(n=self.MODE))

        # root.after(500, self.check_mode)


# Create the root window
root = Tk()

root.attributes("-fullscreen", False)
root.bind("<Escape>", exit)
slide_show = Slideshow(root)
root.mainloop()
