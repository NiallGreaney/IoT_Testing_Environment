# IoT_Testing_Environment
18/19 EE443 Final Year Project install instructions

# ThingsBoard
An Raspbian image of the ThingsBoard image has been provided.
Unzip and Flash this to an sd card and boot Pi

usr: pi
pwd: Passw0rd

A static IP has be set for this Pi: 192.168.43.202
Edit /ect/dhcpcd.conf with a text editor of your choice (eg nano, vi, etc)
To revert back to dhcp, comment out these line or edit to configure a new static ip.
Note: all scripts use this IP for referencing ThingsBoard, therefore they will need to be update to point to the new address:

interface eth0

static ip_address=192.168.0.10/24
static routers=192.168.0.1
static domain_name_servers=192.168.0.1

interface wlan0

static ip_address=192.168.0.200/24
static routers=192.168.0.1
static domain_name_servers=192.168.0.1

You can login to the ThingsBoard Web UI @ http://<ip addr>:8080
Email: niallgreaney@gmail.com
Pwd: Passw0rd!

The Express REST API boots as a service on this pi
To check the status: sudo systemctl status spotify_controller.service
To restart the service: sudo systemctl restart spotify_controller.service
JavaScript and HTML for the service located at /home/pi/SpotifyController/app.js /home/pi/SpotifyController/public/index.html
If you want to run the app.js: node app.js

# Sensor Pi
Two scripts used in combination with the Pimoroni EnviroPhat:
getTemperature.py - Reads temp and pressure readings from shield and sends to TB server over MQTT
shakeDetection.py - Reads accelerometer readings and sends a shakeDetected msg to TB server over MQTT

Both scripts require the install of Paho MQTT: pip install paho-mqtt

# Security Camera
Compile NGINX with the RTMP module:
wget http://nginx.org/download/nginx-1.10.0.tar.gz
tar xvf nginx-1.10.0.tar.gz
git clone https://github.com/ut0mt8/nginx-rtmp-module/
cd nginx-1.10.0
./configure --add-module=../nginx-rtmp-module
make
make install

Next copy the nginx.conf file to /usr/local/nginx/conf/
cp nginx.conf /usr/local/nginx/conf/

Start Service using:
systemctl start nginx.service

The security_camera.py scripts has the following requirements:
FFMPEG:
git clone git://source.ffmpeg.org/ffmpeg.git
cd ffmpeg/
sudo ./configure --arch=armel --target-os=linux --enable-gpl --enable-libx264 --enable-nonfree
make
sudo make install
 
OpenCV 4 - https://www.pyimagesearch.com/2018/09/26/install-opencv-4-on-your-raspberry-pi/

imutils: pip install imutils
Paho MQTT: pip install paho-mqtt