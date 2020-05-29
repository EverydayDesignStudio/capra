#!/usr/bin/env python3

# Sets the system clock on the Raspberry Pi to read
# from the hwclock which is the DS3231 Real Time Clock
# This has to be done upon setup of every new camera

import os                       # For calling shell commands


def main():
    print("Setting the system clock to the RTC")
    change_config()
    remove_fake_hwclock()

# /boot/config.txt
def change_config():
    with open("/boot/config.txt", "a") as file:
        file.write("\n# RTC\ndtoverlay=i2c-rtc,ds3231\n")
    print("✅ Updated /boot/config.txt")

# Remove fake-hwclock which can interfere with the real hwclock
def remove_fake_hwclock():
    os.popen('sudo apt-get -y remove fake-hwclock').read()
    print("✅ Removed: apt-get -y remove fake-hwclock")

    os.popen('sudo update-rc.d -f fake-hwclock remove').read()
    print("✅ Removed: update-rc.d -f fake-hwclock remove")

    os.popen('sudo systemctl disable fake-hwclock').read()
    print("✅ Removed: systemctl disable fake-hwclock")

    print("🎉 fake-hwclock removed!")

if __name__ == "__main__":
    main()
