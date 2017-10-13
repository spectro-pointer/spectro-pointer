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

#    # Purge old lights state
#    guids = [tracked_light["guid"] for tracked_light in tracked_lights]
#    new_state = {}
#    for guid in state:
#        if guid in guids:
#            new_state[guid] = state[guid]
#    state = new_state
#
#    # Assign a random color to new lights
#    new_lights = 0
#    for tracked_light in tracked_lights:
#        light_state = state.get(tracked_light["guid"])
#        if light_state == None:
#            color = (randint(100, 255), randint(100, 255), randint(100, 255))
#            state[tracked_light["guid"]] = color
#            new_lights += 1

    # Show all detected lights
    for detectedLight in tracked_lights:
        if detectedLight["area"] >= 7:
            color = (randint(100, 255), randint(100, 255), randint(100, 255))
            cv2.circle(im, (detectedLight["x"], detectedLight["y"]), 15, color, 3)

    # Draw colimation point
    cv2.circle(im, (316, 235), 5, (0, 0, 255), 3)

    print "Showing " + str(len(tracked_lights)) + " lights"
    for light in tracked_lights:
        print "x: " + str(light["x"]) + "y: " + str(light["y"]) + "Area " + str(light["area"])

    cv2.imshow("busca", im)
    cv2.waitKey(100)
