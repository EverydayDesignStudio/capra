#!/usr/bin/env python3

import time
import smbus  # For interfacing over I2C with the altimeter


# Collect raw data from altimeter and compute altitude
def query_altimeter(bus: smbus) -> float:
    # Logic taken from:
    # https://www.instructables.com/id/Raspberry-Pi-MPL3115A2-Precision-Altimeter-Sensor--1/

    # MPL3115A2 address, 0x60(96) - Select control register, 0x26(38)
    # 0xB9(185)	Active mode, OSR = 128(0x80), Altimeter mode
    bus.write_byte_data(0x60, 0x26, 0xB9)

    # MPL3115A2 address, 0x60(96)
    # Read data back from 0x00(00), 6 bytes
    # status, tHeight MSB1, tHeight MSB, tHeight LSB, temp MSB, temp LSB
    data = bus.read_i2c_block_data(0x60, 0x00, 6)
    tHeight = ((data[1] * 65536) + (data[2] * 256) + (data[3] & 0xF0)) / 16
    altitude = round(tHeight / 16.0, 2)
    return altitude


def main():
    print("Testing the value from the altimeter")

# while(True):
    i2c_bus = smbus.SMBus(1)             # Setup I2C bus
    t1 = time.time()
    print('Time before altimeter query: {t}'.format(t=t1))
    altitude = query_altimeter(i2c_bus)  # Query Altimeter first
    t2 = time.time()
    print('Time after altimeter query: {t}'.format(t=t2))
    print('Time difference is: {t}'.format(t=round(t2-t1, 4)))
    print('Altitude is: {a}'.format(a=altitude))


if __name__ == "__main__":
    main()


'''
# This code is designed to work with the MPL3115A2_I2CS I2C Mini Module

# Get I2C bus
bus = smbus.SMBus(1)

# MPL3115A2 address, 0x60(96)
# Select control register, 0x26(38)
# 0xB9(185) Active mode, OSR = 128, Altimeter mode
bus.write_byte_data(0x60, 0x26, 0xB9)

# MPL3115A2 address, 0x60(96)
# Select data configuration register, 0x13(19)
# 0x07(07) Data ready event enabled for altitude, pressure, temperature
# bus.write_byte_data(0x60, 0x13, 0x07)

# MPL3115A2 address, 0x60(96)
# Select control register, 0x26(38)
# 0xB9(185) Active mode, OSR = 128, Altimeter mode
# bus.write_byte_data(0x60, 0x26, 0xB9)

time.sleep(1)

# MPL3115A2 address, 0x60(96)
# Read data back from 0x00(00), 6 bytes
# status, tHeight MSB1, tHeight MSB, tHeight LSB, temp MSB, temp LSB
data = bus.read_i2c_block_data(0x60, 0x00, 6)

# Convert the data to 20-bits
tHeight = ((data[1] * 65536) + (data[2] * 256) + (data[3] & 0xF0)) / 16
temp = ((data[4] * 256) + (data[5] & 0xF0)) / 16
altitude = tHeight / 16.0
cTemp = temp / 16.0
fTemp = cTemp * 1.8 + 32

# MPL3115A2 address, 0x60(96)
# Select control register, 0x26(38)
# 0x39(57) Active mode, OSR = 128, Barometer mode
bus.write_byte_data(0x60, 0x26, 0x39)
time.sleep(1)

# MPL3115A2 address, 0x60(96)
# Read data back from 0x00(00), 4 bytes
# status, pres MSB1, pres MSB, pres LSB
data = bus.read_i2c_block_data(0x60, 0x00, 4)

# Convert the data to 20-bits
pres = ((data[1] * 65536) + (data[2] * 256) + (data[3] & 0xF0)) / 16
pressure = (pres / 4.0) / 1000.0

# Output data to screen
print("Pressure : {p} kPa".format(p=pressure))
print("Altitude : {a} m".format(a=altitude))
print("Temperature in Celsius : {c} C".format(c=cTemp))
print("Temperature in Fahrenheit : {t} F".format(t=fTemp))
'''
