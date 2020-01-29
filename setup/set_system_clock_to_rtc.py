#!/usr/bin/env python3

# Sets the system clock on the Raspberry Pi to read
# from the hwclock which is the DS3231 Real Time Clock
# This has to be done upon setup of every new camera

import os                       # For calling shell commands
import time                     # For unix timestamps


def main():
    print("Setting the system clock to the RTC")
    change_config()
    turn_off_on_ntp()


# /boot/config.txt
def change_config():
    with open("/boot/config.txt", "a") as file:
        file.write("# RTC\ndtoverlay=i2c-rtc,ds3231\n")
    print("✅ Updated /boot/config.txt")


# sudo timedatectl set-ntp false
def turn_off_on_ntp():
    os.popen('sudo timedatectl set-ntp true')
    print("✅ NTP sync turned ON")
    os.popen('sudo timedatectl set-ntp false')
    print("✅ NTP sync turned OFF")


# Helper function which isn't used
def get_time():
    timestamp = time.time()
    return timestamp


if __name__ == "__main__":
    main()
