import rpyc
from lights import *
import numpy as np

controller = rpyc.connect("127.0.0.1", 8003)

print "Getting..."
r = controller.root.get()
print "Done "  + str(len(r[0]))

print "Length: " + str(len(r[1]))

while True:
    r = controller.root.get()
    im = np.fromstring(r[1], dtype=np.uint8).reshape((480, 640, 3))
    cv2.imshow("foo", im)
    cv2.waitKey(100)
