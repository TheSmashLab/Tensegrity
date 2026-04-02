from launch import LaunchDescription
from launch_ros.actions import Node

def generate_launch_description():
    return LaunchDescription([
        Node(
            package='elbow_brace',
            executable='motor_control',
            name='motor_control'
        ),
        Node(
            package='joy',
            executable='joy_node',
            name='joy_node',
            parameters=[{
                'device_id': 0, # The joystick device to use. `ros2 run joy joy_enumerate_devices` wil list the attached devices.
                'deadzone': 0.05, # Amount by which the joystick has to move before it is considered to be off-center.
                'autorepeat_rate': 5.0, # Rate in Hz at which a joystick that has a non-changing state will resend the previously sent message. If set to 0.0, autorepeat will be disabled, meaning joy messages will only be published when the joystick changes.
                'coalesce_interval': 0.1
            }]
        )
    ])