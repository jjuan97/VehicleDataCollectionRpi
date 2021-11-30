# Tests folder
En esta carpeta se encuentran códigos de prueba para probar la correcta funcinalidad de la Raspberry Pi 3b+.

Todos los esquemas usados para las conexiones de cada código puede verse en el siguiente [enlace](https://gpiozero.readthedocs.io/en/stable/recipes.html)

# GPS folder

En esta carpeta se encuentran todos los archivos relacionados con la implementación del modulo GPS.

La documentación usada para lograr el correcto funcionamiento es la siguiente:

 - Video config: https://www.youtube.com/watch?v=N8fH0nc9v9Q
 - Github explain and more detailed: https://github.com/FranzTscharf/Python-NEO-6M-GPS-Raspberry-Pi 
 - Docs more used: https://sparklers-the-makers.github.io/blog/robotics/use-neo-6m-module-with-raspberry-pi/
 - A good alternative: https://maker.pro/raspberry-pi/tutorial/how-to-use-a-gps-receiver-with-raspberry-pi-4
 - Configuring GPS frequency: https://forum.arduino.cc/t/neo-6m-gps-shield-update-faster-than-1hz/452414
 - About NEO6M and NMEA protocol: https://www.engineersgarage.com/articles-raspberry-pi-neo-6m-gps-module-interfacing/
 - UBX and NMEA protocol: https://www.u-blox.com/sites/default/files/products/documents/u-blox8-M8_ReceiverDescrProtSpec_UBX-13003221.pdf

# IMU: mpu6050
 - Python library: https://github.com/adafruit/Adafruit_CircuitPython_MPU6050
 - Tutorial: https://learn.adafruit.com/mpu6050-6-dof-accelerometer-and-gyro/python-and-circuitpython
 - How IMU works: https://lastminuteengineers.com/mpu6050-accel-gyro-arduino-tutorial/

# Flask WebServer

- Guide to config flask: https://towardsdatascience.com/python-webserver-with-flask-and-raspberry-pi-398423cc6f5d
- 

# APT packages installed

- sqlite3
- rpi.gpio-common

# PIP Packages installed
Package                          Version
-------------------------------- -----------
Adafruit-Blinka                  6.15.0
adafruit-circuitpython-busdevice 5.1.1
adafruit-circuitpython-mpu6050   1.1.9
adafruit-circuitpython-register  1.9.6
adafruit-io                      2.6.0
Adafruit-PlatformDetect          3.17.2
Adafruit-PureIO                  1.1.9
APScheduler                      3.8.1
backports.zoneinfo               0.2.1
certifi                          2021.10.8
charset-normalizer               2.0.8
click                            8.0.3
Flask                            2.0.2
idna                             3.3
importlib-metadata               4.8.2
itsdangerous                     2.0.1
Jinja2                           3.0.3
MarkupSafe                       2.0.1
paho-mqtt                        1.6.1
pip                              18.1
pkg-resources                    0.0.0
pyftdi                           0.53.3
pynmea2                          1.18.0
pyserial                         3.5
pytz                             2021.3
pytz-deprecation-shim            0.1.0.post0
pyusb                            1.2.1
requests                         2.26.0
rpi-ws281x                       4.3.1
RPi.GPIO                         0.7.0
setuptools                       40.8.0
six                              1.16.0
sysv-ipc                         1.1.0
typing-extensions                4.0.0
tzdata                           2021.5
tzlocal                          4.1
urllib3                          1.26.7
Werkzeug                         2.0.2
zipp                             3.6.0
