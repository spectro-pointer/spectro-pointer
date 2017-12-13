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
import detector_spectroscope
import threading
import Queue
import csv


class Positions:
    'A collection of positions. A position will store the collection of lights found at one position'

    def __init__(self, numAzimuthPositions, numElevationPositions):
        self.numAzimuthPositions = numAzimuthPositions
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
        self.folder_name = os.path.join('captures', ("%s" % datetime.utcnow()).replace(':', '-'))
    

    def findLights(self, lightsController):
        print "Capturing Lights & Saving Picture..."
        detectedLights, im = lights_controller.get_lights_and_image()
        savePicture(detectedLights, im, self.folder_name, "Lights_Detected")
        self.lights = []
        print detectedLights
        for light in detectedLights:
            newLight = Light(light["x"], light["y"], self.azimuth, self.elevation, light["area"], self.folder_name)
            self.lights.append(newLight)
        print "Saving Light Positions..."
        self.saveLightPositions()
            
    def saveLightPositions(self):
        light_position_file = self.folder_name
        light_position_file = os.path.join(light_position_file, ("%s" % datetime.utcnow()).replace(':', '-') + '_Light_Positions.csv')
        with open(light_position_file, 'wb') as csvFile:
            lightWriter = csv.writer(csvFile, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)
            lightWriter.writerow(['X-Position', 'Y-Position', 'Elevation', 'Azimuth', 'Area'])
            for light in self.lights:
                lightWriter.writerow([str(light.getX()), str(light.getY()), str(light.getElevation()), str(light.getAzimuth()), light.getArea()])
            
    def getAzimuth(self):
        return self.azimuth

    def getElevation(self):
        return self.elevation

    def getAzimuthID(self):
        return self.azimuthID

    def getElevationID(self):
        return self.elevationID

    def visitLights(self, elevation_controller, azimuth_controller, coli_controller, spectrometer):
        'Visit the each detected light in the current position'
        for light in self.lights:
            print "visiting light at Elevation: " + str(light.getElevation()) + " Azimuth: " + str(light.getAzimuth())
            light.center(elevation_controller, azimuth_controller)
            # detector_spectroscope.sta
            light.collimation(coli_controller, elevation_controller, azimuth_controller, spectrometer);

    def printAbsPositions(self):
        'Print the absolute position of this position'
        for light in self.lights:
            print "Light Position: Elevation: " + str(light.getElevation()) + " Azimuth: " + str(light.getAzimuth())

    def printLights(self):
        'Print each light and position'
        for light in self.lights:
            print "Light Position: X: " + str(light.getX()) + " Y: " + str(light.getY())


