# Services
> Services are programs which are called upon startup of a Raspberry Pi. Services call other programs.

## Setup 
1. These services should be placed in `/lib/systemd/system/name-of-service.service` on the respective Pi.

2. The permission on the unit file needs to be set to `644`
`sudo chmod 644 /lib/systemd/system/name-of-service.service`

3. Now the unit file has been defined we can tell systemd to start it during the boot sequence: <br>
`sudo systemctl daemon-reload`
`sudo systemctl enable sample.service`

4. Reboot the Pi and your custom service should run:
`sudo reboot now`


## Collector (camera)
`capra-startup.service` - calls the timelapse program to be started on power up
`capra-listen-for-shutdown.service` - manages the `off` button

## Explorer (projector)
