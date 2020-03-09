define INIT_MESSAGE
For which device would you like to install dependencies?
Run one of the following options:

----------------------------Camera----------------------------
[make camera_setup1]		installs dependencies and adds line to /boot/config.txt for RTC
[make camera_setup2] 		sets RTC, creates db, and setups services

[make camera_install]		installs dependencies from pip3 and apt-get
[make camera_clock1_use_rtc]	only run once; adds line to /boot/config.txt for RTC
[make camera_clock2_set_rtc]	sets RTC to correct time from NTP
[make camera_db]		creates a new database along file storage
[make camera_services]		loads services to be run on startup

----------------------------Projector----------------------------
[make projector]		installs dependencies and creates db
[make projector_db]		creates a new database along file storage

endef

export INIT_MESSAGE

init:
	@echo "$$INIT_MESSAGE"

# -------------- Projector --------------
define PROJECTOR_INSTALL
sudo pip3 install -r setup/requirements_explorer.txt
sudo ./setup/install_apps_explorer.sh
endef

projector:
	$(call PROJECTOR_INSTALL)
	./setup/create_db_projector.py

projector_db:
	./setup/create_db_projector.py

# -------------- Camera --------------
define CAMERA_INSTALL
sudo pip3 install -r setup/requirements_collector.txt
sudo ./setup/install_apps_collector.sh
endef

define CAMERA_USE_RTC
sudo ./setup/use_rtc.py
endef

define CAMERA_RTC_DB_SERVICES
./setup/set_rtc.py
./setup/create_db_camera.py
./services/init-camera-services
endef

camera_setup1:
	$(call CAMERA_INSTALL)
	$(call CAMERA_USE_RTC)

camera_setup2:
	$(call CAMERA_RTC_DB_SERVICES)

camera_install:
	$(call CAMERA_INSTALL)

camera_clock1_use_rtc:
	$(call CAMERA_USE_RTC)

camera_clock2_set_rtc:
	./setup/set_rtc.py

camera_db:
	./setup/create_db_camera.py

camera_services:
	./services/init-camera-services