class Light:
    'Light - Detected light in the current position'

    def __init__(self, x, y, position_azimuth, position_elevation, area, captures_folder):
        self.x = x
        self.y = y
        self.area = area
        azi_ele = centrador.pixel2Absolute(x, y, position_azimuth, position_elevation)
        self.azimuth = azi_ele[0]
        self.elevation = azi_ele[1]
        self.captures_folder = os.path.join(captures_folder, ("%s" % datetime.utcnow()).replace(':', '-') + "_Individual_Lights")

    def getArea(self):
        return self.area
    
    def setAbsolutePosition(self, azimuth, elevation):
        'Set absolute position of this light'
        self.azimuth = azimuth
        self.elevation = elevation

    def center(self, elevation_controller, azimuth_controller):
        'Center the camera on this light'
        elevation_controller.move_to(self.elevation)
        azimuth_controller.move_to(self.azimuth)
        print "light at:\nElevation: " + str(self.elevation) + " Azimuth: " + str(self.azimuth) + " Visited."

    def collimation(self, coli_controller, elevation_controller, azimuth_controller, spectrometer):
        'Uses fine motor control to center the motor on the detected light'
        centered = False
        undetectedCounter = 0
        totalCounter = 0
        MAX_LOOPS = 20
        UNDETECTED = 100
        while not centered:
            im_str = str(coli_controller.get_image())
            im = np.fromstring(im_str, dtype=np.uint8).reshape((387 - 100, 443 - 185, 3))
            cx, cy = getContour(im)
            offset = check_quadrant(cx, cy)
            if (offset == ''):
                print "No Light Detected"
                undetectedCounter += 1
                if (undetectedCounter > UNDETECTED):
                    print "Reached Undetected Threshold"
                    break
            elif (offset.find("x-center") != -1 or offset.find("y-center") != -1):
                print 'running parallel'
                spectrum, wavelengths = self.runCollimationAndTakeSpectrum(coli_controller, elevation_controller, azimuth_controller, spectrometer)
                print 'finished parallel'
                centered = True

            if (offset.find("left") != -1):
                print "Move Left"
                azimuth_controller.move_left(1)
            elif (offset.find("right") != -1):
                print "Move Right"
                azimuth_controller.move_right(1)
            if (offset.find("up") != -1):
                print "Move Up"
                elevation_controller.move_to(elevation_controller.position() - 0.00015)
            elif (offset.find("down") != -1):
                print "Move Down"
                elevation_controller.move_to(elevation_controller.position() + 0.00015)
            if (totalCounter > MAX_LOOPS):
                print 'Reached Maximum Number of Loops: ' + str(MAX_LOOPS)
                spectrum, wavelengths = self.runCollimationAndTakeSpectrum(coli_controller, elevation_controller, azimuth_controller, spectrometer)
                break
            totalCounter += 1

        print "Finished Collimation"

    def getX(self):
        return self.x

    def getY(self):
        return self.y

    def getElevation(self):
        return self.elevation

    def getAzimuth(self):
        return self.azimuth

    
    
    def runCollimationAndTakeSpectrum(self, coli_controller, elevation_controller, azimuth_controller, spectrometer):
        success = False
        thresh = 50000
        integration_time = 1 #seconds
        factor = 1.5
        saturation = 60000
        while(not success):
            e = threading.Event()
            queue = Queue.Queue()
            t1 = threading.Thread(target=noSpectrumCollimation,
                                  args=(coli_controller, elevation_controller, azimuth_controller, spectrometer, e))
            t2 = threading.Thread(target=takeSpectrometer, args=(spectrometer, e, queue, integration_time))
            t1.start()
            t2.start()
            t1.join()
            t2.join()
            spectrum = queue.get()
            wavelengths = queue.get()
            self.saveSpectrometer(spectrum, wavelengths)
            correct = correctIntegrationTime(spectrum, saturation, thresh)
            if(correct == 'Saturated'):
                integration_time = integration_time / factor
            elif(correct == 'Above Threshold'):
                success = True
            elif(correct == 'Below Threshold'):
                integration_time = integration_time * factor
        return spectrum, wavelengths
    
    def saveSpectrometer(self, spectrum, wavelengths):
        timestamp = datetime.utcnow()
        current_capture_folder = ("%s" % timestamp).replace(':', '-') 
        folder = os.path.join(self.captures_folder, current_capture_folder)
        os.makedirs(folder)
        plt.plot(wavelengths, spectrum)
        plt.xlim(wavelengths[0], wavelengths[len(wavelengths) - 1])
        plt.ylim(0, 2 ** 16)
        plt.ylabel('Intensity')
        plt.xlabel('Wavelength')
        plt.savefig(os.path.join(folder, "spectrum.png"), bbox_inches='tight')
        plt.close()
        with open(os.path.join(folder, "spectrum.txt"), "w") as text_file:
            for i in range(len(wavelengths)):
                text_file.write("%f %f\n" % (wavelengths[i], spectrum[i]))
        detectedLights, im = lights_controller.get_lights_and_image()
        savePicture(detectedLights, im, folder, "Coli_Capture")
        
def correctIntegrationTime(spectrum, saturation, threshold):
        MIN = min(spectrum)
        #       MEAN = sum(spectrum)/len(spectrum)
        # Saturation detection
        MAX = max(spectrum)
        if MAX >= saturation:
            #            self._integration_time *= self._integration_factor
            #            print 'Saturation: %d. Lowering integration time: %f' % (MAX, self._integration_time)
            #            self._spectrometer.set_integration(self._integration_time*1e6)
            return 'Saturated'
        # Baseline reduction
        spectrum = [v - MIN for v in spectrum]
        # Detection
        MAX -= MIN
        if MAX > threshold:  # Detection
            #            # Save spectrum
            #            print 'Detection: %d' % MAX
            #            self._save_spectrum(self._location, spectrum)
            #            if(fig != 0):
            #                close()
            #            fig = self._plot_spectrum(spectrum)
            #            numCaptures += 1
            #            if numCaptures > MAX_NUMCAPTURES:
            #                print 'Stop!!!'
            #                self.stop()
            return 'Above Threshold'
        else:
            #            # Increase integration time
            #            self._integration_time /= self._integration_factor
            #            if self._integration_time > self.MAX_INTEGRATION_TIME:
            #                self._integration_time = self.MAX_INTEGRATION_TIME
            #            print 'No detection: %d. Integration time: %f' % (MAX, self._integration_time)
            #            self._spectrometer.set_integration(self._integration_time*1e6)
            return 'Below Threshold'
        
