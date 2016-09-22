import sys
import RPi.GPIO as GPIO
from stepper import Stepper
from SimpleXMLRPCServer import SimpleXMLRPCServer

class ElevationController:
    DIRECTION_GPIO = 36
    PULSE_GPIO = 32
    # There are ~150 degrees between the two home sensors
    HOME_DOWN_GPIO = 24
    HOME_UP_GPIO = 26
    MICROSTEPS = 400
    GEAR_RATIO = 48
    DOWN_DIRECTION = True
    UP_DIRECTION = not DOWN_DIRECTION

    def __init__(self):
        GPIO.setup(self.HOME_DOWN_GPIO, GPIO.IN, pull_up_down = GPIO.PUD_UP)
        GPIO.setup(self.HOME_UP_GPIO, GPIO.IN, pull_up_down = GPIO.PUD_UP)
        self.__stepper = Stepper(self.MICROSTEPS * self.GEAR_RATIO, self.DIRECTION_GPIO, self.PULSE_GPIO)

        steps = 0
        while self.is_home_down():
            self.__stepper.pulse(self.UP_DIRECTION)
            steps += 1
            if (steps > self.__stepper.total_steps()):
                raise ValueError("Cannot home the elevation stepper. It is likely not moving or the sensor is broken.")
        while not self.is_home_down():
            self.__stepper.pulse(self.DOWN_DIRECTION)
            steps += 1
            if (steps > self.__stepper.total_steps()):
                raise ValueError("Cannot home the elevation stepper. It is likely not moving or the sensor is broken.")

        steps = 0
        self.__amplitude = 0
        while not self.is_home_up():
            self.__stepper.pulse(self.UP_DIRECTION)
            steps += 1
            self.__amplitude += 1
            if (steps > self.__stepper.total_steps()):
                raise ValueError("Cannot home the elevation stepper. It is likely not moving or the sensor is broken.")
        self.__stepper.reset_position()

    def is_home(self):
        return self.is_home_down() or self.is_home_up()

    def is_home_down(self):
        return not GPIO.input(self.HOME_DOWN_GPIO)

    def is_home_up(self):
        return not GPIO.input(self.HOME_UP_GPIO)

    def position(self):
        position = float(self.__stepper.position()) / self.amplitude()
        if position < 0 or position > 1:
            raise ValueError("Invalid position about to be returned: " + position)
        return position

    def amplitude(self):
        return self.__amplitude

    def move_to(self, percentage_amplitude, max_delta = sys.maxint):
        if percentage_amplitude < 0 or percentage_amplitude > 1:
            raise ValueError("Percentage of amplitude must be between 0 and 1: " + str(percentage_amplitude))
        delta = int((percentage_amplitude - self.position()) * self.amplitude())
        direction = self.UP_DIRECTION if delta < 0 else self.DOWN_DIRECTION
        self.__stepper.move(direction, min(abs(delta), max_delta))
        return abs(delta) <= max_delta

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
