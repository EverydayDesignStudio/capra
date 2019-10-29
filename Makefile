define INIT_MESSAGE
For which device would you like to install dependencies?

Run one of the following options:
[sudo make collector] 		installs dependencies, sets time, and creates db
[make collector_db]		creates db
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

collector_db:
	./setup/create_db_camera.py
