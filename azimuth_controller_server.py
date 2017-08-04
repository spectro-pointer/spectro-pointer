import sys
import RPi.GPIO as GPIO
from stepper import Stepper
from SimpleXMLRPCServer import SimpleXMLRPCServer

class AzimuthController:
    DIRECTION_GPIO = 38
    PULSE_GPIO = 40
    HOME_GPIO = 22
    MICROSTEPS = 400
    GEAR_RATIO = 48
    LEFT_DIRECTION = True
    RIGHT_DIRECTION = not LEFT_DIRECTION
    HOMING_DIRECTION = LEFT_DIRECTION
    BACKLASH_STEPS = 24

    def __init__(self):
        GPIO.setup(self.HOME_GPIO, GPIO.IN, pull_up_down = GPIO.PUD_UP)
        self.__stepper = Stepper(self.MICROSTEPS * self.GEAR_RATIO, self.DIRECTION_GPIO, self.PULSE_GPIO, self.BACKLASH_STEPS)

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

    def move_left(self, steps):
        return self.move(self.LEFT_DIRECTION, steps)

    def move_right(self, steps):
        return self.move(self.RIGHT_DIRECTION, steps)

    def move(self, direction, steps):
        self.__stepper.move(direction, steps)
        return True

    def move_to(self, position, max_steps = sys.maxint):
        if position < 0 or position >= self.total_steps():
            raise ValueError("Invalid position")

        steps_from_left = (position - self.position()) % self.total_steps()
        steps_from_right = (self.position() - position) % self.total_steps()

        if steps_from_left <= steps_from_right:
            self.move(self.LEFT_DIRECTION, min(steps_from_left, max_steps))
            return steps_from_left <= max_steps
        else:
            self.move(self.RIGHT_DIRECTION, min(steps_from_right, max_steps))
            return steps_from_right <= max_steps

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
