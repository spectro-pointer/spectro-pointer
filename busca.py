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
    MAX_MULTIPLIER = 10

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

    def capture_positions(self):
        self.old_azimuth = self.azimuth_controller.position()
        self.old_elevation = self.elevation_controller.position()

    def restore_positions(self):
        azimuth_controller.move_to(self.old_azimuth)
        elevation_controller.move_to(self.old_elevation)

class LightState:
    def __init__(self):
        self.in_tracking = False
        self.tracked = False

class Busca:
    WIDTH = 640
    HEIGHT = 480

    def __init__(self, lights_controller, error_controller):
        self.lights_controller = lights_controller
        self.error_controller = error_controller
        self.state = {}

    def is_in_range(self, light):
        return light["x"] > (self.WIDTH / 2) - 30 and light["x"] < (self.WIDTH / 2) + 30 and light["y"] > 1 * (self.HEIGHT / 4) and light["y"] < 3 * (self.HEIGHT / 4)

    def process(self):
        # Capture current controller positions
        self.error_controller.capture_positions()

        tracked_lights = self.lights_controller.get_lights()

        # Purge old state
        guids = [tracked_light["guid"] for tracked_light in tracked_lights]
        new_state = {}
        for guid in self.state:
            if guid in guids:
                new_state[guid] = self.state[guid]
        self.state = new_state

        # Initialize state for all new lights
        for tracked_light in tracked_lights:
            if tracked_light["guid"] not in self.state:
                self.state[tracked_light["guid"]] = LightState()

        # Track all lights currently in range
        while True:
            tracked_lights = self.lights_controller.get_lights()

            # Find back the light we are currently tracking
            tracked_light_to_follow = None
            for tracked_light in tracked_lights:
                light_state = self.state.get(tracked_light["guid"])

                if light_state != None and light_state.in_tracking:
                    light_to_follow = tracked_light
                    break

            # If none, find a next light to track
            if tracked_light_to_follow == None:
                for tracked_light in tracked_lights:
                    light = tracked_light["light"]
                    light_state = self.state.get(tracked_light["guid"])

                    if self.is_in_range(light) and light_state != None and not light_state.tracked:
                        tracked_light_to_follow = tracked_light
                        light_state.in_tracking = True
                        break

            # If still none, we are done
            if tracked_light_to_follow == None:
                break

            # Is the light to be tracked centered?
            is_centered = self.error_controller.center(tracked_light_to_follow["light"]["x"], tracked_light_to_follow["light"]["y"])

            if is_centered:
                light_state = self.state.get(tracked_light_to_follow["guid"])
                light_state.in_tracking = False
                light_state.tracked = True

        # Restore controller positions incrementally
        self.error_controller.restore_positions()

        return len(tracked_lights)

def scan(azimuth_controller, elevation_controller, busca, elevation_steps):
    for elevation in range(0, elevation_steps):
        if elevation < 2:
            continue

        elevation_controller.move_to(elevation*(1.0 / elevation_steps) + (1.0 / elevation_steps) / 2.0)

        scans_without_light = 0
        for azimuth in range(0, azimuth_controller.total_steps(), 40):
            azimuth_controller.move_left(40)

            print "@ elevation " + str(elevation_controller.position()) + " & azimuth " + str(azimuth_controller.position())
            if scans_without_light > 10 and scans_without_light % 12 != 0:
                scans_without_light += 1
                print "  skipped because last " + str(scans_without_light) + " scans where without any lights"
                continue

            old_azimuth = azimuth_controller.position()
            old_elevation = elevation_controller.position()

            number_of_lights = busca.process()
            if number_of_lights == 0:
                scans_without_light += 1
            else:
                scans_without_light = 0 

            if azimuth_controller.position() != old_azimuth or abs(elevation_controller.position() - old_elevation) > 0.001:
                raise ValueError("Unexpected controller positions: azimuth " + str(azimuth_controller.position()) + " vs " + str(old_azimuth) + ", elevation: " + str(elevation_controller.position()) + " vs " + str(old_elevation))

MOTORES_IP = "127.0.0.1"
BUSCA_IP = "127.0.0.1"

azimuth_controller = xmlrpclib.ServerProxy("http://" + MOTORES_IP + ":8000")
elevation_controller = xmlrpclib.ServerProxy("http://" + MOTORES_IP + ":8001")
lights_controller = xmlrpclib.ServerProxy("http://" + BUSCA_IP + ":8003")

busca = Busca(lights_controller, ErrorController(azimuth_controller, elevation_controller))

while True:
    scan(azimuth_controller, elevation_controller, busca, elevation_steps = 4)
