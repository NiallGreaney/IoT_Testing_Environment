# import the necessary packages
from imutils.video import VideoStream
import datetime
import imutils
import time
import cv2
import numpy as np
import subprocess as sp
import paho.mqtt.client as mqtt
import json

# FFMPEG sub process command
command = ['ffmpeg',
   '-y',
    '-f', 'rawvideo',
    '-vcodec','rawvideo',
    '-pix_fmt', 'bgr24',
    '-s', '640x480',
    '-i', '-',
    '-c:v', 'libx264',
    '-pix_fmt', 'yuv420p',
    '-profile:v', 'baseline',
    '-preset', 'ultrafast',
    '-tune', 'zerolatency',
    '-b:v', '500k',
    '-minrate', '500k',
    '-maxrate', '500k',
    '-bufsize', '1000k',
    '-g', '60',
    '-f', 'flv',
    'rtmp://192.168.43.204:1935/dash/picamstream_low']

command2 = ['ffmpeg',
    '-y',
    '-f', 'rawvideo',
    '-vcodec','rawvideo',
    '-pix_fmt', 'bgr24',
    '-s', '1280x720',
    '-i', '-',
    '-c:v', 'libx264',
    '-pix_fmt', 'yuv420p',
    '-profile:v', 'baseline',
    '-preset', 'ultrafast',
    '-tune', 'zerolatency',
    '-b:v', '1500k',
    '-minrate', '1500k',
    '-maxrate', '1500k',
    '-bufsize', '3000k',
    '-g', '60',
    '-f', 'flv',
    'rtmp://192.168.43.204:1935/dash/picamstream_med']

command3 = ['ffmpeg',
    '-y',
    '-f', 'rawvideo',
    '-vcodec','rawvideo',
    '-pix_fmt', 'bgr24',
    '-s', '1920x1080',
    '-i', '-',
    '-c:v', 'libx264',
    '-pix_fmt', 'yuv420p',
    '-profile:v', 'baseline',
    '-preset', 'ultrafast',
    '-tune', 'zerolatency',
    '-b:v', '5000k',
    '-minrate', '5000k',
    '-maxrate', '5000k',
    '-bufsize', '10000k',
    '-g', '60',
    '-f', 'flv',
    'rtmp://192.168.43.204:1935/dash/picamstream_high']

# initalise the subprocesses
proc1 = sp.Popen(command, stdin=sp.PIPE,shell=False)
proc2 = sp.Popen(command2, stdin=sp.PIPE,shell=False)
proc3 = sp.Popen(command3, stdin=sp.PIPE,shell=False)

# Minimum motion detection area in pixels
min_area = 8000

# Get the video stream from the pi camera
vs = VideoStream(src=0).start()
time.sleep(2.0)

# initialize the first frame in the video stream
background = None

# Face detection parameters
face_casc = cv2.CascadeClassifier('/home/pi/opencv/data/haarcascades/haarcascade_frontalface_default.xml')
scale = 1.3
neighbours = 5

# ThingsBorad Host
THINGSBOARD_HOST = '192.168.43.202'

# Access Token
ACCESS_TOKEN = 'SEC_CAM_TOKEN_2345'

# MQTT Port
MQTT_PORT = 1883

# Define and Start MQTT client
client = mqtt.Client()
client.username_pw_set(ACCESS_TOKEN)
client.connect(THINGSBOARD_HOST, MQTT_PORT, 60)
client.loop_start()

# JSON Intruder MSG
#intrMsg = {'intruderDetected' : 'true'}

# loop over the frames of the video
while True:
	# grab the current frame and initialize the occupied/unoccupied text
	frame = vs.read()
	text = "All Clear"

	# resize the frame, convert it to grayscale, and blur it
	#frame = imutils.resize(frame, width=500, height=500)
	gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
	gauss_blur_gray = cv2.GaussianBlur(gray, (5, 5), 0)

	# if the first frame is None, initialize it
	if background is None:
        	background = gauss_blur_gray
        	continue

	# compute the absolute difference between the current frame and
	# first frame
	frameDelta = cv2.absdiff(background, gauss_blur_gray)
	thresh = cv2.threshold(frameDelta, 20, 255, cv2.THRESH_BINARY)[1]

	# dilate the thresholded image to fill in holes, then find contours
	# on thresholded image
	thresh = cv2.dilate(thresh, np.ones((3, 3), np.uint8), iterations=3)
	cnts = cv2.findContours(thresh.copy(), cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
	cnts = imutils.grab_contours(cnts)

	# loop over the contours
	for c in cnts:
		# if the contour is too small, ignore it
		if cv2.contourArea(c) < min_area:
			continue

		# compute the bounding box for the contour, draw it on the frame,
		# and update the text
		(x, y, w, h) = cv2.boundingRect(c)
		cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
		text = "Intruder Alert!!!"
		# Send alert to TB
		client.publish('v1/devices/me/telemerty', json.dumps(intrMsg), 1)

	# draw the text and timestamp on the frame
	cv2.putText(frame, "Room Status: {}".format(text), (10, 20), cv2.FONT_HERSHEY_DUPLEX, 0.5, (255, 255, 0), 1)
	cv2.putText(frame, datetime.datetime.now().strftime("%A %d %B %Y %I:%M:%S%p"), (10, frame.shape[0] - 10), cv2.FONT_HERSHEY_DUPLEX, 0.4, (0, 0, 255), 1)

	# Get faces in the gray frame and draw a blue rectangle for each
	faces = face_casc.detectMultiScale(gray, scale, neighbours)
	for (x,y,w,h) in faces:
        	cv2.rectangle(frame, (x,y), (x+w,y+h), (255,0,0), 2)

	# show the frame and record if the user presses a key
	#cv2.imshow("Security Feed", frame)
	#cv2.imshow("Thresh", thresh)
	#cv2.imshow("Frame Delta", frameDelta)
	#key = cv2.waitKey(1) & 0xFF

	# if the `q` key is pressed, break from the loop
	#if key == ord("q"):
	#	break

    # Send the the raw frames to FFmpeg sub processes for encoding and transmission
	proc1.stdin.write(frame.tostring())
    proc2.stdin.write(frame.tostring())
    proc3.stdin.write(frame.tostring())
    
# cleanup the camera and close any open windows
vs.stop()
cv2.destroyAllWindows()
