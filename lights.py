import cv2
import uuid
import numpy as np
import math

class Light:
    def __init__(self, x, y, area):
        self.x = x
        self.y = y
        self.area = area

class LightDetector:
    MIN_BRIGHTNESS_THRESHOLD = 87
    MIN_LIGHT_AREA = 2

    def detect(self, im):
        gray_im = cv2.cvtColor(im, cv2.COLOR_BGR2GRAY)
    
        _, gray_im = cv2.threshold(gray_im, self.MIN_BRIGHTNESS_THRESHOLD, 255, cv2.THRESH_BINARY)
        contours, _ = cv2.findContours(gray_im.copy(), cv2.RETR_LIST, cv2.CHAIN_APPROX_NONE)
        lights = []
        for contour in contours:
            area = len(contour)
            if area >= self.MIN_LIGHT_AREA:
                x = []
                y = []
                for point in contour:
                    x.append(point[0][0])
                    y.append(point[0][1])
                x = np.int32(np.mean(x)).item()
                y = np.int32(np.mean(y)).item()

                lights.append(Light(x, y, area))

        return lights

class LightTracker:
    MAX_DISPLACEMENT = 30

    def __init__(self):
        self.old_lights = []
        self.guids = {}

    def track(self, new_lights):
        updated_guids = {}
        updated_lights = []
        matched_new_lights = {}

        # Add tracked lights
        for old_light in self.old_lights:
            best_match = None
            for new_light in new_lights:
                d = (new_light.x - old_light.x)**2 + (new_light.y - new_light.y)**2
                if best_match == None or d < best_match[0]:
                    best_match = [d, new_light]

            if best_match == None or math.sqrt(best_match[0]) / self.MAX_DISPLACEMENT >= 1.0:
                continue

            new_light = best_match[1]
            guid = self.guids[old_light]
            updated_guids[new_light] = guid
            updated_lights.append(new_light)
            matched_new_lights.append(new_light)

        # Add new lights
        unmatched_new_lights = set(new_lights) - matched_new_lights
        for unmatched_new_light in unmatched_new_lights:
            guid = str(uuid.uuid4())
            updated_guids[new_light] = guid
            updated_lights.append(new_light)

        self.guids = updated_guids
        self.old_lights = updated_lights

    def state(self):
        return [{"guid": self.guids[light], "light": light} for light in self.guids]
