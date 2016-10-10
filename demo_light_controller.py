import rpyc
from lights import *
import numpy as np

controller = rpyc.connect("127.0.0.1", 8003, config = {"allow_public_attrs": True, "allow_pickle": True})

while True:
    tracked_lights, im = controller.root.get()
    print "Found " + str(len(tracked_lights)) + " lights"
    for tracked_light in tracked_lights:
      print "GUID: " + str(tracked_light["guid"])
    im = np.fromstring(im, dtype = np.uint8).reshape((480, 640, 3))
    cv2.imshow("foo", im)
    cv2.waitKey(100)
