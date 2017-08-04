import RPi.GPIO as GPIO
import time

class Stepper:
    GPIO_SLEEP = 8.0 / 1000.0

    def __init__(self, total_steps, direction_gpio, pulse_gpio, backlash_steps):
        self.__total_steps = total_steps
        self.__direction_gpio = direction_gpio
        self.__pulse_gpio = pulse_gpio
        self.__backlash_steps = backlash_steps
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
            self.compensate_backlash()

        self.pulse()

        if direction:
          self.__position += 1
        else:
          self.__position -= 1
        self.__position %= self.__total_steps

    def compensate_backlash(self):
        for i in range(self.__backlash_steps):
            self.pulse()

    def pulse(self):
        GPIO.output(self.__pulse_gpio, False)
        time.sleep(self.GPIO_SLEEP)
        GPIO.output(self.__pulse_gpio, True)
        time.sleep(self.GPIO_SLEEP)
