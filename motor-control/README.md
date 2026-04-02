# Motor Control
## Info 
This repo contains the code to control the motors for the elbow brace project with an Xbox controller. It uses ROS2, a Raspberry Pi and Xbox controller.

## Setup
1. Install Ubuntu Server 24 on Raspberry Pi
1. Install ROS2 Jazzy on RPi: https://docs.ros.org/en/jazzy/Installation/Ubuntu-Install-Debs.html
1. Create a ros workspace ``mkdir -p ~/ros2_ws/src``
1. Clone this repo into src folder
    ```bash
    cd ~/ros2_ws/src
    git clone git@10.5.112.228:elbow-brace/motor-control.git
    ```
1. Build the project
    ```bash
    source /opt/ros/jazzy/setup.bash
    cd ~/ros2_ws
    colcon build --symlink-install
    ```
    It will give you an error about `easy_install` command being deprecated, thats ok, this is a problem between ros and python.

    ```bash
    sudo rosdep init
    rosdep update
    rosdep install --from-paths src --ignore-src -r -y
    ```

# Running ROS
1. You must always source ROS: `source install/setup.bash`
1. `ros2 launch elbow_brace elbow_brace_launch.py`

# To Commit Changes
Since this project is on a shared machine, a shared deploy key is used to push and pull changes from the repository. This means when you make a commit, it doesn't know who is committing to the project so we have to use the following command:
```bash
git -c user.name='Name' -c user.email='NETID@byu.edu' commit -m 'Your message here'
```
Using your own name and email. For instance:
```bash
git -c user.name='Austin Brown' -c user.email='arbrown@byu.edu' commit -m 'Initial commit'
```

# Connect Controller
To connect with USB cable:
```bash
sudo apt install xboxdrv 
```

To connect with Bluetooth you also need:  
TODO: figure out how to enable bluetooth