#!/usr/bin/env python3

# Sets the system clock on the Raspberry Pi to read
# from the hwclock which is the DS3231 Real Time Clock
# This has to be done upon setup of every new camera

import os                       # For calling shell commands


def main():
    print("Setting the system clock to the RTC")
    turn_off_on_ntp()


# sudo timedatectl set-ntp false
def turn_off_on_ntp():
    os.popen('sudo timedatectl set-ntp true')
    print("✅ NTP sync turned ON")
    os.popen('sudo timedatectl set-ntp false')
    print("✅ NTP sync turned OFF")


if __name__ == "__main__":
    main()
