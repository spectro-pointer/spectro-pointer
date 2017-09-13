import cv2
import copy
import threading
import time
import xmlrpclib

from camera import Camera
from SimpleXMLRPCServer import SimpleXMLRPCServer

class ColiController():
    def __init__(self):
        self.lock = threading.Lock()

    def capture(self, im):
        im = im[100:387, 185:443]
        im = cv2.flip(im, 0)
        self.lock.acquire()
        self.im = im
        self.lock.release()

        print "Received a new frame"

    def get_image(self):
        self.lock.acquire()
        result = xmlrpclib.Binary(self.im.tostring())
        self.lock.release()

        return result

def capture_frames(camera, controller):
    print "Starting the frame capture loop..."
    while True:
        yield camera.stream()
        controller.capture(camera.image())

def serve_requests(controller):
    print "Initializing the XML-RPC server..."
    server = SimpleXMLRPCServer(("0.0.0.0", 8002))
    server.register_instance(controller)
    print "Waiting for incoming requests..."
    server.serve_forever()

if __name__ == '__main__':
    controller = ColiController()

    t = threading.Thread(target = serve_requests, args = (controller, ))
    t.daemon = True
    t.start()

    camera = Camera(3)
    camera.capture_sequence(capture_frames(camera, controller)) 
