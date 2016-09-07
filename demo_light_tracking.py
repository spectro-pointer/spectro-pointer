from lights import *
from random import randint

detector = LightDetector()
tracker = LightTracker()

im = cv2.imread("photos/tracking1.png")
lights = detector.detect(im)
tracker.track(lights)
for light in lights:
    color = (randint(100, 255), randint(100, 255), randint(100, 255))
    tracker.set(light, color)
    cv2.circle(im, (light.x, light.y), 15, color, 3)

cv2.imshow("demo", im)
cv2.waitKey()

im = cv2.imread("photos/tracking2.png")
lights = detector.detect(im)
tracker.track(lights)
for light in lights:
    color = tracker.get(light)
    if color != None:
        cv2.circle(im, (light.x, light.y), 15, color, 3)
cv2.imshow("demo", im)
cv2.waitKey()
