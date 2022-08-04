#!/usr/bin/env python3

# Sets system time (and consequently) the hwclock's time,
# via the Network Time Protocol (NTP) then turns it off.
# Now the system time will be kept with the hwclock, not through WiFi.

import os                       # For calling shell commands


def main():
    print("Setting the system clock to the RTC")
    turn_off_on_ntp()


def turn_off_on_ntp():
    os.popen('sudo timedatectl set-ntp true')
    print("✅ NTP sync turned ON")
    os.popen('sudo timedatectl set-ntp false')
    print("✅ NTP sync turned OFF")


if __name__ == "__main__":
    main()
