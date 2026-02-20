PYTHON = python2

.PHONY: install run run-analyzer

install:
	$(PYTHON) -m pip install pcapy impacket reprint matplotlib requests

run:
	@echo "Usage: sudo $(PYTHON) PresenceChecker.py -i <monitor_interface>"
	@echo "Example: sudo $(PYTHON) PresenceChecker.py -i wlan0mon"

run-analyzer:
	@echo "Usage: $(PYTHON) Analyzer.py -d <log_directory> -m <mac_address>"
	@echo "Example: $(PYTHON) Analyzer.py -d ~/PresenceCheckerLOG/ -m 00:11:22:33:44:55"
