# Capra 🎥 ⛰️

*A system for hikers to document and revisit their past hikes.*

---

## Remote Connection
There is a RealVNC Capra group for connecting to both the cameras and projectors remotely. Login details can be found in the Dropbox.

## Collector (Camera unit)
### Services
The timelapse program is started on power up by the service: `/lib/systemd/system/capra-startup.service`

The (on/off) button is controlled by the service: `/lib/systemd/system/capra-listen-for-shutdown.service`

### Hardware
Electronically, the Capra Collector consists of
- Raspberry Pi Zero
- [Adafruit Powerboost 1000](https://www.adafruit.com/product/2465)
- 2 x 21700 LiPo Batteries
- 2 x custom PCBs
- 3 x Raspberry Pi Camera V2's.

In the image below, a systematic view of the respective connections is given.

![Capra PCB ](https://raw.githubusercontent.com/EverydayDesignStudio/guides/master/images/capra/CapraPCBprinciple.jpg)

#### Cam Multiplexer
The RPi is typically only capable of connecting to a single camera; the first custom PCB, named the 'Cam Multiplexer V4' enables the RPi to switch between cameras and take pictures. The CamMultiplexer also contains a MPL3115A2 Altimeter that allows the RPi to sense the altitude of the Collector. Lastly, there is a DS3231 Real Time Clock on the board that allows the RPi to keep its internal clock synchronised. The DS3231 which will continue to run even when the RPi is off (or even runs out of battery) because it is connected to a small CR1220 Coincell battery. This battery will slowly drain, but will keep the collector running for several years!

The flat cables (called 'FFC' - Flat Flexible Cable) contain all signals that travel between the cameras and the RPi. These signals can be categorised in two protocols:

| Protocol   | Function   | Through |
| ---------- | ---------- | ------- |
| [I2C](https://en.wikipedia.org/wiki/I%C2%B2C)        | RPI issue commands to the camera. | VideoCore (GPU) of RPi and Camera through Analog Multiplexer 74HC4051 |
| [MIPI](https://mipi.org/specifications/d-phy)       | Contains all the data that comprise the image taken by the camera. | VideoCore (GPU) of RPi and Camera through (one or both) FSA642UMX |

The table above echoes the systematic drawing in that it shows the signals between the RPi and the cameras being split up and switched via two different chips; this is due to the vastly different electronic requirements of those signals.

Note that the I2C meant in the context of the cameras is NOT easily directly programmable. The I2C bus that runs between the cameras and the RPi is called I2C-0. The 'regular' I2C bus (BCM 2 & BCM3) is an entirely separate I2C bus!! The latter talks to the Altimter and the RTC and is called I2C-1.

#### LED Meanings
| LED   | Location   | Meaning |
| ----- |:----------:|--------:|
| 💚 solid/blinking  | Raspberry pi Zero | Raspberry pi is on  |
| 💚    | Capra PCB | Unassigned  |
| 🧡    | Capra PCB | Unassigned  |
| 🔴 blinking   | Capra PCB (White/Silver Version) | collector.py is PAUSED  |
| ⚪ blinking   | Capra PCB (Silver/ Version) | collector.py is PAUSED  |
| 🔵 solid | Adafruit Powerbooster | Adafruit Powerbooster has power |
| 💚 solid   | Adafruit Powerbooster | Batteries fully charged  |
| 🔴 solid   | Adafruit Powerbooster | Batteries low  |
| 🧡 solid   | Adafruit Powerbooster | Batteries charging  |


## Explorer (Projector unit)
The Explorers functionality is twofold:
- Providing storage for the photos from the Collector  
- Playing the photos back via its internal projector.

### File transfer
File transfer from the Collector to the Explorer is initiated when the Collector is physically placed over the Explorers controls. This is registered by the Explorer by a magnetometer that senses the magnetic field of a small magnet in the Collectors' housing.
At this point, the Explorer starts two parallel processes: the file transfer is initiated and a __transfer animation__ is started.

The transfer animation shows
