# GARAGE_SECURITY
Monitor PIR sensors to detect motion and magnetic reed switches to detect open doors.

![Deployment on NanoPI NEO Duo2](https://github.com/newfoundlandplucky/GARAGE_SECURITY/blob/master/documentation/Delpoyment.jpg?raw=true)

**Tested using the following environment**
* SBC: NanoPI NEO Core2 "stretch/sid"
* Linux GarageSensors 4.14.111 #27 SMP Wed Apr 24 20:18:02 CST 2019 armv7l armv7l armv7l GNU/Linux

**Vendors and Forums**
* https://linux-sunxi.org/Main_Page
* Friendly Elec: https://www.friendlyarm.com/
* SunXi H3 > NanoPi-Duo2 https://drive.google.com/drive/folders/1fwBNaVULDohrIG_dpLuIvMZ6rC0tGSqD

![NanoPi NEO Core2 Pinout](https://github.com/newfoundlandplucky/GARAGE_SECURITY/blob/master/documentation/NanoPi_Duo2.jpg?raw=true)

**Sample Output**

```
elvis@GarageSensors:~$ sudo make status
● monitor.service - Security sensor monitoring service.
   Loaded: loaded (/lib/systemd/system/monitor.service; enabled; vendor preset: enabled)
   Active: active (running) since Thu 2016-02-11 12:17:52 EST; 38min ago
 Main PID: 1896 (python2)
   CGroup: /system.slice/monitor.service
           └─1896 /usr/bin/python2 /home/pi/monitor.py

Feb 11 12:17:52 GarageSensors systemd[1]: Started Security sensor monitoring service..
Feb 11 12:17:54 GarageSensors python2[1896]: CRITICAL:Security Monitor:Side Door is open
Feb 11 12:17:54 GarageSensors python2[1896]: CRITICAL:Security Monitor:Car Bay is active
```

![NanoPi NEO Core2 Pinout](https://github.com/newfoundlandplucky/GARAGE_SECURITY/blob/master/documentation/WebInterface.jpg?raw=true)

**Benchtop Evaluation**

![Benchtop Evaluation](https://github.com/newfoundlandplucky/GARAGE_SECURITY/blob/master/documentation/BenchTest.jpg?raw=true)
