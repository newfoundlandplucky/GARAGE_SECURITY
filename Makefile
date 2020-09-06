install:
	@echo "[Unit]"> /lib/systemd/system/monitor.service
	@echo "Description=Security sensor monitoring service." >> /lib/systemd/system/monitor.service
	@echo "BindsTo=sys-devices-platform-soc-1c10000.mmc-mmc_host-mmc2-mmc2:0001-mmc2:0001:1-net-wlan0.device" >> /lib/systemd/system/monitor.service
	@echo "After=sys-devices-platform-soc-1c10000.mmc-mmc_host-mmc2-mmc2:0001-mmc2:0001:1-net-wlan0.device" >> /lib/systemd/system/monitor.service
	@echo "" >> /lib/systemd/system/monitor.service
	@echo "[Service]" >> /lib/systemd/system/monitor.service
	@echo "Type=simple" >> /lib/systemd/system/monitor.service
	@echo "ExecStart=/usr/bin/python2 /home/pi/monitor.py" >> /lib/systemd/system/monitor.service
	@echo "Restart=always" >> /lib/systemd/system/monitor.service
	@echo "RestartSec=0"  >> /lib/systemd/system/monitor.service
	@echo "" >> /lib/systemd/system/monitor.service
	@echo "[Install]" >> /lib/systemd/system/monitor.service
	@echo "WantedBy=multi-user.target" >> /lib/systemd/system/monitor.service
	systemctl enable monitor.service
	systemctl start monitor.service
	systemctl daemon-reload
	@echo "#!/bin/bash" > /etc/cron.hourly/monitor.crontab
	@echo "systemctl --force reboot" >> /etc/cron.hourly/monitor.crontab
	chmod 755 /etc/cron.hourly/monitor.crontab
	crontab -l > /tmp/crontab
	@echo "@reboot nmcli r wifi on" >> /tmp/crontab"
	crontab < /tmp/crontab"
	rm /tmp/crontab"
	

clean:
	@systemctl stop monitor.service; true
	@systemctl disable monitor.service; true
	rm -rf /etc/cron.hourly/monitor.crontab; true
	rm -rf /lib/systemd/system/monitor.service; true
	rm -rf monitor.pickle; true

reset:
	@systemctl stop monitor.service; true
	rm -rf monitor.pickle
	@systemctl start monitor.service; true

status:
	@systemctl status monitor.service; true
