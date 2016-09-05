import cv2

class LightDetector:
    MIN_BRIGHTNESS_THRESHOLD = 150
    MIN_LIGHT_AREA = 15

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
                lights.append({"x": x, "y": y, "area": area, "contour": contour})

        return lights
