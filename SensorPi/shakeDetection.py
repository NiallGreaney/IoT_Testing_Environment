from envirophat import motion
import time
import time
import sys
import paho.mqtt.client as mqtt
import json

# ThingsBoard Host IP, MQTT Port Number and the TB Access Token
THINGSBOARD_HOST = '192.168.1.202'
MQTT_PORT = 1883
ACCESS_TOKEN = 'SHAKE_TOKEN_4587'

# Set the inital coordinates
prevX, prevY, prevZ = motion.accelerometer()
time.sleep(1)

# Amount any coordinate has to change for a valid shake
THRESHOLD = 0.6

# Time between two shakes in seconds
SHAKE_INTERVAL = 1

# Create MQTT Client Object
client = mqtt.Client()

#Set access token
client.username_pw_set(ACCESS_TOKEN)

#Set access token
client.username_pw_set(ACCESS_TOKEN)

# Connect to ThingsBoard using default MQTT port and 60 second keep alive interval
client.connect(THINGSBOARD_HOST, MQTT_PORT, 60)
print("Connected to: " + THINGSBOARD_HOST + " on port: " + str(MQTT_PORT))

# Start the loop
client.loop_start()

# JSON obj to send if shake is detected
shake = {'shakeDetected' : 'true'}

# Main Loop
try:
    while True:
        currX, currY, currZ = motion.accelerometer()

        # Current reading - stationary reading
        diffX = currX - prevX
        diffY = currY - prevY
        diffZ = currZ - prevZ

        # Get the abs
        diffX = abs(diffX)
        diffY = abs(diffY)
        diffZ = abs(diffZ)

        # If the diff goes above the threshold, a shake has beed detected
        if diffX > THRESHOLD or diffY > THRESHOLD or diffZ > THRESHOLD:
            print("Shake detected")
            client.publish('v1/devices/me/telemetry', json.dumps(shake), 1)
            time.sleep(SHAKE_INTERVAL)

	# 20ms delay to keep things stable
	time.sleep(0.2)

except KeyboardInterrupt:
    pass

# Clean up the client
client.disconnect()
