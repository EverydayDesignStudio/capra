define INIT_MESSAGE
For which device would you like to install dependencies?

Run [make collector] or [make explorer]

endef
export INIT_MESSAGE

init:
	@echo "$$INIT_MESSAGE"

explorer:
	pip3 install -r requirements_explorer.txt
	./install_apps_explorer.sh

collector:
	pip3 install -r requirements_collector.txt
	./install_apps_collector.sh
