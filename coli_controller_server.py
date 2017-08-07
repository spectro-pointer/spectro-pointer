import cv2
import copy
import threading
import time
import xmlrpclib

from camera import Camera
from SimpleXMLRPCServer import SimpleXMLRPCServer

class ColiController():
    def __init__(self, camera):
        self.camera = camera
        self.lock = threading.Lock()

    def capture(self):
        im = self.camera.capture_frame()
        self.lock.acquire()
        self.im = im
        self.lock.release()

        print "Received a new frame"

    def get_image(self):
        self.lock.acquire()
        result = xmlrpclib.Binary(self.im.tostring())
        self.lock.release()

        return result

def capture_frames(controller):
    print "Starting the frame capture loop..."
    while True:
        controller.capture()

def serve_requests(controller):
    print "Initializing the XML-RPC server..."
    server = SimpleXMLRPCServer(("0.0.0.0", 8002))
    server.register_instance(controller)
    print "Waiting for incoming requests..."
    server.serve_forever()

if __name__ == '__main__':
    controller = ColiController(Camera(3))

    t = threading.Thread(target = serve_requests, args = (controller, ))
    t.daemon = True
    t.start()

    capture_frames(controller)
