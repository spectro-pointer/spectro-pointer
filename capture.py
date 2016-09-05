import cv2
import xmlrpclib
import time

from picamera.array import PiRGBArray
from picamera import PiCamera

class LightDetector:
  MIN_BRIGHTNESS_THRESHOLD = 150
  MIN_LIGHT_AREA = 150

  def detect(self, frame):
    gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    
    _, gray_frame = cv2.threshold(gray_frame, self.MIN_BRIGHTNESS_THRESHOLD, 255, cv2.THRESH_BINARY)
    contours, _ = cv2.findContours(gray_frame.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    lights = []

    for contour in contours:
      m = cv2.moments(contour)
      area = m["m00"]
      if area >= self.MIN_LIGHT_AREA:
        x = int(m["m10"] / m["m00"])
        y = int(m["m01"] / m["m00"])
        lights.append({"x": x, "y": y, "area": area, "contour": contour})

    return lights

def capture_frame(camera, stream):
    """
    Captures Current Frame
    This function should be called inside a loop.
    :returns: frame"""
    stream.seek(0)
    stream.truncate()
    frame = None
    try:
        camera.capture(stream, format='bgr', use_video_port=True)
        frame = stream.array
    except:
        print "Error with camera.capture"
    return frame

SIZE = (640, 480)

camera = PiCamera()
camera.resolution = SIZE
stream = PiRGBArray(camera, size=SIZE)
time.sleep(0.1)  # allow the camera to warmup

detector = LightDetector()
s = xmlrpclib.ServerProxy('http://192.168.0.100:8000', allow_none = True)
print "Position: " + str(s.position())

while True:
  im = capture_frame(camera, stream)
  lights = detector.detect(im)

  cv2.drawContours(im, [light["contour"] for light in lights], -1, (0, 255, 0))
  for light in lights:
    cv2.circle(im, (light["x"], light["y"]), 15, (0, 0, 255))

  if len(lights) == 1:
    x = lights[0]["x"]
    e = x - 320

    if (abs(e) < 10):
      steps = 5
    elif (abs(e) < 15):
      steps = 10
    elif (abs(e) < 20):
      steps = 20
    elif (abs(e) < 50):
      steps = 50
    elif (abs(e) < 100):
      steps = 100
    else:
      steps = 500

    if e < -3:
      print "Light is on the left @ " + str(x) + " & error = " + str(e)
      s.move(True, steps)
      print "New position: " + str(s.position()) + ", moved by " + str(steps) + " steps"
    elif e > 3:
      print "Light is on the right @ " + str(x) + " & error = " + str(e)
      s.move(False, steps)
      print "New position: " + str(s.position()) + ", moved by " + str(steps) + " steps"
    else:
      print "Light is centered! @ " + str(x) + " & error = " + str(e)

  cv2.imshow("live", im)
  cv2.waitKey(100)
