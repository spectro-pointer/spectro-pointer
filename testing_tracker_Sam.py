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
from tracker_lib import getContour, check_quadrant
from spectrometer import Spectrometer


    
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
        print "Capturing Lights..."
        detectedLights, im = lights_controller.get_lights_and_image()
        savePicture(detectedLights, im)
        self.lights = []
        print detectedLights
        for light in detectedLights:
            newLight = Light(light["x"], light["y"], self.azimuth, self.elevation, light["area"])
            self.lights.append(newLight)
            
    def getAzimuth(self):
        return self.azimuth
    
    def getElevation(self):
        return self.elevation
    
    def getAzimuthID(self):
        return self.azimuthID
    
    def getElevationID(self):
        return self.elevationID
    
    def visitLights(self, elevation_controller, azimuth_controller, coli_controller):
        for light in self.lights:
            light.center(elevation_controller, azimuth_controller)
            light.takeCollimation(coli_controller, elevation_controller, azimuth_controller);
    
    def printAbsPositions(self):
        for light in self.lights:
            print "Light Position: Elevation: " + str(light.getElevation()) + " Azimuth: " + str(light.getAzimuth())
  
    def printLights(self):
        for light in self.lights:
            print "Light Position: X: " + str(light.getX()) + " Y: " + str(light.getY())
class Light:
    'Light'
    def __init__(self, x, y, position_azimuth, position_elevation, area):
        self.x = x
        self.y = y
        self.area = area
        azi_ele = centrador.pixel2Absolute(x, y, position_azimuth, position_elevation)
        self.azimuth = azi_ele[0]
        self.elevation = azi_ele[1]
        
        
    def setAbsolutePosition(self, azimuth, elevation):
        self.azimuth = azimuth
        self.elevation = elevation
        
    def center(self, elevation_controller, azimuth_controller):
        elevation_controller.move_to(self.elevation)
        azimuth_controller.move_to(self.azimuth)
        print "light at:\nElevation: " + str(self.elevation) + " Azimuth: " + str(self.azimuth) + " Visited."
        
    def takeCollimation(self, coli_controller, elevation_controller, azimuth_controller):
        centered = False
        undetectedCounter = 0
        while not centered:
            im_str = str(coli_controller.get_image())
            im = np.fromstring(im_str, dtype = np.uint8).reshape((387-100, 443-185, 3))
            cx, cy = getContour(im)
            offset = check_quadrant(cx, cy)
            print offset
            if(offset == ''):
                print "No Light Detected"
                undetectedCounter += 1
                if(undetectedCounter > 200):
                    print "Reached Undetected Threshold"
                    break
            elif(offset.find("x-center") != -1 and offset.find("y-center") != -1):
                print "Light centered"
                time.sleep(5)
                centered = True
            elif(offset.find("left") != -1):
                print "Move Left"
                azimuth_controller.move_left(1)
            elif(offset.find("right") != -1):
                print "Move Right"
                azimuth_controller.move_right(1)
            elif(offset.find("up") != -1):
                print "Move Up"
                elevation_controller.move_to(elevation_controller.position() - 0.00015)
            elif(offset.find("down") != -1):
                print "Move Down" 
                elevation_controller.move_to(elevation_controller.position() + 0.00015)
        print "Finished Collimation"
    
    def getX(self):
        return self.x
        
    def getY(self):
        return self.y
    
    def getElevation(self):
        return self.elevation
    
    def getAzimuth(self):
        return self.azimuth
        
def coliImageTest():
    test_light = Light(300, 300, 4500, 0.5, 250)
    COLI_IP = "127.0.0.1"
    coli_controller = xmlrpclib.ServerProxy("http://" + COLI_IP + ":8002")
    test_light.takeCollimation(coli_controller)
    
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

def savePicture(tracked_lights, im_str):
    captures_folder = 'captures'
    timestamp = datetime.utcnow()
    current_capture_folder = ("%s" % timestamp).replace(':','-')
    folder = os.path.join(captures_folder, current_capture_folder)
    os.makedirs(folder)
    
    im_str = str(im_str)
    im = np.fromstring(im_str, dtype = np.uint8).reshape((480, 640, 3))

    # Show all detected lights
    for detectedLight in tracked_lights:
        if detectedLight["area"] >= 7:
            color = (randint(100, 255), randint(100, 255), randint(100, 255))
            cv2.circle(im, (detectedLight["x"], detectedLight["y"]), 15, color, 3)

    # Draw colimation point
    cv2.circle(im, (316, 235), 5, (0, 0, 255), 3)
    cv2.imwrite(os.path.join(folder, "busca.png"), im)
    
def background(azimuth_controller, elevation_controller, lights_controller, coli, spectrometer, azimuthRange, elevationRange):
    positions = Positions(len(azimuthRange), len(elevationRange))
    elevationID = 0
    azimuthID = 0
    for elevation in elevationRange:
        for angle in azimuthRange:
            print "Moving to Next Position"
            elevation_controller.move_to(elevation)
            azimuth_controller.move_to(angle)
            print "@ elevation %f & azimuth %d" % (elevation_controller.position(), azimuth_controller.position())
            time.sleep(0.2)
            newPosition = Position(elevation_controller.position(), azimuth_controller.position(), elevationID, azimuthID)
            print "Position Created"
            newPosition.findLights(lights_controller)
            newPosition.printAbsPositions()
            newPosition.visitLights(elevation_controller, azimuth_controller, coli)
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

#busca = Busca(ErrorController(azimuth_controller, elevation_controller))
coli = Coli(coli_controller, azimuth_controller, elevation_controller)

elevation_range = [ 0.674929, 0.669685, 0.5, 0.000300]
azimuth_range = [16967, 0, 2400, 4800, 7200, 9600, 12000, 14400, 16800]

background(azimuth_controller, elevation_controller, lights_controller, coli_controller, spectrometer, azimuth_range, elevation_range)
#scan(azimuth_controller, elevation_controller, lights_controller, busca, coli, spectrometer, elevation_steps = 4)
