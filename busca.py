import cv2
import xmlrpclib
import time
from random import randint

from lights import *
from camera import Camera

MOTORES_IP = "192.168.0.100"
ELEVATION_STEPS = 4

camera = Camera()
azimuth_controller = xmlrpclib.ServerProxy("http://" + MOTORES_IP + ":8000")
elevation_controller = xmlrpclib.ServerProxy("http://" + MOTORES_IP + ":8001")
detector = LightDetector()

class ErrorController:
    WIDTH = 640
    HEIGHT = 480
    ERROR_TOLERANCE = 1
    P_AZIMUTH = 5 # 30 is ~4px
    P_ELEVATION = 0.0005 # 0.0025 is ~3 px

    @staticmethod
    def center(x, y):
        error_x = x - (self.WIDTH / 2)
        error_y = y - (self.HEIGHT / 2)

        if abs(error_x) <= self.ERROR_TOLERANCE and abs(error_x) <= self.ERROR_TOLERANCE:
            return True

        if abs(error_x) > self.ERROR_TOLERANCE:
            delta = abs(error_x) * self.P_AZIMUTH
            if error_x <= 0:
                azimuth_controller.move_left(delta)
            else:
                azimuth_controller.move_right(delta)

        if abs(error_y) > self.ERROR_TOLERANCE:
            delta = abs(error_y) * self.P_ELEVATION
            if error_y <= 0:
                elevation = elevation_controller.position() - delta
                # TODO Check elevation range
                elevation_controller.move_to(elevation)
            else:
                elevation = elevation_controller.position() + delta
                # TODO Check elevation range
                elevation_controller.move_to(elevation)

        return False

class LightState:
    def __init__(self, color):
        self.in_tracking = False
        self.tracked = False
        self.color = color

def is_in_range(light):
    return light.x > 160 and light.x < 520 and light.y > 120 and light.y < 360

def process():
    im = camera.capture_frame()
    lights = detector.detect(im)

    tracker = LightTracker()
    tracker.track(lights)

    if len(lights) == 0:
        print "No lights detects"
        cv2.imshow("busca", im)
        cv2.waitKey(100)

    for light in lights:
        if is_in_range(light):
            color = (randint(100, 255), randint(100, 255), randint(100, 255))
            light_state = LightState(color)
            tracker.set(light, light_state)

    count = 0
    for light in lights:
        light_state = tracker.get(light)
        if light_state != None:
            cv2.circle(im, (light.x, light.y), 15, light_state.color, 3)
            count += 1
    print "Showing the " + str(count) + " detected lights in range..."
    cv2.imshow("busca", im)
    cv2.waitKey(5000)

    while True:
        im = camera.capture_frame()
        lights = detector.detect(im)
        tracker.track(lights)

        # Find back the light we are currently tracking
        light_to_follow = None
        for light in lights:
            light_state = tracker.get(light)
            if light_state != None and light_state.in_tracking:
                light_to_follow = light
                break
        print "Currently tracking: " + str(light_to_follow)

        # If none, find a next light to track
        if light_to_follow == None:
            for light in lights:
                light_state = tracker.get(light)
                if light_state != None and not light_state.tracked:
                    light_to_follow = light
                    light_state.in_tracking = True
                    break
        print "Now tracking: " + str(light_to_follow)

        # If still none, we are done
        if light_to_follow == None:
            break

        # Is the light to be tracked centered?
        is_centered = ErrorController.center(light_to_follow.x, light_to_follow.y)

        if is_centered:
            light_state = tracker.get(light_to_follow)
            light_state.in_tracking = False
            light_state.tracked = True
            continue

        # Show the current image
        for light in lights:
            light_state = tracker.get(light)
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

def scan():
    for elevation in range(0, ELEVATION_STEPS):
        # Skip the boring elevations
        if elevation != 2:
            continue

        elevation_controller.move_to(elevation*(1.0 / ELEVATION_STEPS) + (1.0 / ELEVATION_STEPS) / 2.0)
        for azimuth in range(0, azimuth_controller.total_steps(), 480*2):
            azimuth_controller.move_left(480*2)
            old_position = azimuth_controller.position()
            print "Azimuth: " + str(azimuth_controller.position()) + " Elevation: " + str(elevation_controller.position())
            process()
            new_position = azimuth_controller.position()
            print "New position " + str(new_position) + ", old position " + str(old_position)
            azimuth_controller.move_to(old_position)

while True:
    scan()
