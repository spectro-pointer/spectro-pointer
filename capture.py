import cv2
import xmlrpclib

class LightDetector:
  MIN_BRIGHTNESS_THRESHOLD = 150
  MIN_LIGHT_AREA = 150
  MAX_LIGHT_AREA = 5000

  def detect(self, frame):
    gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    
    _, gray_frame = cv2.threshold(gray_frame, self.MIN_BRIGHTNESS_THRESHOLD, 255, cv2.THRESH_BINARY)
    contours, _ = cv2.findContours(gray_frame.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    lights = []

    for contour in contours:
      m = cv2.moments(contour)
      area = m["m00"]
      if (area >= self.MIN_LIGHT_AREA and area <= self.MAX_LIGHT_AREA):
        x = int(m["m10"] / m["m00"])
        y = int(m["m01"] / m["m00"])
        lights.append({"x": x, "y": y, "area": area, "contour": contour})

    return lights


camera = cv2.VideoCapture(0)
camera.set(3, 640)
camera.set(4, 480)
detector = LightDetector()
s = xmlrpclib.ServerProxy('http://192.168.0.100:8000', allow_none = True)
print "Position: " + str(s.position())

while True:
  _, im = camera.read()

  lights = detector.detect(im)

  cv2.drawContours(im, [light["contour"] for light in lights], -1, (0, 255, 0))
  for light in lights:
    cv2.circle(im, (light["x"], light["y"]), 15, (0, 0, 255))

  if len(lights) == 1:
    if lights[0]["x"] < 320:
      print "Light is on the left"
      s.move(True, 50)
    else:
      print "Light is on the right"
      s.move(False, 50)

  print "New position: " + str(s.position())

  cv2.imshow("live", im)
  cv2.waitKey(500)
