import cv2
import sys

MIN_BRIGHTNESS_THRESHOLD = 150
MIN_LIGHT_AREA = 15
MAX_LIGHT_AREA = 500

if len(sys.argv) != 2:
  print "Expected 1 argument: The photo to analyze"
  quit(1)

frame = cv2.imread(sys.argv[1])

gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
_, gray_frame = cv2.threshold(gray_frame, MIN_BRIGHTNESS_THRESHOLD, 255, cv2.THRESH_BINARY)
contours, _ = cv2.findContours(gray_frame.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
lights = []
for contour in contours:
  m = cv2.moments(contour)
  area = m["m00"]
  if (area >= MIN_LIGHT_AREA and area <= MAX_LIGHT_AREA):
    x = int(m["m10"] / m["m00"])
    y = int(m["m01"] / m["m00"])
    lights.append({"x": x, "y": y, "area": area, "contour": contour})

print "Found " + str(len(lights)) + " lights"
cv2.drawContours(frame, [light["contour"] for light in lights], -1, (0, 255, 0))
for light in lights:
  cv2.circle(frame, (light["x"], light["y"]), MIN_LIGHT_AREA, (0, 0, 255))

cv2.imshow("", frame)
cv2.waitKey()
