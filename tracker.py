import xmlrpclib
import time
import rpyc
import numpy as np
from random import randint

class ErrorController:
    WIDTH = 640
    HEIGHT = 480
    ERROR_TOLERANCE = 1
    P_AZIMUTH = 5 # 30 is ~4px
    P_ELEVATION = 0.0003 # 0.0025 is ~3 px
    MAX_MULTIPLIER = 8

    def __init__(self, azimuth_controller, elevation_controller):
        self.azimuth_controller = azimuth_controller
        self.elevation_controller = elevation_controller

    def center(self, x, y):
        error_x = x - (self.WIDTH / 2)
        error_y = y - (self.HEIGHT / 2)

        if abs(error_x) <= self.ERROR_TOLERANCE and abs(error_y) <= self.ERROR_TOLERANCE:
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
    def __init__(self):
        self.in_tracking = False
        self.tracked = False

class Busca:
    WIDTH = 640
    HEIGHT = 480
    MIN_LIGHT_AREA = 7

    def __init__(self, error_controller):
        self.error_controller = error_controller
        self.state = {}
        self.is_centered = False

    def update_state(self, lights):
        # Purge old state
        guids = [light["guid"] for light in lights]
        new_state = {}
        for guid in self.state:
            if guid in guids:
                new_state[guid] = self.state[guid]
        self.state = new_state

        # Initialize state for all new lights
        for light in lights:
            if light["guid"] not in self.state:
                self.state[light["guid"]] = LightState()

    def get_tracked_light(self, lights):
        for light in lights:
            light_state = self.state.get(light["guid"])

            if light_state != None and light_state.in_tracking:
                return light

        return None

    def get_new_light_to_track(self, lights):
        self.is_centered = False
        self.update_state(lights)

        right_most_light_to_track = None

        for light in lights:
            light_x = light["light"]["x"]
            light_state = self.state.get(light["guid"])

            if (light_x <= self.WIDTH / 2 and light["light"]["area"] >= self.MIN_LIGHT_AREA and
                    (not light_state.tracked) and
                    (right_most_light_to_track == None or light_x > right_most_light_to_track["light"]["x"])):
                right_most_light_to_track = light

        if right_most_light_to_track == None:
            return None

        light_state = self.state.get(right_most_light_to_track["guid"])
        light_state.in_tracking = True

        return right_most_light_to_track

    def center_tracked_light(self, lights):
        self.is_centered = False
        self.update_state(lights)

        tracked_light = self.get_tracked_light(lights)

        if tracked_light == None:
            print "  The tracked light disappeared"
            return True

        print "Tracking light %s at %d, %d" % (tracked_light["guid"], tracked_light["light"]["x"], tracked_light["light"]["y"])

        if not self.error_controller.center(tracked_light["light"]["x"], tracked_light["light"]["y"]):
            return False

        print "Centered on light %s at %d, %d" % (tracked_light["guid"], tracked_light["light"]["x"], tracked_light["light"]["y"])
        light_state = self.state.get(tracked_light["guid"])
        light_state.in_tracking = False
        light_state.tracked = True
        self.is_centered = True

        return True

    def is_centered(self):
        return self.is_centered

def scan(azimuth_controller, elevation_controller, lights_controller, busca, elevation_steps):
    for elevation_step in range(0, elevation_steps):
        if elevation_step != 2:
            continue

        elevation = elevation_step*(1.0 / elevation_steps) + (1.0 / elevation_steps) / 2.0

        azimuth_controller.move_to(0)

        while True:
            elevation_controller.move_to(elevation)

            print "@ elevation %f & azimuth %d" % (elevation_controller.position(), azimuth_controller.position())

            lights = lights_controller.get_lights()
            if busca.get_new_light_to_track(lights) == None:
                azimuth_controller.move_left(120)
                continue

            while not busca.center_tracked_light(lights):
                lights = lights_controller.get_lights()

            if busca.is_centered():
                print "  Final elevation %f & azimuth %d" % (elevation_controller.position(), azimuth_controller.position())
                exit()

MOTORES_IP = "127.0.0.1"
BUSCA_IP = "127.0.0.1"

azimuth_controller = xmlrpclib.ServerProxy("http://" + MOTORES_IP + ":8000")
elevation_controller = xmlrpclib.ServerProxy("http://" + MOTORES_IP + ":8001")
lights_controller = xmlrpclib.ServerProxy("http://" + BUSCA_IP + ":8003")

busca = Busca(ErrorController(azimuth_controller, elevation_controller))

scan(azimuth_controller, elevation_controller, lights_controller, busca, elevation_steps = 4)