#!/usr/bin/env python3

import RPi.GPIO as GPIO
import time
import sys
import globals as g
g.init()

GPIO.setmode(GPIO.BCM)
# GPIO.setwarnings(False)
GPIO.setup(g.HALL_EFFECT_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(g.BUTT_MODE, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(g.BUTT_PLAY_PAUSE, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(g.BUTT_PREV, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(g.BUTT_NEXT, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(g.OFF_BUTTON, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(g.ON_BUTTON, GPIO.IN)

GPIO.setup(g.ENC1_BUTT, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(g.ENC1_A, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(g.ENC1_B, GPIO.IN, pull_up_down=GPIO.PUD_UP)


def write(line):
    sys.stdout.write(line)
    sys.stdout.flush()


def full_write(output):
    output = output.replace("\n", "\n\033[K")
    write(output)
    lines = len(output.split("\n"))
    write("\033[{}A".format(lines - 1))


write("----- Test Button & Rotary Encoder Values -----")


def main():
    while True:
        hall_effect_stat = ""
        mode_stat = ""
        play_pause_stat = ""
        prev_stat = ""
        next_stat = ""
        off_stat = ""
        on_stat = ""
        enc1_stat = ""

        if GPIO.input(g.HALL_EFFECT_PIN) == 0:
            hall_effect_stat = 'Magnet Near'
        if GPIO.input(g.BUTT_MODE) == 0:
            mode_stat = 'Pressed'
        if GPIO.input(g.BUTT_PLAY_PAUSE) == 0:
            play_pause_stat = 'Pressed'
        if GPIO.input(g.BUTT_PREV) == 0:
            prev_stat = 'Pressed'
        if GPIO.input(g.BUTT_NEXT) == 0:
            next_stat = 'Pressed'
        if GPIO.input(g.OFF_BUTTON) == 1:
            off_stat = 'Pressed'
        on_stat = GPIO.input(g.ON_BUTTON)
        if GPIO.input(g.ENC1_BUTT) == 0:
            enc1_stat = 'Pressed'

        output = """
Hall Effect:{he}

Mode:       {m}
Previous:   {pr}
Play Pause: {pl}
Next:       {n}

Encoder:    {e}

On:         {on}
Off:        {off}
""".format(he=hall_effect_stat, m=mode_stat, pl=play_pause_stat, pr=prev_stat,
           n=next_stat, off=off_stat, on=on_stat, e=enc1_stat)
        full_write(output)

        time.sleep(0.1)


# def main():
    # while True:
    #     GPIO.wait_for_edge(g.BUTT_MODE, GPIO.FALLING)
    #     GPIO.wait_for_edge(g.BUTT_PREV, GPIO.FALLING)

    #     print('hi there people')


    # while True:
    #     if mode.is_pressed:
    #         print("Mode is: pressed")
    #     else:
    #         print("Mode is:")


# def main():
    # GPIO.add_event_callback(g.BUTT_MODE, GPIO.BOTH, callback=modePress)
    # GPIO.add_event_detect(g.BUTT_MODE, GPIO.FALLING, callback=modePress, bouncetime=300)

    # try:
    #     GPIO.wait_for_edge(g.BUTT_MODE, GPIO.RISING)
    # except:
    #     print('howdy')

    # GPIO.add_event_callback(g.BUTT_MODE, callback=modePress)
    # while True:
    #     time.sleep(.1)

        # print(GPIO.input(g.HALL_EFFECT_PIN))
        # print(GPIO.input(g.BUTT_MODE))
        # print(GPIO.input(g.BUTT_PAUSE))


# def main():
#     write("----- Test Button & Rotary Encoder Values -----")

#     while True:
#         hall_effect = GPIO.input(g.HALL_EFFECT_PIN)
#         if hall_effect == 1:
#             hall_effect_stat = 'Magnet Near'
#         else:
#             hall_effect_stat = ''

#         mode = GPIO.input(g.BUTT_MODE)
#         if mode == 1:
#             mode_stat = 'Pressed'
#         else:
#             mode_stat = ''

#         time.sleep(0.05)

#         output = """
# Hall Effect: {he}
# Mode Button: {m}
# """.format(he=hall_effect_stat, m=mode_stat)

#         output = output.replace("\n", "\n\033[K")
#         write(output)
#         lines = len(output.split("\n"))
#         write("\033[{}A".format(lines - 1))


if __name__ == "__main__":
    main()
