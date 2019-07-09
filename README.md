# Capra 🎥 ⛰️

*A system for hikers to document and revisit their past hikes.*

---

## Remote Connection
There is a RealVNC Capra group for connecting to both the cameras and projectors remotely. Login details can be found in the Dropbox.

## Collector (Camera unit)

### Services
The timelapse program is started on power up by the service: `/lib/systemd/system/capra-startup.service`

The (on/off) button is controlled by the service: `/lib/systemd/system/capra-listen-for-shutdown.service`

### LED Meanings
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
