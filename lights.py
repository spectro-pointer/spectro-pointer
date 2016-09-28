import cv2

class Light:
    def __init__(self, x, y, area):
        self.x = x
        self.y = y
        self.area = area

class LightDetector:
    MIN_BRIGHTNESS_THRESHOLD = 130
    MIN_LIGHT_AREA = 3

    def detect(self, im):
        gray_im = cv2.cvtColor(im, cv2.COLOR_BGR2GRAY)
    
        _, gray_im = cv2.threshold(gray_im, self.MIN_BRIGHTNESS_THRESHOLD, 255, cv2.THRESH_BINARY)
        contours, _ = cv2.findContours(gray_im.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
        lights = []

        for contour in contours:
            m = cv2.moments(contour)
            area = m["m00"]
            if area >= self.MIN_LIGHT_AREA:
                x = int(m["m10"] / m["m00"])
                y = int(m["m01"] / m["m00"])
                lights.append(Light(x, y, area))

        return lights

class LightTracker:
    MAX_DISPLACEMENT = 25
    MAX_RESIZING_FACTOR = 2.0
    DISPLACEMENT_WEIGHT = 0.8
    RESIZING_FACTOR_WEIGHT = 1.0 - DISPLACEMENT_WEIGHT

    def __init__(self):
        self.old_lights = []
        self.dictionary = {}

    def track(self, new_lights):
        remaining_old_lights = list(self.old_lights)
        for new_light in new_lights:
            distances = [(LightTracker.distance(new_light, old_light), old_light) for old_light in remaining_old_lights]
            distances.sort(key = lambda t: t[0])
            if len(distances) > 0 and distances[0][0] < 1.0:
                match = distances[0]
                old_light = match[1]
                remaining_old_lights.remove(old_light)
                value = self.dictionary.pop(old_light, None)
            else:
                value = None
            self.dictionary[new_light] = value

        for old_light in self.old_lights:
            self.dictionary.pop(old_light, None)

        self.old_lights = new_lights

    def get(self, light):
        self.raise_if_light_not_valid(light)
        return self.dictionary.get(light)

    def set(self, light, value):
        self.raise_if_light_not_valid(light)
        self.set_if_present(light, value)

    def set_if_present(self, light, value):
        if light not in self.old_lights
            return False

        self.dictionary[light] = value
        return True

    def raise_if_light_not_valid(self, light):
        if light not in self.old_lights:
            raise ValueError("The given light is not being tracked")

    @staticmethod
    def distance(light1, light2):
        displacement = cv2.norm((light1.x, light1.y), (light2.x, light2.y))
        displacement_ratio = displacement / LightTracker.MAX_DISPLACEMENT

        resizing_factor = abs(float(light2.area - light1.area) / light1.area)
        resizing_factor_ratio = resizing_factor / LightTracker.MAX_RESIZING_FACTOR

        if displacement_ratio > 1.0 or resizing_factor_ratio > 1.0:
            return 1.0

        return LightTracker.DISPLACEMENT_WEIGHT * displacement_ratio + LightTracker.RESIZING_FACTOR_WEIGHT * resizing_factor_ratio
