# import the necessary packages
from imutils.video import VideoStream
import argparse
import datetime
import imutils
import time
import cv2

# construct the argument parser and parse the arguments
ap = argparse.ArgumentParser()
ap.add_argument("-a", "--min-area", type=int, default=500, help="minimum area size")
args = vars(ap.parse_args())

# if the video argument is None, then we are reading from webcam
vs = VideoStream(src=0).start()
time.sleep(2.0)

# initialize the first frame in the video stream
frame = vs.read()
frame = imutils.resize(frame, width=500)
gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
gray = cv2.GaussianBlur(gray, (21, 21), 0)
referenceFrame = gray
refreshTime = time.time()
stateRefresh = refreshTime
t = "Unoccupied"
text = "Unoccupied"

# loop over the frames of the video
while True:
	# grab the current frame and initialize the occupied/unoccupied
	# text
	currTime = time.time()

	frame = vs.read()

	# resize the frame, convert it to grayscale, and blur it
	frame = imutils.resize(frame, width=500)
	gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
	gray = cv2.GaussianBlur(gray, (21, 21), 0)

	if currTime > refreshTime + 2:
		referenceFrame = gray
		refreshTime = currTime
		t = text
		print(t)

	# compute the absolute difference between the current frame and
	# first frame
	frameDelta = cv2.absdiff(referenceFrame, gray)
	thresh = cv2.threshold(frameDelta, 25, 255, cv2.THRESH_BINARY)[1]

	# dilate the thresholded image to fill in holes, then find contours
	# on thresholded image
	thresh = cv2.dilate(thresh, None, iterations=2)
	cnts = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL,
		cv2.CHAIN_APPROX_SIMPLE)
	cnts = cnts[0] if imutils.is_cv2() else cnts[1]

	# loop over the contours
	if (len(cnts) is 0):
		text = "No Movement"

	x1Min = 500
	y1Min = 500
	x2Max = 0
	y2Max = 0
	pList = []
	for c in cnts:
		# if the contour is too small, ignore it
		if cv2.contourArea(c) < args["min_area"]:
			continue

		# compute the bounding box for the contour, draw it on the frame,
		# and update the text
		(x, y, w, h) = cv2.boundingRect(c)
		x1 = x
		y1 = y
		x2 = x+w
		y2 = y+h
		CoordList = {"x1":x1, "y1":y1, "x2":x2, "y2":y2}
		pList.append(CoordList)
		#cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)

		text = "Movement"
		# draw the text and timestamp on the frame
	for p in pList:
		x1 = p['x1']
		y1 = p['y1']
		x2 = p['x2']
		y2 = p['y2']
		if x1 < x1Min: x1Min = x1
		if y1 < y1Min: y1Min = y1
		if x2 > x2Max: x2Max = x2
		if y2 > y2Max: y2Max = y2


	if len(pList) > 0:
		cv2.rectangle(frame, (x1Min, y1Min), (x2Max, y2Max), (0, 255, 0), 2)
	cv2.putText(frame, "Room Status: {}".format(text), (10, 20),
		cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
	cv2.putText(frame, datetime.datetime.now().strftime("%A %d %B %Y %I:%M:%S%p"),
		(10, frame.shape[0] - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.35, (0, 0, 255), 1)
	# show the frame and record if the user presses a key
	cv2.imshow("Thresh", thresh)
	cv2.imshow("Frame Delta", frameDelta)
	cv2.imshow("Security Feed", frame)
	key = cv2.waitKey(1) & 0xFF

	# if the `q` key is pressed, break from the lop
	if key == ord("q"):
		break

# cleanup the camera and close any open windows
vs.stop() if args.get("video", None) is None else vs.release()
cv2.destroyAllWindows()
