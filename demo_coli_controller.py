import cv2
import xmlrpclib
import numpy as np

controller = xmlrpclib.ServerProxy("http://127.0.0.1:8002")

while True:
    im_str = str(controller.get_image())
    im = np.fromstring(im_str, dtype = np.uint8).reshape((387-100, 443-185, 3))
    cv2.circle(im, (128, 137), 5, (0, 0, 255), 1)
    cv2.imshow("coli", im)
    cv2.waitKey(333)
