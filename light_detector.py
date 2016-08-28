import cv2

MIN_BRIGHTNESS_THRESHOLD = 150

frame = cv2.imread("photos/small4.jpg")
frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
_retval, frame = cv2.threshold(frame, MIN_BRIGHTNESS_THRESHOLD, 255, cv2.THRESH_BINARY)
cv2.imshow("frame", frame)

cv2.waitKey()
