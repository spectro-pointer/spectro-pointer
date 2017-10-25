# -*- coding: utf-8 -*-
"""
Created on Fri Oct  6 17:59:03 2017

@author: newho
"""
import cv2
import xmlrpclib
import time
import rpyc
import os
import numpy as np
import matplotlib.pyplot as plt
from random import randint
from datetime import datetime
import centrador_test as centrador

from spectrometer import Spectrometer

class ErrorController:
    WIDTH = 640
    HEIGHT = 480
    ERROR_TOLERANCE = 1
    P_AZIMUTH = 1 # 30 is ~4px
    P_ELEVATION = 0.00025 # 0.0025 is ~3 px
    MAX_MULTIPLIER = 50

    def __init__(self, azimuth_controller, elevation_controller):
        self.azimuth_controller = azimuth_controller
        self.elevation_controller = elevation_controller

    def center(self, x, y):
        error_x = x - (self.WIDTH / 2)
        error_y = y - (self.HEIGHT / 2)

        if abs(error_x) <= self.ERROR_TOLERANCE and abs(error_y) <= self.ERROR_TOLERANCE:
            return True

        error = abs(error_x)
        if abs(error_x) > self.ERROR_TOLERANCE:
            if error <= 3:
                p = 1
            elif error <= 10:
                p = self.MAX_MULTIPLIER / 2
            else:
                p = self.MAX_MULTIPLIER

            delta = p * self.P_AZIMUTH
            if error_x <= 0:
                self.azimuth_controller.move_left(delta)
            else:
                self.azimuth_controller.move_right(delta)

        error = abs(error_y)
        if error > self.ERROR_TOLERANCE:
            if error <= 3:
                p = 1
            elif error <= 10:
                p = self.MAX_MULTIPLIER / 2
            else:
                p = self.MAX_MULTIPLIER

            delta = p * self.P_ELEVATION
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

    def update_state(self, lights): #Problem?
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
        self.update_state(lights)

        tracked_light = self.get_tracked_light(lights)

        if tracked_light == None:
            return False, False

        print "Tracking light %s at %d, %d" % (tracked_light["guid"], tracked_light["light"]["x"], tracked_light["light"]["y"])

        if not self.error_controller.center(tracked_light["light"]["x"], tracked_light["light"]["y"]):
            return True, False

        print "Centered on light %s at %d, %d" % (tracked_light["guid"], tracked_light["light"]["x"], tracked_light["light"]["y"])
        light_state = self.state.get(tracked_light["guid"])
        light_state.in_tracking = False
        light_state.tracked = True

        return False, True
    
class Positions:
    'A collection of positions. A position will store the collection of lights found at one position'
    
    def __init__(self, numAzimuthPositions, numElevationPositions):
		print "Positions initialized"
		self.positions = []
        
    def addPosition(self, newPosition):
		self.positions.append(newPosition)
        
class Position:
    'A position of the spectro-pointer. Includes the Azimuth and Elevation angles. Contains all of the lights found at the position'
    
    def __init__(self, elevation, azimuth, elevationID, azimuthID):
        self.azimuth = azimuth
        self.elevation = elevation
        self.elevationID = elevationID
        self.azimuthID = azimuthID
        
    def findLights(self, lightsController):
        detectedLights = lights_controller.get_lights()
        self.lights = []
        for light in detectedLights:
            self.lights.append(Light(light["light"]["x"], light["light"]["y"], self.azimuth, self.elevation, light["light"]["area"]))
            
    def getAzimuth(self):
        return self.azimuth
    
    def getElevation(self):
        return self.elevation
    
    def getAzimuthID(self):
        return self.azimuthID
    
    def getElevationID(self):
        return self.elevationID
    
    def visitLights(self, elevation_controller, azimuth_controller):
        for light in self.lights:
            light.center(elevation_controller, azimuth_controller)
            
    def printLights(self):
        for light in self.lights:
            print "Light Position: X: " + str(light.getX()) + " Y: " + str(light.getY())
class Light:
    'Light'
    def __init__(self, x, y, position_azimuth, position_elevation, area):
        self.x = x
        self.y = y
        self.area = area
        self.azimuth, self.elevation = centrador.pixel2Absolute(x, y, position_azimuth, position_elevation)
        
        
    def setAbsolutePosition(self, azimuth, elevation):
        self.azimuth = azimuth
        self.elevation = elevation
        
    def center(self, elevation_controller, azimuth_controller):
        elevation_controller.move_to(self.elevation)
        azimuth_controller.move_to(self.azimuth)
        print "light at:\nElevation: " + str(self.elevation) + " Azimuth: " + str(self.azimuth) + " Visited."
        
    def takeCollimation(self):
        print("hello")
    
    def getX(self):
        return self.x
        
    def getY(self):
        return self.y
        