def noSpectrumCollimation(coli_controller, elevation_controller, azimuth_controller, spectrometer, e):
    'Uses fine motor control to center the motor on the detected light'
    centered = False
    undetectedCounter = 0
    totalCounter = 0
    MAX_LOOPS = 1600
    notifierEvent = threading.Event()
    while not e.isSet():
        im_str = str(coli_controller.get_image())
        im = np.fromstring(im_str, dtype=np.uint8).reshape((387 - 100, 443 - 185, 3))
        cx, cy = getContour(im)
        offset = check_quadrant(cx, cy)
        if (offset == ''):
            print "No Light Detected"
            undetectedCounter += 1
            if (undetectedCounter > 20):
                print "Reached Undetected Threshold"
                break
        elif (offset.find("x-center") != -1 or offset.find("y-center") != -1):
            print 'Centered?: ' + str(centered)

        if (offset.find("left") != -1):
            print "Move Left"
            azimuth_controller.move_left(1)

        elif (offset.find("right") != -1):
            print "Move Right"
            azimuth_controller.move_right(1)

        if (offset.find("up") != -1):
            print "Move Up"
            elevation_controller.move_to(elevation_controller.position() - 0.00015)

        elif (offset.find("down") != -1):
            print "Move Down"
            elevation_controller.move_to(elevation_controller.position() + 0.00015)

        if (totalCounter > MAX_LOOPS):
            print 'Reached Maximum Number of Loops: ' + MAX_LOOPS
            break
        totalCounter += 1
    print "Finished Parallel Collimation"

def takeSpectrometer(spectrometer, e, queue, integration_time):
    print "  Capturing spectrum..."
    spectrometer.set_integration(integration_time * 1e6)
    wavelengths = spectrometer.get_wavelengths()
    wavelengths = [float(v) for v in wavelengths.split()]
    spectrum = spectrometer.get_spectrum()
    spectrum = [float(v) for v in spectrum.split()]
    e.set()
    queue.put(spectrum)
    queue.put(wavelengths)
    return spectrum, wavelengths
    
def savePicture(tracked_lights, im_str, folder_name, picture_name):
    captures_folder = folder_name
    timestamp = datetime.utcnow()
    current_capture_folder = ("%s" % timestamp).replace(':', '-') + picture_name
    folder = os.path.join(captures_folder, current_capture_folder)
    os.makedirs(folder)

    im_str = str(im_str)
    im = np.fromstring(im_str, dtype=np.uint8).reshape((480, 640, 3))

    # Show all detected lights
    for detectedLight in tracked_lights:
        if detectedLight["area"] >= 7:
            color = (randint(100, 255), randint(100, 255), randint(100, 255))
            cv2.circle(im, (detectedLight["x"], detectedLight["y"]), 15, color, 3)

    # Draw colimation point
    cv2.circle(im, (316, 235), 5, (0, 0, 255), 3)
    cv2.imwrite(os.path.join(folder, "busca.png"), im)


def background(azimuth_controller, elevation_controller, lights_controller, coli, spectrometer, azimuthRange,
               elevationRange):
    'Obtain the background images for the sky, detect the lights and take their spectrums'
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
            newPosition = Position(elevation_controller.position(), azimuth_controller.position(), elevationID,
                                   azimuthID)
            print "Position Created"
            newPosition.findLights(lights_controller)
            newPosition.printAbsPositions()
            newPosition.visitLights(elevation_controller, azimuth_controller, coli, spectrometer)
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

# busca = Busca(ErrorController(azimuth_controller, elevation_controller))

elevation_range = [0.674929, 0.669685, 0.5, 0.000300]
azimuth_range = [16967, 0, 2400, 4800, 7200, 9600, 12000, 14400, 16800]

background(azimuth_controller, elevation_controller, lights_controller, coli_controller, spectrometer, azimuth_range,
           elevation_range)
# scan(azimuth_controller, elevation_controller, lights_controller, busca, coli, spectrometer, elevation_steps = 4)
