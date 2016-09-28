import cv2
import xmlrpclib
import copy
from multiprocessing import Process, Lock

from lights import *
from camera import Camera

class LightsController:
    def __init__(self, camera, detector, tracker):
        self.camera = camera
        self.tracker = tracker
        self.lock = Lock()

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

    p1 = Process(target = track_lights, args = (controller))
    p1.start()

    p2 = Process(target = serve_requests, args = (controller))
    p2.start()

    p1.join()
    p2.join()