class Coli:
    WIDTH = 190
    HEIGHT = 170
    FIBER_X = 75
    FIBER_Y = 77
    DX = 25
    DY = 4
    MIN_INTENSITY_ELEVATION = 30000
    MAX_TRIALS_ELEVATION = 60
    MIN_INTENSITY_AZIMUTH = 4500
    MAX_TRIALS_AZIMUTH = 25

    def __init__(self, coli_controller, azimuth_controller, elevation_controller):
        self.coli_controller = coli_controller
        self.azimuth_controller = azimuth_controller
        self.elevation_controller = elevation_controller

    def colimate(self):
        print "Starting elevation colimation at %f" % elevation_controller.position()

        last_intensity = 0
        for i in range(0, self.MAX_TRIALS_ELEVATION):
            time.sleep(0.7)

            im_str = str(coli_controller.get_image())
            im = np.fromstring(im_str, dtype = np.uint8).reshape((self.HEIGHT, self.WIDTH, 3))
            roi = im[self.FIBER_Y-self.DY:self.FIBER_Y+self.DY, 0:self.WIDTH]
            (b, g, r) = cv2.split(roi)
            intensity = cv2.sumElems(cv2.max(cv2.max(b, g), r))[0]

            print "At elevation %f, measured colimation intensity of %d" % (elevation_controller.position(), intensity)

            if intensity >= self.MIN_INTENSITY_ELEVATION and intensity < last_intensity:
                print "Starting azimuth colimation at %d" % azimuth_controller.position()

                for j in range(0, self.MAX_TRIALS_AZIMUTH):
                    time.sleep(0.7)

                    im_str = str(coli_controller.get_image())
                    im = np.fromstring(im_str, dtype = np.uint8).reshape((self.HEIGHT, self.WIDTH, 3))
                    roi = im[self.FIBER_Y-self.DY:self.FIBER_Y+self.DY, self.FIBER_X-self.DX:self.FIBER_X]
                    (b, g, r) = cv2.split(roi)
                    intensity_left = cv2.sumElems(cv2.max(cv2.max(b, g), r))[0]

                    roi = im[self.FIBER_Y-self.DY:self.FIBER_Y+self.DY, self.FIBER_X:self.FIBER_X+self.DX]
                    (b, g, r) = cv2.split(roi)
                    intensity_right = cv2.sumElems(cv2.max(cv2.max(b, g), r))[0]

                    print "At azimuth %d, measured colimation intensities: left %d, right %d" % (azimuth_controller.position(), intensity_left, intensity_right)

                    if intensity_left >= self.MIN_INTENSITY_AZIMUTH and intensity_right >= self.MIN_INTENSITY_AZIMUTH:
                        return True, im
                    elif intensity_left >= self.MIN_INTENSITY_AZIMUTH and intensity_right < self.MIN_INTENSITY_AZIMUTH:
                        azimuth_controller.move_left(1)
                    else:
                        azimuth_controller.move_right(1)

                return False, im

            last_intensity = intensity
            elevation_controller.move_to(elevation_controller.position() - 0.00025)

        return False, im
        
def background(azimuth_controller, elevation_controller, lights_controller, busca, coli, spectrometer, azimuthRange, elevationRange):
    positions = Positions(len(azimuthRange), len(elevationRange))
    elevationID = 0
    azimuthID = 0
    for elevation in elevationRange:
        for angle in azimuthRange:
            elevation_controller.move_to(elevation)
            azimuth_controller.move_to(angle)
            print "@ elevation %f & azimuth %d" % (elevation_controller.position(), azimuth_controller.position())
            time.sleep(0.2)
            newPosition = Position(elevation_controller.position(), azimuth_controller.position(), elevationID, azimuthID)
            print "Position Created"
            newPosition.findLights(lights_controller)
            newPosition.printLights()
            newPosition.visitLights(elevation_controller, azimuth_controller)
            positions.addPosition(newPosition)
            azimuthID += 1
	    elevationID += 1
		
	


MOTORES_IP = "127.0.0.1"
BUSCA_IP = "127.0.0.1"
COLI_IP = "127.0.0.1"
SPECTROMETER_IP = "127.0.0.1"
SPECTROMETER_INTEGRATION_TIME = 20

azimuth_controller = xmlrpclib.ServerProxy("http://" + MOTORES_IP + ":8000")
elevation_controller = xmlrpclib.ServerProxy("http://" + MOTORES_IP + ":8001")
lights_controller = xmlrpclib.ServerProxy("http://" + BUSCA_IP + ":8003")
coli_controller = xmlrpclib.ServerProxy("http://" + COLI_IP + ":8002")

spectrometer = Spectrometer(SPECTROMETER_IP, 1865)
spectrometer.set_integration(SPECTROMETER_INTEGRATION_TIME * 1e6)

busca = Busca(ErrorController(azimuth_controller, elevation_controller))
coli = Coli(coli_controller, azimuth_controller, elevation_controller)

elevation_range = [ 0.669685, 0.5, 0.000300]
azimuth_range = [0, 2400, 4800, 7200, 9600, 12000, 14400, 16800]

background(azimuth_controller, elevation_controller, lights_controller, busca, coli, spectrometer, azimuth_range, elevation_range)
#scan(azimuth_controller, elevation_controller, lights_controller, busca, coli, spectrometer, elevation_steps = 4)
