import rpyc
from lights import *
import numpy as np

controller = rpyc.connect("127.0.0.1", 8003)

while True:
    lights, tracker, im = controller.root.get()
    print "Found " + str(len(lights)) + " lights, " + str(len(tracker)) + " of which are tracked"
    im = np.fromstring(im, dtype = np.uint8).reshape((480, 640, 3))
    cv2.imshow("foo", im)
    cv2.waitKey(100)
