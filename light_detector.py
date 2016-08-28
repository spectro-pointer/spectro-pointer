import cv2

MIN_BRIGHTNESS_THRESHOLD = 150

frame = cv2.imread("photos/small4.jpg")
gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
_, gray_frame = cv2.threshold(gray_frame, MIN_BRIGHTNESS_THRESHOLD, 255, cv2.THRESH_BINARY)
contours = cv2.findContours(gray_frame.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
cv2.drawContours(frame, contours[0], -1, (0, 255, 0))
cv2.imshow("", frame)

cv2.waitKey()
