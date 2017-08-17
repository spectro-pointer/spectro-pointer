import cv2
import copy
import threading
import time
import xmlrpclib
import io

from lights import *
from camera import Camera
from SimpleXMLRPCServer import SimpleXMLRPCServer

class BuscaController():
    def __init__(self, detector, tracker):
        self.detector = detector
        self.tracker = tracker
        self.lock = threading.Lock()

    def track(self, im):
        lights = self.detector.detect(im)

        self.lock.acquire()
        self.im = im
        self.lights = lights
        old_guids = [tracked_light["guid"] for tracked_light in self.tracker.state()]
        self.tracker.track(lights)
        new_guids = [tracked_light["guid"] for tracked_light in self.tracker.state()]
        self.lock.release()

        new_lights = len(set(new_guids) - set(old_guids))
        print "Tracked a new frame with " + str(len(new_guids)) + " lights, out of which " + str(new_lights) + " are new"

    def get_lights_and_image(self):
        self.lock.acquire()
        result = (copy.deepcopy(self.tracker.state()), xmlrpclib.Binary(self.im.tostring()))
        self.lock.release()

        return result

    def get_lights(self):
        self.lock.acquire()
        result = copy.deepcopy(self.tracker.state())
        self.lock.release()

        return result

def track_lights(camera, controller):
    print "Starting light tracker loop..."
    while True:
        yield camera.stream()
        controller.track(camera.image())

def serve_requests(controller):
    print "Initializing the XML-RPC server..."
    server = SimpleXMLRPCServer(("0.0.0.0", 8003))
    server.register_instance(controller)
    print "Waiting for incoming requests..."
    server.serve_forever()

if __name__ == '__main__':
    controller = BuscaController(LightDetector(), LightTracker())

    t = threading.Thread(target = serve_requests, args = (controller, ))
    t.daemon = True
    t.start()

    camera = Camera(10)
    camera.capture_sequence(track_lights(camera, controller)) 
