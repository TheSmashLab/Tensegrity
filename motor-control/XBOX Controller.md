# Testing XBOX controller from terminal
`jstest /dev/input/js0`

# Testing XBOX Controller with Joy in ROS
1. Source ROS  
    `source install/setup.bash`
1. Run the joy node  
    `ros2 run joy joy_node`
1. In a second terminal source ROS again  
    `source install/setup.bash`
1. Echo the ros topic  
    `ros2 topic echo /joy`