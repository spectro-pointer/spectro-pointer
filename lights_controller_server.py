import cv2
import xmlrpclib
import copy
import threading
import time
import rpyc
import numpy as np

from lights import *
from camera import Camera

class LightsController():
    def __init__(self, camera, detector, tracker):
        self.camera = camera
        self.detector = detector
        self.tracker = tracker
        self.lock = threading.Lock()

    def capture_and_track(self):
        im = self.camera.capture_frame()
        lights = self.detector.detect(im)

        self.lock.acquire()
        self.im = im
        self.lights = lights
        old_guids = [tracked_light["guid"] for tracked_light in self.tracker.state()]
        self.tracker.track(lights)
        new_guids = [tracked_light["guid"] for tracked_light in self.tracker.state()]
        self.lock.release()

        new_lights = len(set(new_guids) - set(old_guids))
        print "Tracked a new frame with " + str(len(new_guids)) + " lights, out of which " + str(new_lights) + " were are new"

    def get(self):
        self.lock.acquire()
        result = (copy.deepcopy(self.tracker.state()), self.im.tostring())
        self.lock.release()

        return result

def track_lights(controller):
    print "Starting light tracker loop..."
    while True:
        controller.capture_and_track()

def serve_requests(controller):
    print "Initializing the RPyC server..."

    class MyService(rpyc.Service):
        def on_connect(self):
            pass

        def on_disconnect(self):
            pass
        
        def exposed_get(self):
            return controller.get()

    from rpyc.utils.server import ThreadedServer
    t = ThreadedServer(MyService, port = 8003, protocol_config = {"allow_public_attrs": True, "allow_pickle": True})
    t.start()

if __name__ == '__main__':
    controller = LightsController(Camera(), LightDetector(), LightTracker())

    t = threading.Thread(target = serve_requests, args = (controller, ))
    t.daemon = True
    t.start()

    track_lights(controller)
