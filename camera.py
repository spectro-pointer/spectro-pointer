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

        self._camera = camera
        self._stream = PiRGBArray(self._camera, size = self.SIZE)

    def stream(self):
        self._stream.truncate(0)
        return self._stream

    def capture_sequence(self, callback):
        self._camera.capture_sequence(callback(), format = 'bgr', use_video_port = True)
