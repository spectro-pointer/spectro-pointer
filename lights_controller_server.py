import cv2
import xmlrpclib
import copy
import thread
import threading

from SimpleXMLRPCServer import SimpleXMLRPCServer

from lights import *
from camera import Camera

class LightsController:
    def __init__(self, camera, detector, tracker):
        self.camera = camera
        self.tracker = tracker
        self.lock = threading.Lock()

    def loop(self):
        im = self.camera.capture_frame()
        lights = self.detector.detect(im)

        self.lock.acquire()
        self.im = im
        self.lights = lights
        self.tracker.track(lights)
        self.lock.release()

    def get(self):
        self.lock.acquire()
        result = (copy.deepcopy(self.lights), copy.deepcopy(self.tracker.dictionary), copy.deepcopy(self.im))
        self.lock.release()

        return result

    def set(self, light, state):
        self.lock.acquire()
        result = self.tracker.set_if_present(light, state)
        self.lock.release()

        return result

def track_lights(controller):
    print "Starting light tracker loop..."
    controller.loop()

def serve_requests(controller):
    print "Initializing the XML-RPC server..."
    server = SimpleXMLRPCServer(("0.0.0.0", 8003))
    server.register_instance(controller)

    print "Waiting for incoming requests..."

    server.serve_forever()

if __name__ == '__main__':
    controller = LightsController(Camera(), LightDetector(), LightTracker())

    thread.start_new_thread(track_lights, (controller, ))
    thread.start_new_thread(serve_requests, (controller, ))
