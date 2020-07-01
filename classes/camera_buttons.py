import time
import shared
import RPi.GPIO as GPIO
from classes.led_player import RGB_LED  # For controlling LED on Buttonboard
import globals as g
g.init()        # Initialize global constants
shared.init()   # Initialize shared variables


class PlayPauseButton:
    def __init__(self, BUTTON):
        self._running = True
        self.BUTTON = BUTTON
        GPIO.setup(self.BUTTON, GPIO.IN)

    def terminate(self):
        self._running = False

    def run(self):
        while self._running:
            print("=========Interrupt Start==========")
            GPIO.wait_for_edge(self.BUTTON, GPIO.RISING)
            shared.pause = not shared.pause
            print("Pause Button pressed | shared.pause = ", shared.pause)
            time.sleep(0.5)


class TurnOffButton:
    def __init__(self, BUTTON):
        self._running = True
        self.BUTTON = BUTTON
        GPIO.setwarnings(False)
        GPIO.setup(self.BUTTON, GPIO.IN)
        self.rgb_led = RGB_LED(g.LED_RED, g.LED_GREEN, g.LED_BLUE)  # red, green, blue LED

    def terminate(self):
        self._running = False

    def run(self):
        while self._running:
            print("=========Waiting for Turn Off=========")
            GPIO.wait_for_edge(self.BUTTON, GPIO.RISING)

            timer = 0
            duration = 10
            while GPIO.input(self.BUTTON):
                print("Turning off in: ", str(duration - timer))
                timer += 1
                time.sleep(0.2)
                if timer > duration:  # Set turn_off to True
                    shared.turn_off = True
                    self.rgb_led.turn_white()
                    # player.play_power_off_jingle()
                    # time.sleep(1)
                    # subprocess.call(['shutdown', '-h', 'now'], shell=False)
