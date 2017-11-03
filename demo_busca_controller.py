import xmlrpclib
import numpy as np
import cv2
from random import randint

controller = xmlrpclib.ServerProxy("http://127.0.0.1:8003")
state = {}

while True:
    tracked_lights, im_str = controller.get_lights_and_image()
    im_str = str(im_str)
    im = np.fromstring(im_str, dtype = np.uint8).reshape((480, 640, 3))

    # Show all detected lights
    for detectedLight in tracked_lights:
        if detectedLight["area"] >= 7:
            color = (randint(100, 255), randint(100, 255), randint(100, 255))
            cv2.circle(im, (detectedLight["x"], detectedLight["y"]), 15, color, 3)

    # Draw colimation point
    cv2.circle(im, (325 , 231), 5, (0, 0, 255), 1)

    print "Showing " + str(len(tracked_lights)) + " lights"
    for light in tracked_lights:
        print "x: " + str(light["x"]) + "y: " + str(light["y"]) + "Area " + str(light["area"])

    cv2.imshow("busca", im)
    cv2.waitKey(100)
