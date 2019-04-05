import os
import time
import sys
import paho.mqtt.client as mqtt
import json
from envirophat import weather

THINGSBOARD_HOST = '192.168.1.202'
MQTT_PORT = 1883
ACCESS_TOKEN = 'ENVIRO_DEMO_TOKEN'

# Data capture and upload interval
INTERVAL = 2

sensor_data = {'temperature': 0, 'pressure': 0}
temperature_offset = 16
next_reading = time.time()

client = mqtt.Client()

#Set access token
client.username_pw_set(ACCESS_TOKEN)

# Connect to ThingsBoard using default MQTT port and 60 second keep alive interval
client.connect(THINGSBOARD_HOST, MQTT_PORT, 60)

print("Connected to: " + THINGSBOARD_HOST + " on port: " + str(MQTT_PORT))

client.loop_start()

try:
	while True:
		temperature = round(weather.temperature(), 2)-temperature_offset
		pressure = round(weather.pressure(unit='hPa'), 2)
		print("Temperature: {:g}\u00b0C, Pressure: {:g}hPa".format(temperature, pressure))
		sensor_data['temperature'] = temperature
		sensor_data['pressure'] = pressure

		#Sending data to ThingsBoard
		client.publish('v1/devices/me/telemetry', json.dumps(sensor_data), 1)

		next_reading += INTERVAL
		sleep_time = next_reading - time.time()
		if sleep_time > 0:
			time.sleep(sleep_time)
except KeyboardInterrupt:
	pass

client.loop_stop()
client.disconnect()
