import RPi.GPIO as GPIO
from stepper import Stepper
from SimpleXMLRPCServer import SimpleXMLRPCServer

class ElevationController:
    DIRECTION_GPIO = 36
    PULSE_GPIO = 32
    HOME1_GPIO = 24
    HOME2_GPIO = 26
    MICROSTEPS = 400
    GEAR_RATIO = 48
    HOMING_DIRECTION = True

    def __init__(self):
        GPIO.setup(self.HOME1_GPIO, GPIO.IN, pull_up_down = GPIO.PUD_UP)
        GPIO.setup(self.HOME2_GPIO, GPIO.IN, pull_up_down = GPIO.PUD_UP)
        self.__stepper = Stepper(self.MICROSTEPS * self.GEAR_RATIO, self.DIRECTION_GPIO, self.PULSE_GPIO)

        steps = 0
        while self.is_home():
            self.__stepper.pulse(self.HOMING_DIRECTION)
            steps += 1
            if (steps > self.total_steps()):
                raise ValueError("Cannot home the elevation stepper. It is likely not moving or the sensor is broken.")
        while not self.is_home():
            self.__stepper.pulse(self.HOMING_DIRECTION)
            steps += 1
            if (steps > self.total_steps()):
                raise ValueError("Cannot home the elevation stepper. It is likely not moving or the sensor is broken.")
        self.__stepper.reset_position()

    def is_home(self):
        return self.is_home1() or self.is_home2()

    def is_home1(self):
        return not GPIO.input(self.HOME1_GPIO)

    def is_home2(self):
        return not GPIO.input(self.HOME2_GPIO)

    def position(self):
        return self.__stepper.position()

    def total_steps(self):
        return self.__stepper.total_steps()

    def move(self, direction, steps):
        self.__stepper.move(direction, steps)

# Initialization
GPIO.setmode(GPIO.BOARD)
GPIO.setwarnings(False)

print 'Initializing and homing the elevation controller...'
controller = ElevationController()

print 'Initializing the XML-RPC server...'
server = SimpleXMLRPCServer(("0.0.0.0", 8001))
server.register_instance(controller)

print 'Waiting for incoming requests...'

server.serve_forever()
