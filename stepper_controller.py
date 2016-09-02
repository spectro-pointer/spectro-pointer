import RPi.GPIO as GPIO
import time

class Stepper:
    GPIO_SLEEP = 0.25 / 1000.0

    def __init__(self, total_steps, direction_gpio, pulse_gpio):
        self.__total_steps = total_steps
        self.__direction_gpio = direction_gpio
        self.__pulse_gpio = pulse_gpio
        self.__position = 0
        self.__last_direction = True

        GPIO.setup(self.__direction_gpio, GPIO.OUT)
        GPIO.setup(self.__pulse_gpio, GPIO.OUT)

        GPIO.output(self.__direction_gpio, self.__last_direction)
        GPIO.output(self.__pulse_gpio, True)
        time.sleep(self.GPIO_SLEEP)

    def reset_position(self):
        self.__position = 0

    def position(self):
        return self.__position

    def total_steps(self):
        return self.__total_steps

    def move(self, direction, steps):
        for i in range(0, steps):
            self.pulse(direction)

    def pulse(self, direction):
        if (self.__last_direction != direction):
            GPIO.output(self.__direction_gpio, direction)
            time.sleep(self.GPIO_SLEEP)
            self.__last_direction = direction

        GPIO.output(self.__pulse_gpio, False)
        time.sleep(self.GPIO_SLEEP)
        GPIO.output(self.__pulse_gpio, True)
        time.sleep(self.GPIO_SLEEP)

        if direction:
          self.__position += 1
        else:
          self.__position -= 1
        self.__position %= self.__total_steps

class AzimuthStepper:
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
            if (steps > self.__stepper.total_steps()):
                raise ValueError("Cannot home the azimuth stepper. It is likely not moving or the sensor is broken.")
        while not self.is_home():
            self.__stepper.pulse(self.AZIMUTH_HOMING_DIRECTION)
            steps += 1
            if (steps > self.__stepper.total_steps()):
                raise ValueError("Cannot home the azimuth stepper. It is likely not moving or the sensor is broken.")
        self.__stepper.reset_position()

    def is_home(self):
        return not GPIO.input(self.AZIMUTH_HOME_GPIO)

# Initialization
GPIO.setmode(GPIO.BOARD)
GPIO.setwarnings(False)

azimuth = AzimuthStepper()
