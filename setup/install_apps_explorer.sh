#!/bin/sh

apt-get update

apt-get install vim --assume-yes
apt-get install python3-pil python3-pil.imagetk --assume-yes
apt-get install exfat-fuse exfat-utils --assume-yes
apt-get install i2c-tools
