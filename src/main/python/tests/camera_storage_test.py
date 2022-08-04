#!/usr/bin/env python3

import time
import sys
import psutil  # For checking free space of system


path = '/home/pi/'


def write(line):
    sys.stdout.write(line)
    sys.stdout.flush()


write("--- Storage Space ---")
# Main loop to read the sensor values and print them every half second
while True:
    low_storage = False
    bytes_available = psutil.disk_usage(path).free
    megs_available = round(bytes_available / 1024 / 1024, 0)
    gigs_available = round(bytes_available / 1024 / 1024 / 1024, 2)
    if megs_available < 512:
        output = """
🔴💾 Low Storage!
{g} GB
{m:0.0f} MB
""".format(g=gigs_available, m=megs_available)
    else:
        output = """
{g} GB
{m:0.0f} MB
""".format(g=gigs_available, m=megs_available)

    time.sleep(0.5)

    output = output.replace("\n", "\n\033[K")
    write(output)
    lines = len(output.split("\n"))
    write("\033[{}A".format(lines - 1))
