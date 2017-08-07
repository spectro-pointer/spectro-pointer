from picamera.array import PiRGBArray
from picamera import PiCamera
from fractions import Fraction
from time import sleep

class Camera:
    SIZE = (640, 480)

    def __init__(self, fps):
        camera = PiCamera(resolution=self.SIZE, framerate=Fraction(fps, 1))
        camera.shutter_speed = 1000000 / fps
        camera.iso = 800
        sleep(2)
        camera.exposure_mode = 'off'
        camera.awb_mode = 'off'
        camera.awb_gains = (Fraction(299, 256), Fraction(49, 32))

        self.camera = camera
        self.stream = PiRGBArray(self.camera, size = self.SIZE)

    def capture_frame(self):
        self.stream.seek(0)
        self.stream.truncate()

        self.camera.capture(self.stream, format = 'bgr', use_video_port = True)

        return self.stream.array
