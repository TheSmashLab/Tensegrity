from gpiozero import PWMOutputDevice, OutputDevice
from time import sleep

class StepperMotor:
    """
    A class representing a stepper motor.

    Args:
        enable_pin (int): The pin number for the enable pin.
        step_pin (int): The pin number for the step pin.
        direction_pin (int): The pin number for the direction pin.
        max_frequency (int, optional): The maximum frequency of the motor. Defaults to 100.

    Attributes:
        enablePin (OutputDevice): The output device for the enable pin.
        stepPin (PWMOutputDevice): The PWM output device for the step pin.
        directionPin (OutputDevice): The output device for the direction pin.
        maxFrequency (int): The maximum frequency of the motor.
        direction (int): The direction of rotation (1 for clockwise, 0 for counter-clockwise).

    Methods:
        set_speed(speed): Sets the speed of the motor.
        enable(): Enables the motor.
        disable(): Disables the motor.
    """
    def __init__(self, enable_pin, step_pin, direction_pin, max_frequency=100):
        self.enablePin = OutputDevice(enable_pin)
        self.stepPin = PWMOutputDevice(step_pin, frequency=100)
        self.directionPin = OutputDevice(direction_pin)
        self.maxFrequency = max_frequency

        self.enablePin.off()  # Disable the motor initially

        self.direction = 1  # 1 for clockwise, 0 for counter-clockwise
        self.stepPin.value = 0.5


    def set_speed(self, speed):
        """
        Sets the speed of the motor.

        Parameters:
            speed (float): The speed value between -1 and 1.
                           Positive values indicate clockwise rotation.
                           Negative values indicate counter-clockwise rotation,

        Returns:
            None
        """
        if speed < 0 and self.direction == 1:
            self.directionPin.off()
        elif speed > 0 and self.direction == 0:
            self.directionPin.on()

        # Set the speed of the motor (0 to 1)
        self.stepPin.frequency = abs(speed * self.maxFrequency)

    def enable(self):
        self.enablePin.on()  # Enable the motor

    def disable(self):
        self.enablePin.off()  # Disable the motor

# Example usage
if __name__ == "__main__":
    motor = StepperMotor(enable_pin=17, step_pin=27, direction_pin=22, max_frequency=100)
    motor.set_speed(0.5)  # Set speed to 50% CW
    motor.enable()
    sleep(5)  # Run the motor for 5 seconds
    motor.disable()
