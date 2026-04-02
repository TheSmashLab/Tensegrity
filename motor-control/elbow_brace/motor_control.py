import rclpy
from rclpy.node import Node

from sensor_msgs.msg import Joy

# from StepperMotor import StepperMotor

class MotorControl(Node):
    def __init__(self):
        super().__init__('motor_control')
        self.subscription = self.create_subscription(
            Joy, # message type
            'joy', # topic name
            self.listener_callback,
            10) # Queue size 
        self.timer = self.create_timer(0.5, self.timer_callback) # TODO: use timer for motor timeout

        self.maxfrequency = 1200
        self.motor1 = StepperMotor(enable_pin=27, step_pin=18, direction_pin=17, max_frequency=self.maxfrequency) # put step_pin on a hardware PWM pin
        self.motor2= StepperMotor(enable_pin=15, step_pin=13, direction_pin=14, max_frequency=self.maxfrequency) 
        self.motor1.disable()
        self.motor2.disable()
        
    def listener_callback(self, msg):
        
        # motor 1
        speed=1
        if msg.buttons[2]: # X button
            self.motor1.enable()
            self.motor1.set_speed(speed)
        elif msg.buttons[1]: # B button
            self.motor1.enable()
            self.motor1.set_speed(-speed)
        else:
            self.motor1.disable()
        
        # motor 2
        if msg.buttons[0]: # A button
            self.motor2.enable()
            self.motor2.set_speed(speed)
        elif msg.buttons[3]: # Y button
            self.motor2.enable()
            self.motor2.set_speed(-speed)
        else:
            self.motor2.disable()
        
    
    def timer_callback(self):
        pass # use timer for motor timeout so if controller disconnects, motors stop

    def destroy_node(self):
        self.super.destroy_node()

        self.motor1.disable() # ensure motor is disabled when node is stopped


def main(args=None):
    rclpy.init(args=args)

    motor_control = MotorControl()

    rclpy.spin(motor_control)

    motor_control.destroy_node()
    rclpy.shutdown()
    


if __name__ == '__main__':
    main()


from gpiozero import PWMOutputDevice, OutputDevice

class StepperMotor:
    """
    A class representing a stepper motor. Pins are specified with GPIO pin numbers.

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
    def __init__(self, enable_pin, step_pin, direction_pin, max_frequency=(1200)):
        self.enablePin = OutputDevice(enable_pin)
        self.stepPin = PWMOutputDevice(step_pin, frequency=100)
        self.directionPin = OutputDevice(direction_pin)
        self.maxFrequency = max_frequency
 
        self.disable()  # Disable the motor initially

        self.direction = 1  # 1 for clockwise, 0 for counter-clockwise
        self.directionPin.off()
        self.stepPin.value = 0.5


    def set_dir(self, dir):
        if dir == 1:
            self.directionPin.on()
            self.direction = 1
        elif dir == 0:
            self.directionPin.off()
            self.direction = 0
        else:
            print("Invalid direction value. Use 1 for clockwise and 0 for counter-clockwise")



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
            self.direction=0
        elif speed > 0 and self.direction == 0:
            self.directionPin.on()
            self.direction=1
        elif abs(speed)> 1 :
            print("Speed value must be between -1 and 1")

        # Set the speed of the motor (0 to 1)
        speed=speed
        self.stepPin.frequency = abs(speed * self.maxFrequency)

    def enable(self):
        if self.Enabled:
            return
        
        self.enablePin.off()  # Enable the motor
        self.Enabled = True

    def disable(self):
        if not self.Enabled:
            return
        
        self.enablePin.on()  # Disable the motor
        self.Enabled = False

