import cv2
import sys

MIN_BRIGHTNESS_THRESHOLD = 150
MIN_LIGHT_AREA = 15

if len(sys.argv) != 2:
  print "Expected 1 argument: The photo to analyze"
  quit(1)

frame = cv2.imread(sys.argv[1])

gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
_, gray_frame = cv2.threshold(gray_frame, MIN_BRIGHTNESS_THRESHOLD, 255, cv2.THRESH_BINARY)
contours, _ = cv2.findContours(gray_frame.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
lightContours = [contour for contour in contours if cv2.contourArea(contour) >= MIN_LIGHT_AREA]
print "Found " + str(len(lightContours)) + " lights"
cv2.drawContours(frame, lightContours, -1, (0, 255, 0))
cv2.imshow("", frame)

cv2.waitKey()
