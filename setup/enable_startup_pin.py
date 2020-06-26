#!/usr/bin/env python3

# Add ability for LED to light up immediately during POWER ON
# Adds a single line to the /boot/config.txt

import os  # For calling shell commands


def main():
    print("Enabling startup PIN 14")
    change_config()


# /boot/config.txt
def change_config():
    with open("/boot/config.txt", "a") as file:
        file.write("\n# Keeps PIN 14 (TXD) pulled HIGH on startup\nenable_uart=1\n")
    print("✅ Updated /boot/config.txt")


if __name__ == "__main__":
    main()
