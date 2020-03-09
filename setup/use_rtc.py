#!/usr/bin/env python3

# Sets the system clock on the Raspberry Pi to read
# from the hwclock which is the DS3231 Real Time Clock
# This has to be done upon setup of every new camera

import os                       # For calling shell commands


def main():
    print("Setting the system clock to the RTC")
    change_config()


# /boot/config.txt
def change_config():
    with open("/boot/config.txt", "a") as file:
        file.write("\n# RTC\ndtoverlay=i2c-rtc,ds3231\n")
    print("✅ Updated /boot/config.txt")


if __name__ == "__main__":
    main()
