#!/usr/bin/env python3

import RPi.GPIO as GPIO
import time
from classes.led_player import RGB_LED
import globals as g
g.init()

GPIO.setwarnings(False)     # Turn off GPIO warnings
GPIO.setmode(GPIO.BCM)      # Broadcom pin numbers

GPIO.setup(g.WHITE_LED1, GPIO.OUT)
GPIO.setup(g.WHITE_LED2, GPIO.OUT)
GPIO.setup(g.WHITE_LED3, GPIO.OUT)
rgb1 = RGB_LED(g.RGB1_RED, g.RGB1_GREEN, 0)
rgb2 = RGB_LED(g.RGB2_RED, g.RGB2_GREEN, g.RGB2_BLUE)


def run_white(pin, name):
    print('---------- ' + name + ' ----------')
    GPIO.output(pin, True)
    time.sleep(2)
    GPIO.output(pin, False)
    print('')


def run_rgb_colors(led, name):
    print('---------- ' + name + ' ----------')
    led.turn_off()
    print(name + ': red')
    led.turn_red()
    led.sleep_off()
    print(name + ': green')
    led.turn_green()
    led.sleep_off()
    print(name + ': blue')
    led.turn_blue()
    led.sleep_off()
    print(name + ': pink')
    led.turn_pink()
    led.sleep_off()
    print(name + ': teal')
    led.turn_teal()
    led.sleep_off()
    print(name + ': orange')
    led.turn_orange()
    led.sleep_off()
    print(name + ': white')
    led.turn_white()
    led.sleep_off()
    print(name + ': off\n')


print('')
run_white(g.WHITE_LED1, 'WHITE1')
run_white(g.WHITE_LED2, 'WHITE2')
run_white(g.WHITE_LED3, 'WHITE3')
run_rgb_colors(rgb1, 'RGB1')
run_rgb_colors(rgb2, 'RGB2')
