#!/bin/sh
#
# https://askubuntu.com/questions/271387/how-to-restart-wifi-connection
#
# Alternatives:
#	1. systemctl restart NetworkManager
#	   systemctl restart network-manager
#	2. ifconfig wlan0 down
#          ifconfig wlan0 up
#	3. nmcli networking off
#          nmcli networking on
#	4. iwconfig wlan0 txpower off
#          iwconfig wlan0 txpower auto
#       5. rfkill block wifi
#          rfkill unblock wifi
#	6. systemctl --force reboot
#	7. nmcli nm wifi off
#	   nmcli nm wifi on
# 
while [ 1 ] 
do
    ping -c 1 192.168.2.16 2>1 > /dev/null < /dev/null
    if  [ $? -ne 0 ]; then
        echo `date` ": wlan down."
	systemctl status network-manager --full --no-pager
	iwconfig wlan0
        systemctl restart network-manager
        sleep 15
    else
        echo `date` ": wlan up."
    fi
    sleep 300
done

