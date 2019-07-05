# Capra 🎥 ⛰️

*A system for hikers to document and revisit their past hikes.*

---

## Remote Connection
There is a RealVNC Capra group for connecting to both the cameras and projectors remotely. Login details can be found in the Dropbox.

## Collector

### Services
The timelapse program is started on power up by the service: `/lib/systemd/system/capra-startup.service`

The (on/off) button is controlled by the service: `/lib/systemd/system/capra-listen-for-shutdown.service`

### LED Meanings
| LED   | Location   | Meaning |
| ----- |:----------:|--------:|
| 💚 solid/blinking  | Raspberry pi Zero | Raspberry pi is on  |
| 💚    | Capra PCB | Unassigned  |
| 🧡    | Capra PCB | Unassigned  |
| 🔴 blinking   | Capra PCB | collector.py is PAUSED  |
| 🔵 solid | Adafruit Powerbooster | Adafruit Powerbooster has power |
| 💚 solid   | Adafruit Powerbooster | Batteries fully charged  |
| 🔴 solid   | Adafruit Powerbooster | Batteries low  |
| 🧡 solid   | Adafruit Powerbooster | Batteries charging  |

## Explorer


