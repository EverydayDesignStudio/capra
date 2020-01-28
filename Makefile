define INIT_MESSAGE
For which device would you like to install dependencies?

Run one of the following options:
[sudo make collector] 		installs dependencies, sets time, creates db, and setups services
[sudo make collector_install]	installs dependencies from pip3 and apt-get
[make collector_setrtc]		sets time for clock on multiplexer
[sudo make collector_settime]	sets system time to read from RTC
[make collector_db]		creates db
[make collector_services]	loads services to be run on startup

[sudo make explorer]		installs dependencies and creates db
[make explorer_db]		creates db

endef

export INIT_MESSAGE

init:
	@echo "$$INIT_MESSAGE"

explorer:
	pip3 install -r setup/requirements_explorer.txt
	./setup/install_apps_explorer.sh
	./setup/create_db_projector.py

explorer_db:
	./setup/create_db_projector.py

collector:
	pip3 install -r setup/requirements_collector.txt
	./setup/install_apps_collector.sh
	./setup/create_db_camera.py
	./setup/set_ds3231_rtc.py
	./setup/set_system_clock_to_RTC.py
	./services/init-camera-services

collector_install:
	pip3 install -r setup/requirements_collector.txt
	./setup/install_apps_collector.sh

collector_setrtc:
	./setup/set_ds3231_rtc.py

collector_settime:
	./setup/set_system_clock_to_rtc.py

collector_db:
	./setup/create_db_camera.py

collector_services:
	./services/init-camera-services
