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
        while self.is_home_up():
            self.__stepper.pulse(self.DOWN_DIRECTION)
            steps += 1
            if (steps > self.total_steps()):
                raise ValueError("Cannot home the elevation stepper. It is likely not moving or the sensor is broken.")
        while not self.is_home_up():
            self.__stepper.pulse(self.UP_DIRECTION)
            steps += 1
            if (steps > self.total_steps()):
                raise ValueError("Cannot home the elevation stepper. It is likely not moving or the sensor is broken.")
        self.__stepper.reset_position()

        steps = 0
        self.amplitude = 0
        while not self.is_home_down():
            self.__stepper.pulse(self.DOWN_DIRECTION)
            steps += 1
            self.amplitude += 1
            if (steps > self.total_steps()):
                raise ValueError("Cannot home the elevation stepper. It is likely not moving or the sensor is broken.")

    def is_home(self):
        return self.is_home_down() or self.is_home_up()

    def is_home_down(self):
        return not GPIO.input(self.HOME_DOWN_GPIO)

    def is_home_up(self):
        return not GPIO.input(self.HOME_UP_GPIO)

    def position(self):
        return self.__stepper.position()

    def total_steps(self):
        return self.__stepper.total_steps()

    def move(self, direction, steps):
        self.__stepper.move(direction, steps)
        return True

# Initialization
GPIO.setmode(GPIO.BOARD)
GPIO.setwarnings(False)

print 'Initializing and homing the elevation controller...'
controller = ElevationController()

print 'Initializing the XML-RPC server...'
server = SimpleXMLRPCServer(("0.0.0.0", 8002))
server.register_instance(controller)

print 'Waiting for incoming requests...'

server.serve_forever()
