import RPi.GPIO as GPIO
from stepper import Stepper
from SimpleXMLRPCServer import SimpleXMLRPCServer

class AzimuthController:
    DIRECTION_GPIO = 38
    PULSE_GPIO = 40
    HOME_GPIO = 22
    MICROSTEPS = 400
    GEAR_RATIO = 48
    HOMING_DIRECTION = True

    def __init__(self):
        GPIO.setup(self.HOME_GPIO, GPIO.IN, pull_up_down = GPIO.PUD_UP)
        self.__stepper = Stepper(self.MICROSTEPS * self.GEAR_RATIO, self.DIRECTION_GPIO, self.PULSE_GPIO)

        steps = 0
        while self.is_home():
            self.__stepper.pulse(self.HOMING_DIRECTION)
            steps += 1
            if (steps > self.total_steps()):
                raise ValueError("Cannot home the azimuth stepper. It is likely not moving or the sensor is broken.")
        while not self.is_home():
            self.__stepper.pulse(self.HOMING_DIRECTION)
            steps += 1
            if (steps > self.total_steps()):
                raise ValueError("Cannot home the azimuth stepper. It is likely not moving or the sensor is broken.")
        self.__stepper.reset_position()

    def is_home(self):
        return not GPIO.input(self.HOME_GPIO)

    def position(self):
        return self.__stepper.position()

    def total_steps(self):
        return self.__stepper.total_steps()

    def move(self, direction, steps):
        self.__stepper.move(direction, steps)
        return True

    def move_to(self, steps):
        while self.position() != steps:
            self.move(self, self.HOMING_DIRECTION, 1)
        return True

# Initialization
GPIO.setmode(GPIO.BOARD)
GPIO.setwarnings(False)

print 'Initializing and homing the azimuth controller...'
controller = AzimuthController()

print 'Initializing the XML-RPC server...'
server = SimpleXMLRPCServer(("0.0.0.0", 8000))
server.register_instance(controller)

print 'Waiting for incoming requests...'

server.serve_forever()
