import cv2
import xmlrpclib
import time
from random import randint

from lights import *
from camera import Camera

class ErrorController:
    WIDTH = 640
    HEIGHT = 480
    ERROR_TOLERANCE = 1
    P_AZIMUTH = 5 # 30 is ~4px
    P_ELEVATION = 0.0005 # 0.0025 is ~3 px
    MAX_MULTIPLIER = 10

    def __init__(self, azimuth_controller, elevation_controller):
        self.azimuth_controller = azimuth_controller
        self.elevation_controller = elevation_controller

    def center(self, x, y):
        error_x = x - (self.WIDTH / 2)
        error_y = y - (self.HEIGHT / 2)

        if abs(error_x) <= self.ERROR_TOLERANCE and abs(error_x) <= self.ERROR_TOLERANCE:
            return True

        if abs(error_x) > self.ERROR_TOLERANCE:
            delta = min(abs(error_x), self.MAX_MULTIPLIER) * self.P_AZIMUTH
            if error_x <= 0:
                self.azimuth_controller.move_left(delta)
            else:
                self.azimuth_controller.move_right(delta)

        if abs(error_y) > self.ERROR_TOLERANCE:
            delta = min(abs(error_y), self.MAX_MULTIPLIER) * self.P_ELEVATION
            if error_y <= 0:
                elevation = elevation_controller.position() - delta
                # TODO Check elevation range
                self.elevation_controller.move_to(elevation)
            else:
                elevation = elevation_controller.position() + delta
                # TODO Check elevation range
                self.elevation_controller.move_to(elevation)

        return False

class LightState:
    def __init__(self, color):
        self.in_tracking = False
        self.tracked = False
        self.color = color

class Busca:
    WIDTH = 640
    HEIGHT = 480

    def __init__(self, camera, detector, error_controller):
        self.camera = camera
        self.detector = detector
        self.error_controller = error_controller
        self.tracker = LightTracker()

    def is_in_range(self, light):
        return light.x > (self.WIDTH / 2) - 10 and light.x < (self.WIDTH / 2) + 10 and light.y > 1 * (self.HEIGHT / 4) and light.y < 3 * (self.HEIGHT / 4)

    def clear_tracker(self):
        self.tracker = LightTracker()

    def process(self):
        im = self.camera.capture_frame()
        lights = self.detector.detect(im)

        self.tracker.track(lights)

        # Assign a random color to new lights
        for light in lights:
            light_state = self.tracker.get(light)
            if light_state == None:
                color = (randint(100, 255), randint(100, 255), randint(100, 255))
                light_state = LightState(color)
                self.tracker.set(light, light_state)

        # Show all detected lights
        for light in lights:
            light_state = self.tracker.get(light)
            color = (255, 0, 0) if light_state.tracked else light_state.color
            cv2.circle(im, (light.x, light.y), 15, color, 3)
        cv2.imshow("busca", im)
        cv2.waitKey(100)

        # Track all lights currently in range
        while True:
            im = self.camera.capture_frame()
            lights = self.detector.detect(im)
            self.tracker.track(lights)

            # Find back the light we are currently tracking
            light_to_follow = None
            for light in lights:
                light_state = self.tracker.get(light)
                if light_state != None and light_state.in_tracking:
                    light_to_follow = light
                    break

            # If none, find a next light to track
            if light_to_follow == None:
                for light in lights:
                    light_state = self.tracker.get(light)
                    if self.is_in_range(light) and light_state != None and not light_state.tracked:
                        light_to_follow = light
                        light_state.in_tracking = True
                        break

            # If still none, we are done
            if light_to_follow == None:
                break

            # Is the light to be tracked centered?
            is_centered = self.error_controller.center(light_to_follow.x, light_to_follow.y)

            if is_centered:
                light_state = self.tracker.get(light_to_follow)
                light_state.in_tracking = False
                light_state.tracked = True
                continue

            # Show the current image
            for light in lights:
                light_state = self.tracker.get(light)
                if light_state != None:
                    thickness = 7 if light_state.in_tracking else 3

                    if light_state.in_tracking:
                        color = (0, 0, 255)
                    elif light_state.tracked:
                        color = (255, 0, 0)
                    else:
                        color = light_state.color

                    cv2.circle(im, (light.x, light.y), 15, color, thickness)

            cv2.imshow("busca", im)
            cv2.waitKey(100)

def scan(azimuth_controller, elevation_controller, busca, elevation_steps):
    for elevation in range(0, elevation_steps):
        # Skip the boring elevations
        if elevation != 2:
            continue
        elevation_controller.move_to(elevation*(1.0 / elevation_steps) + (1.0 / elevation_steps) / 2.0)

        busca.clear_tracker()

        for azimuth in range(0, azimuth_controller.total_steps(), 40):
            azimuth_controller.move_left(40)
            old_azimuth = azimuth_controller.position()
            old_elevation = elevation_controller.position()
            busca.process()
            azimuth_controller.move_to(old_azimuth)
            elevation_controller.move_to(old_elevation)

MOTORES_IP = "192.168.0.100"
azimuth_controller = xmlrpclib.ServerProxy("http://" + MOTORES_IP + ":8000")
elevation_controller = xmlrpclib.ServerProxy("http://" + MOTORES_IP + ":8001")
busca = Busca(Camera(), LightDetector(), ErrorController(azimuth_controller, elevation_controller))

while True:
    scan(azimuth_controller,  elevation_controller, busca, elevation_steps = 4)
