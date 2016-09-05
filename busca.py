import cv2
import xmlrpclib
import time

from light_detector import LightDetector
from camera import Camera

camera = Camera()
detector = LightDetector()
s = xmlrpclib.ServerProxy('http://192.168.0.100:8000')
print "Position: " + str(s.position())

while True:
    im = camera.capture_frame()
    lights = detector.detect(im)

    cv2.drawContours(im, [light["contour"] for light in lights], -1, (0, 255, 0))
    for light in lights:
        cv2.circle(im, (light["x"], light["y"]), 15, (0, 0, 255))

        if len(lights) != 1:
            continue

        x = lights[0]["x"]
        e = x - 320

        if (abs(e) < 10):
            steps = 5
        elif (abs(e) < 15):
            steps = 10
        elif (abs(e) < 20):
            steps = 20
        elif (abs(e) < 50):
            steps = 50
        elif (abs(e) < 100):
            steps = 100
        else:
            steps = 500

        if e < -3:
            print "Light is on the left @ " + str(x) + " & error = " + str(e)
            s.move(True, steps)
            print "New position: " + str(s.position()) + ", moved by " + str(steps) + " steps"
        elif e > 3:
            print "Light is on the right @ " + str(x) + " & error = " + str(e)
            s.move(False, steps)
            print "New position: " + str(s.position()) + ", moved by " + str(steps) + " steps"
        else:
            print "Light is centered! @ " + str(x) + " & error = " + str(e)

    cv2.imshow("live", im)
    cv2.waitKey(100)
