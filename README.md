# GARAGE_SECURITY
Monitor PIR sensors to detect motion, magnetic reed switches to detect open doors, and BME280 for environment.

![Deployment on NanoPI NEO Duo2](https://github.com/newfoundlandplucky/GARAGE_SECURITY/blob/master/documentation/Deployment.jpg?raw=true)

**Tested using the following environment**
* SBC: NanoPI NEO Core2 "stretch/sid"
* Linux GarageSensors 4.14.111 #27 SMP Wed Apr 24 20:18:02 CST 2019 armv7l armv7l armv7l GNU/Linux

```
elvis@GarageSensors:~$ sudo pip3 list
chardet (2.3.0)
decorator (4.0.6)
numpy (1.11.0)
pip (8.1.1)
python-apt (1.1.0b1+ubuntu0.16.4.9)
requests (2.9.1)
RPi.bme280 (0.2.3)
RPi.GPIO (0.5.8)
scipy (0.17.0)
setuptools (20.7.0)
six (1.10.0)
smbus2 (0.3.0)
ssh-import-id (5.5)
tornado (6.0.4)
urllib3 (1.13.1)
wheel (0.29.0)
```

**Vendors and Forums**
* "Friendly Elec" https://www.friendlyarm.com/
* "SUNXI" https://linux-sunxi.org/Main_Page
* "NanoPi Duo2 firmware" https://drive.google.com/drive/folders/1fwBNaVULDohrIG_dpLuIvMZ6rC0tGSqD
* "Bosch BME280 digital sensor module interface" https://pypi.org/project/RPi.bme280/
* "Using I2C on NanoPi Duo with Python" http://www.friendlyarm.com/Forum/viewtopic.php?f=59&t=958&p=2883#p2883
* "BMP280 and ESP8266" https://myesp8266.blogspot.com/2016/12/bmp280-and-esp8266.html

![NanoPi NEO Core2 Pinout](https://github.com/newfoundlandplucky/GARAGE_SECURITY/blob/master/documentation/NanoPi_Duo2.jpg?raw=true)

**Browser Interface**

![Web Interface](https://github.com/newfoundlandplucky/GARAGE_SECURITY/blob/master/documentation/WebInterface.jpg?raw=true)
**Benchtop Evaluation**

**Sample Output**

```
elvis@GarageSensors:~/monitor$ sudo make status
● monitor.service - security sensor monitoring service
   Loaded: loaded (/lib/systemd/system/monitor.service; enabled; vendor preset: enabled)
   Active: active (running) since Mon 2020-10-12 22:11:52 EDT; 11h ago
 Main PID: 507 (python3)
   CGroup: /system.slice/monitor.service
           └─507 /usr/bin/python3 /usr/local/bin/monitor.py

Oct 13 08:23:43 GarageSensors python3[507]: INFO:Security Monitor:Equipment Bay is quiet
Oct 13 08:26:21 GarageSensors python3[507]: INFO:Security Monitor:Driveway Lamp is quiet
Oct 13 08:31:24 GarageSensors python3[507]: CRITICAL:Security Monitor:Side Door is open
Oct 13 08:31:25 GarageSensors python3[507]: CRITICAL:Security Monitor:Equipment Bay is active
Oct 13 08:31:31 GarageSensors python3[507]: INFO:Security Monitor:Side Door is closed
Oct 13 08:31:35 GarageSensors python3[507]: INFO:Security Monitor:Equipment Bay is quiet
Oct 13 08:37:55 GarageSensors python3[507]: CRITICAL:Security Monitor:Side Door is open
Oct 13 08:37:58 GarageSensors python3[507]: CRITICAL:Security Monitor:Equipment Bay is active
Oct 13 08:38:07 GarageSensors python3[507]: INFO:Security Monitor:Side Door is closed
Oct 13 08:38:09 GarageSensors python3[507]: INFO:Security Monitor:Equipment Bay is quiet

● checklan.service - check wlan0 connection to local server
   Loaded: loaded (/lib/systemd/system/checklan.service; enabled; vendor preset: enabled)
   Active: active (running) since Mon 2020-10-12 22:11:51 EDT; 11h ago
 Main PID: 495 (checklan.sh)
   CGroup: /system.slice/checklan.service
           ├─  495 /bin/sh /usr/local/bin/checklan.sh
           └─10927 sleep 600

Oct 13 08:31:54 GarageSensors checklan.sh[495]: Tue Oct 13 08:31:54 EDT 2020 : wlan up.
Oct 13 08:41:54 GarageSensors checklan.sh[495]: Tue Oct 13 08:41:54 EDT 2020 : wlan up.
Oct 13 08:51:54 GarageSensors checklan.sh[495]: Tue Oct 13 08:51:54 EDT 2020 : wlan up.
Oct 13 09:01:54 GarageSensors checklan.sh[495]: Tue Oct 13 09:01:54 EDT 2020 : wlan up.
Oct 13 09:11:54 GarageSensors checklan.sh[495]: Tue Oct 13 09:11:54 EDT 2020 : wlan up.
Oct 13 09:21:54 GarageSensors checklan.sh[495]: Tue Oct 13 09:21:54 EDT 2020 : wlan up.
Oct 13 09:31:54 GarageSensors checklan.sh[495]: Tue Oct 13 09:31:54 EDT 2020 : wlan up.
Oct 13 09:41:54 GarageSensors checklan.sh[495]: Tue Oct 13 09:41:54 EDT 2020 : wlan up.
Oct 13 09:51:54 GarageSensors checklan.sh[495]: Tue Oct 13 09:51:54 EDT 2020 : wlan up.
Oct 13 10:01:54 GarageSensors checklan.sh[495]: Tue Oct 13 10:01:54 EDT 2020 : wlan up.
```

**Benchtop Evaluation**

![Benchtop Evaluation](https://github.com/newfoundlandplucky/GARAGE_SECURITY/blob/master/documentation/BenchTest.JPG?raw=true)
