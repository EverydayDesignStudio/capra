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
Electronically, the Capra Collector consists of the following components _(items with an asterisk are further elaborated on)_:
- [Raspberry Pi Zero](https://www.adafruit.com/product/3400)
- [Adafruit Powerboost 1000](https://www.adafruit.com/product/2465)
- [Custom PCB: Cam Multiplexer](#Cam Multiplexer) *
- Custom PCB: Buttonboard *
- 2 x 21700 LiPo Batteries *
- 3 x [Raspberry Pi Camera V2's](https://www.adafruit.com/product/3099)

In the image below, a systematic view of the respective components is given. Note that power and GND connections are typically not shown in this image.

![Capra system](https://raw.githubusercontent.com/EverydayDesignStudio/guides/master/images/capra/CapraPCBprinciple.jpg)

#### Cam Multiplexer
The Cam Muliplexer is a 30x70mm board directly placed on top of the RPi. While the RPi is typically only capable of connecting to a single camera the _'Cam Multiplexer V4'_ enables the RPi to switch between cameras and take pictures. The CamMultiplexer also contains a MPL3115A2 Altimeter that allows the RPi to sense the altitude of the Collector. Lastly, there is a DS3231 Real Time Clock on the board that allows the RPi to keep its internal clock synchronised. The DS3231 which will continue to run even when the RPi is off (or even runs out of battery) because it is connected to a small CR1220 Coincell battery. This battery will slowly drain, but will keep the Collectors' timekeeping accurate for several years!

![Capra Cam Multiplexer](https://raw.githubusercontent.com/EverydayDesignStudio/guides/master/images/capra/Capra-Manual-PH.png)

The flat cables (called 'FFC' - Flat Flexible Cable) contain all signals that travel between the cameras and the RPi. These signals can be categorised in two protocols:

| Protocol   | Function   | Connects | Through |
| ---------- | ---------- | -------- | ------- |
| [I2C](https://en.wikipedia.org/wiki/I%C2%B2C)        | RPI issue commands to the camera (e.g. set resolution, take picture) | VideoCore (GPU) of RPi <-> Camera (Bidirectional) | Through Analog Multiplexer 74HC4051 |
| [MIPI](https://mipi.org/specifications/d-phy)       | Contains all the data that comprise the image taken by the camera. | Camera -> VideoCore (GPU) of RPi (Unidirectional) | Through (one or both) FSA642UMX |

The table above echoes the systematic drawing in that it shows the signals between the RPi and the cameras being split up and switched via two different chips; this is due to the vastly different electronic requirements of those signals.

Note that the I2C meant in the context of the cameras is NOT easily directly programmable. The I2C bus that runs between the cameras and the RPi is called I2C-0. I2C-0 is controlled by the 'GPU' of the RPi (also referred to as the VideoCore). The 'regular' I2C bus (BCM 2 & BCM3) is an entirely separate I2C bus and is controlled by the ARM processor on the RPi. The latter bus talks to the Altimeter and the RTC and is called I2C-1.

##### A tiny bit about I2C
I²C (or I2C, because that is easier to type) is a data protocol that allows multiple devices to be connected to the same pins of a microcontroller. In Capra's case, the Altimeter and RTC are both connected to BCM2 (SCL, _short for 'Slave CLock'_) and BCM3 (SDA, _short for 'Slave DAta'_); yet their functionality does not interfere with each other. This works through something called **addressing**. Each I2C device has a specific address; whenever the microcontoller wants to 'talk'to any of the devices, it first sends out an 'adress': string of 1's and 0's over its data line (SDA). This address will correspond with one of the devices; then that device starts listening to whatever commands the microcontroller sends next. Compare this with a phone call; you first dial a number (analogous to an address) and then start talking (analogous to 'whatever commands the microcontroller sends next').

Using I2C is different for per device. Typically, you can find documentation of how to address the device and what kinds of commands you can send to it in its datasheet. For the altimeter on Capra for example, [its datasheet](https://media.digikey.com/pdf/Data%20Sheets/NXP%20PDFs/MPL3115A2.pdf) will tell you how to address it. However, the process of writing this kind of code is very tedious. If you can, find an existing breakout board from Sparkfun or Adafruit with a component that fulfills your intended functionality. You can then integrate that circuit into your own (Sparkfun and Adafruit open-source their designs!!) and use their code to interface with the chip. Do attribute the author of the code you're importing in the header of your code and link to the respective originating github repo!!

#### Buttonboard
This PCB is placed towards the lower end of the Capra enclosure; and is fixed against the back piece. A 7-cable ribbon connects the buttonboard with the Cam Multiplexer. The following components are on the buttonboard:
- On Button
- Off Button
- Pause button
- 2-colour indicator LED

![Button Board](https://raw.githubusercontent.com/EverydayDesignStudio/guides/master/images/capra/Capra_Buttonboard.png)

The Buttonboard has a row of connections labelled `'To_Raspberry'`. This is where the 7-cable ribbon connects to the button board. These connections have individual names and should be routed as follows:

| ButtonBoard | ↔ | Cam Multiplexer |
| ----------- | - | --------------- |
| GND         | ↔ | GND (⏚ symbol) |
| LED_R       | ↔ | LED             |
| LED_G       | ↔ | LED2            |
| 3V3         | ↔ | 3V3             |
| OFF         | ↔ | OFF             |
| PAUSE       | ↔ | PLAY            |
| SCL         | ↔ | SCL             |

These connections can be found here on the Cam Multiplexer board, (Note that the 'OFF' connection is at an unexpected spot):
![Cam Multiplexer, connections to Button board](https://raw.githubusercontent.com/EverydayDesignStudio/guides/master/images/capra/Capra-Manual-BB.png)

#### Batteries
Capra uses two 21700 LiPo batteries. More specifically, the batteries used are the Samsung 40T batteries. This specific battery type was chosen because two such batteries placed in parallel fit the shape of Capra perfectly and because the 40T model packs an impressive 4000 mAh capacity per unit. In the Collector, I've placed two such batteries in parallel to create a battery pack of 8000mAh @ 3.7V. The name _21700_ refers to the diameter (21mm) and the height (70mm) of the battery - this is a common naming convention with cylindrical LiPo batteries.
> Fun Fact: 21700 batteries were initially [developed for electric vehicles](https://electrek.co/2017/01/09/samsung-2170-battery-cell-tesla-panasonic/). However, their main use nowadays is to power e-cigarettes. Hence, you will find them readily for sale at vape shops.

At an average draw of approximately 800mA @ 5V by the Capra system, the two batteries are able to power the system for an approximate 7,5 hours.

![Samsung 40T](https://raw.githubusercontent.com/EverydayDesignStudio/guides/master/images/capra/40T.jpg)

LiPo batteries do require a specific circuit to regulate their charging. For Capra, I chose the Adafruit PowerBoost 1000. This module 'boosts' the nominal 3.7V of the LiPo battery to 5V @ 800mA required by the RPI and has a load-sharing circuit. The load sharing circuit is what makes it possible to connect the Collector to a 5V USB power source (e.g. 5V powerbank, 5V wall outlet, etc.). Connecting such a power source will have the Collector run on that power AND charge the batteries while connected.

**!! NEVER ATTEMPT TO CHARGE THESE BATTERIES WITHOUT AN APPROPRIATE CIRCUIT OR MODULE !!**

**!! NEVER EVER SOLDER WIRES DIRECTLY TO THE BATTERIES !!**

On the Collectors' back piece, there are recessed areas where the battery clips go. There are two types of battery clips used in the assembly. The one meant for the '+' terminal of the battery has a little circular marking on it (Product code [36-228-ND](https://www.digikey.ca/product-detail/en/keystone-electronics/228/36-228-ND/528660); the one meant for the '-' terminal of the battery has a texturised surface and is springy (Product code [Keystone 36-209](https://www.digikey.ca/product-detail/en/keystone-electronics/209/36-209-ND/151583). These parts are shown below:![Battery Clips](https://raw.githubusercontent.com/EverydayDesignStudio/guides/master/images/capra/BatteryClips.png)

The '+' and '-' terminals should be connected in parallel to the JST-PH2 connector on the PowerBoost module. The output of the PowerBoost module should be connected to the following positions of the Cam Multiplexer:
![Power connection on Cam Multiplexer](https://raw.githubusercontent.com/EverydayDesignStudio/guides/master/images/capra/batteries.jpg)

| PowerBoost | ↔ | Cam Multiplexer |
| ---------- | - | --------------- |
| +          | ↔ | 5V              |
| -          | ↔ | GND (⏚ symbol) |

Note the sides of the PH2 connector: the connection closest to the USB port on the Powerboost should be GND; the other should be +3.7V (power from battery pack).

##### Safety and Batteries
21700 batteries have poorly indicated '+' and '-' terminals. This is **_extremely_** important to remain aware of while inserting them into the battery holders. If inserted the wrong way around, the batteries will immediately short circuit, resulting in **melting wires** at best and **exploding batteries** at worst. This will also irreparably damage the PowerBoost module. To mitigate such mistakes, mark the '-' side of new batteries with tape or permanent marker. The '+' terminal is recognisable by a round indentation. The '-' terminal is entirely flat.

![Battery Marking](https://raw.githubusercontent.com/EverydayDesignStudio/guides/master/images/capra/BatteryMarking.JPG)

The + terminal should be pointed upwards. The '-' terminal should be pointed down (towards the buttonboard). There is also a recessed marking on the back piece that shows the orientation of the batteries:

![Battery Orientation](https://raw.githubusercontent.com/EverydayDesignStudio/guides/master/images/capra/BatteryOrientation.JPG)


#### LED Meanings
| LED                | Location          | Meaning                 |
| ------------------ | ----------------- | ----------------------- |
| 💚 solid/blinking  | Raspberry Pi      | RPi is on               |
| 💚 blinking        | Button board      | collector.py is PAUSED  |
| 🔴 blinking        | Button board      | program is running      |
| 🔵 solid           | Powerbooster      | Powerbooster has power  |
| 💚 solid           | Powerbooster      | Batteries fully charged |
| 🔴 solid           | Powerbooster      | Batteries low           |
| 🧡 solid           | Powerbooster      | Batteries charging      |

## Explorer (Projector unit)
The Explorers functionality is twofold:
- Providing storage for the photos from the Collector  
- Playing the photos back via its internal projector.

### File transfer
File transfer from the Collector to the Explorer is initiated when the Collector is physically placed over the Explorers controls. This is registered by the Explorer by a magnetometer that senses the magnetic field of a small magnet in the Collectors' housing.
At this point, the Explorer starts two parallel processes: the file transfer is initiated and a __transfer animation__ is started.

The transfer animation shows
