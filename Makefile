define INIT_MESSAGE
Run one of the following options:

----------------------------Camera----------------------------
[make camera_setup1]		install dependencies, add RTC and UART to /boot/config.txt, remove fake-hwclock
[make camera_setup2] 		set RTC, create db, and set up services

Individual Make commands, if manually needed
[make camera_install]		install dependencies from pip3 and apt-get
[make camera_clock1_use_rtc]	*only run once* : add RTC to /boot/config.txt, remove fake-hwclock
[make camera_clock2_set_rtc]	set RTC to correct time from NTP
[make camera_startup_pin]	*only run once* : enable UART in /boot/config.txt
[make camera_db]		create a new database along with file storage
[make camera_services]		load services to be run on startup


----------------------------Projector----------------------------
[make projector]		install dependencies, setup services, create db

[make projector_startup_pin]	*only run once* : enable UART in /boot/config.txt
[make projector_services]	load services to be run on startup
[make projector_db]		create a new database along with file storage


----------------------------Tests----------------------------
[make test_projector_software]	runs software tess for the slideshow application

endef

export INIT_MESSAGE

init:
	@echo "$$INIT_MESSAGE"

# -------------- Projector --------------
define PROJECTOR_INSTALL
sudo pip3 install -r setup/requirements_projector.txt
sudo ./setup/install_apps_projector.sh
endef

projector:
	$(call PROJECTOR_INSTALL)
	./setup/create_db_projector.py
	sudo ./setup/enable_startup_pin.py
	./services/init-projector-services

projector_install:
	$(call PROJECTOR_INSTALL)

projector_db:
	./setup/create_db_projector.py

projector_services:
	./services/init-projector-services

projector_startup_pin:
	sudo ./setup/enable_startup_pin.py


# -------------- Camera --------------
define CAMERA_INSTALL
sudo pip3 install -r setup/requirements_camera.txt
sudo ./setup/install_apps_camera.sh
endef

camera_setup1:
	$(call CAMERA_INSTALL)
	sudo ./setup/use_rtc.py
	./setup/set_rtc.py

camera_setup2:
	./setup/create_db_camera.py
	./services/init-camera-services

camera_install:
	$(call CAMERA_INSTALL)

camera_clock1_use_rtc:
	sudo ./setup/use_rtc.py

camera_clock2_set_rtc:
	./setup/set_rtc.py

camera_startup_pin:
	sudo ./setup/enable_startup_pin.py

camera_db:
	./setup/create_db_camera.py

camera_services:
	./services/init-camera-services


# -------------- Tests --------------
test_projector_software:
	./tests/run_projector_software_tests
