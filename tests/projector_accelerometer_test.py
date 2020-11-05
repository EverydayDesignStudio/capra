#!/usr/bin/env python3

# Test for LSM303D accelerometer from Polulu

import math
import sys
import time
from lsm303d import LSM303D

# Tuple of x, y, z acceleration values
lsm = LSM303D(0x1d)  # Change to 0x1e if you have soldered the address jumper


def write(line):
    sys.stdout.write(line)
    sys.stdout.flush()


write("--- Polulu LSM303D Accelerometer ---")


try:
    while True:
        try:
            xyz = lsm.accelerometer()
        except Exception as error:
            time.sleep(2.0)
            continue
            raise Exception("Oops! There was no valid accelerometer data.")

        # xyz = lsm.accelerometer()

        ax = round(xyz[0], 7)
        ay = round(xyz[1], 7)
        az = round(xyz[2], 7)

        pitch = round(180 * math.atan(ax/math.sqrt(ay*ay + az*az))/math.pi, 3)
        roll = round(180 * math.atan(ay/math.sqrt(ax*ax + az*az))/math.pi, 3)

        if abs(pitch) < 20:
            if roll < -45:
                orientation = 'correct vertical'
            elif roll > 45:
                orientation = 'upside-down vertical'
            else:
                orientation = 'horizontal'
        else:
            if roll < -30:
                orientation = 'correct vertical'
            elif roll > 30:
                orientation = 'upside-down vertical'
            else:
                orientation = 'horizontal'

        output = """
    Accelerometer: {x}g {y}g {z}g

    Pitch: {p}
    Roll: {r}

    Orientation: {o}

    """.format(x=ax, y=ay, z=az, p=pitch, r=roll, o=orientation)

        output = output.replace("\n", "\n\033[K")
        write(output)
        lines = len(output.split("\n"))
        write("\033[{}A".format(lines - 1))

        time.sleep(1)

except KeyboardInterrupt:
    pass
