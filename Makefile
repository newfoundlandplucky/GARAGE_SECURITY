install:
	#
	# Install the sensor monitoring service. This service periodically
	# saves state to the /var/lib/monitor directory.
	#
	cp monitor.py /usr/local/bin/monitor.py
	chmod 755 /usr/local/bin/monitor.py
	chown root:root /usr/local/bin/monitor.py
	if [ ! -d "/var/lib/monitor" ]; \
	then \
		mkdir /var/lib/monitor; \
		chmod 755 /var/lib/monitor; \
		cp favicon.ico /var/lib/monitor; \
		chmod 444 /var/lib/monitor/favicon.ico; \
		cp banner.png /var/lib/monitor; \
		chmod 444 /var/lib/monitor/banner.png; \
	fi

	cp monitor.service /lib/systemd/system/monitor.service
	chmod 644 /lib/systemd/system/monitor.service
	chown root:root /lib/systemd/system/monitor.service
	systemctl daemon-reload
	systemctl enable monitor.service
	systemctl start monitor.service

	#
	# Install the checklan service.
	#
	cp checklan.sh /usr/local/bin/checklan.sh
	chmod 755 /usr/local/bin/checklan.sh
	chown root:root /usr/local/bin/checklan.sh

	cp checklan.service /lib/systemd/system/checklan.service
	chmod 644 /lib/systemd/system/checklan.service
	chown root:root /lib/systemd/system/checklan.service
	systemctl daemon-reload
	systemctl enable checklan.service
	systemctl start checklan.service

	#
	# Make sure wireless is enabled at boot. This is not removed
	# when un-installing. Must be done manually if desired.
	#
	crontab -l > /tmp/crontab
	grep "@reboot nmcli r wifi on" /tmp/crontab; \
	if [ $$? -ne 0 ]; \
	then \
		echo "@reboot nmcli r wifi on" >> /tmp/crontab; \
	fi
	crontab < /tmp/crontab
	rm /tmp/crontab

clean:
	#
	# Remove the checklan service.
	#
	if [ -f "/lib/systemd/system/checklan.service" ]; \
	then \
		systemctl stop checklan.service; \
		systemctl disable checklan.service; \
		rm -f /lib/systemd/system/checklan.service; \
		rm -f /usr/local/bin/checklan.sh; \
		true; \
	fi

	#
	# Remove the sensor monitoring service and it's savestate directory.
	#
	if [ -f "/lib/systemd/system/monitor.service" ]; \
	then \
		systemctl stop monitor.service; \
		systemctl disable monitor.service; \
		rm -f /lib/systemd/system/monitor.service; \
		rm -f /usr/local/bin/monitor.py; \
		true; \
	fi
	if [ -d "/var/lib/monitor" ]; \
	then \
		rm -rf /var/lib/monitor; \
	fi

reset:
	@systemctl stop monitor.service; true
	@rm -f /var/lib/monitor/savestate.pickle; true
	@systemctl start monitor.service; true

start:
	@systemctl start monitor.service; true

stop:
	@systemctl stop monitor.service; true

restart:
	@systemctl restart monitor.service; true

status:
	@systemctl status monitor.service; true
	@systemctl status checklan.service; true

