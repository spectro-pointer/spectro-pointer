from picamera.array import PiRGBArray
from picamera import PiCamera

class Camera:
    SIZE = (640, 480)

    def __init__(self):
        self.camera = PiCamera()
        self.camera.resolution = self.SIZE
        self.stream = PiRGBArray(self.camera, size = self.SIZE)

    def capture_frame(self):
        self.stream.seek(0)
        self.stream.truncate()

        self.camera.capture(self.stream, format = 'bgr', use_video_port = True)

        return self.stream.array
