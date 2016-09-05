import RPi.GPIO as GPIO
from stepper import Stepper
from SimpleXMLRPCServer import SimpleXMLRPCServer

class AzimuthController:
    AZIMUTH_DIRECTION_GPIO = 38
    AZIMUTH_PULSE_GPIO = 40
    AZIMUTH_HOME_GPIO = 22
    AZIMUTH_MICROSTEPS = 400
    AZIMUTH_GEAR_RATIO = 48
    AZIMUTH_HOMING_DIRECTION = True

    def __init__(self):
        GPIO.setup(self.AZIMUTH_HOME_GPIO, GPIO.IN, pull_up_down = GPIO.PUD_UP)
        self.__stepper = Stepper(self.AZIMUTH_MICROSTEPS * self.AZIMUTH_GEAR_RATIO, self.AZIMUTH_DIRECTION_GPIO, self.AZIMUTH_PULSE_GPIO)

        steps = 0
        while self.is_home():
            self.__stepper.pulse(self.AZIMUTH_HOMING_DIRECTION)
            steps += 1
            if (steps > self.total_steps()):
                raise ValueError("Cannot home the azimuth stepper. It is likely not moving or the sensor is broken.")
        while not self.is_home():
            self.__stepper.pulse(self.AZIMUTH_HOMING_DIRECTION)
            steps += 1
            if (steps > self.total_steps()):
                raise ValueError("Cannot home the azimuth stepper. It is likely not moving or the sensor is broken.")
        self.__stepper.reset_position()

    def is_home(self):
        return not GPIO.input(self.AZIMUTH_HOME_GPIO)

    def position(self):
        return self.__stepper.position()

    def total_steps(self):
        return self.__stepper.total_steps()

    def move(self, direction, steps):
        self.__stepper.move(direction, steps)

# Initialization
GPIO.setmode(GPIO.BOARD)
GPIO.setwarnings(False)

print 'Initializing and homing the azimuth controller...'
azimuth_controller = AzimuthController()

print 'Initializing the XML-RPC server...'
server = SimpleXMLRPCServer(("0.0.0.0", 8000))
server.register_instance(azimuth_controller)

print 'Waiting for incoming requests...'

server.serve_forever()
