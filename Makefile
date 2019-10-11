define INIT_MESSAGE
For which device would you like to install dependencies?

Run [sudo make collector] or [sudo make explorer]

endef
export INIT_MESSAGE

init:
	@echo "$$INIT_MESSAGE"

explorer:
	pip3 install -r setup/requirements_explorer.txt
	./setup/install_apps_explorer.sh

collector:
	pip3 install -r setup/requirements_collector.txt
	./setup/install_apps_collector.sh
