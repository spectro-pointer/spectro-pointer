import cv2
import xmlrpclib
import time
import rpyc
import os
import numpy as np
import matplotlib.pyplot as plt
from random import randint
from datetime import datetime

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
            print "  The tracked light disappeared"
            return False, False

        print "Tracking light %s at %d, %d" % (tracked_light["guid"], tracked_light["light"]["x"], tracked_light["light"]["y"])

        if not self.error_controller.center(tracked_light["light"]["x"], tracked_light["light"]["y"]):
            return True, False

        print "Centered on light %s at %d, %d" % (tracked_light["guid"], tracked_light["light"]["x"], tracked_light["light"]["y"])
        light_state = self.state.get(tracked_light["guid"])
        light_state.in_tracking = False
        light_state.tracked = True

        return False, True

class Coli:
    WIDTH = 190
    HEIGHT = 170
    FIBER_X = 75
    FIBER_Y = 77
    DX = 25
    DY = 4
    MIN_INTENSITY_ELEVATION = 30000
    MAX_TRIALS_ELEVATION = 40
    MIN_INTENSITY_AZIMUTH = 10000
    MAX_TRIALS_AZIMUTH = 15

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

def scan(azimuth_controller, elevation_controller, lights_controller, busca, coli, spectrometer, elevation_steps):
    for elevation_step in range(0, elevation_steps):
        if elevation_step != 2:
            continue

        elevation = elevation_step*(1.0 / elevation_steps) + (1.0 / elevation_steps) / 2.0

        # 5200
        azimuth_controller.move_to(17250)

        while True:
            elevation_controller.move_to(elevation)

            print "@ elevation %f & azimuth %d" % (elevation_controller.position(), azimuth_controller.position())

            time.sleep(0.2)
            lights = lights_controller.get_lights()
            if busca.get_new_light_to_track(lights) == None:
                azimuth_controller.move_left(120)
                continue

            while True:
                is_tracking, is_centered = busca.center_tracked_light(lights)
                if not is_tracking:
                    break
                time.sleep(0.2)
                lights = lights_controller.get_lights()

            if is_centered:
                _, im_busca = lights_controller.get_lights_and_image()
                im_busca = str(im_busca)
                im_busca = np.fromstring(im_busca, dtype = np.uint8).reshape((480, 640, 3))
                pos_busca = elevation_controller.position(), azimuth_controller.position()

                print "  Final elevation %f & azimuth %d" % (elevation_controller.position(), azimuth_controller.position())

                time.sleep(1)

                is_colimated, im_coli = coli.colimate()
                if is_colimated:
                    pos_coli = elevation_controller.position(), azimuth_controller.position()
                    print "  Colimation succeeded, final coordinates: elevation %f & azimuth %d" % (elevation_controller.position(), azimuth_controller.position())

                    print "  Capturing spectrum..."
                    wavelengths = spectrometer.get_wavelengths()
                    wavelengths = [float(v) for v in wavelengths.split()]
                    spectrum = spectrometer.get_spectrum()
                    spectrum = [int(v) for v in spectrum.split()]
                    if spectrometer.get_current_status() == 'Success':
                        print "  The spectrum capture succeeded, saving it..."

                        captures_folder = 'captures'
                        timestamp = datetime.utcnow()
                        current_capture_folder = "%s" % timestamp
                        folder = os.path.join(captures_folder, current_capture_folder)
                        os.makedirs(folder)

                        with open(os.path.join(folder, "utc_time.txt"), "w") as text_file:
                            text_file.write("%s" % timestamp)

                        with open(os.path.join(folder, "busca_positions.txt"), "w") as text_file:
                            text_file.write("Elevation: %f Azimuth: %d" % (pos_busca[0], pos_busca[1]))

                        cv2.imwrite(os.path.join(folder, "busca.png"), im_busca)
                        with open(os.path.join(folder, "busca_positions.txt"), "w") as text_file:
                            text_file.write("Elevation: %f Azimuth: %d" % (pos_busca[0], pos_busca[1]))

                        cv2.imwrite(os.path.join(folder, "coli.png"), im_coli)
                        with open(os.path.join(folder, "coli_positions.txt"), "w") as text_file:
                            text_file.write("Elevation: %f Azimuth: %d" % (pos_coli[0], pos_coli[1]))

                        plt.plot(wavelengths, spectrum)
                        plt.xlim(wavelengths[0], wavelengths[len(wavelengths) - 1])
                        plt.ylim(1000, 16500)
                        plt.ylabel('Intensity')
                        plt.xlabel('Wavelength')
                        plt.savefig(os.path.join(folder, "spectrum.png"), bbox_inches='tight')
                        plt.close()

                        with open(os.path.join(folder, "spectrum.txt"), "w") as text_file:
                            for i in range(len(wavelengths)):
                                text_file.write("%f %f\n" % (wavelengths[i], spectrum[i]))
                    else:
                        print "  The spectrum capture failed"
                else:
                    print "  Colimation failed"

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

scan(azimuth_controller, elevation_controller, lights_controller, busca, coli, spectrometer, elevation_steps = 4)
