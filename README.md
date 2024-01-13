# 2D Tensegrity Sim

## About
This repo contains code to create a simulation for 2D Tensegrity structures specifically taylored to the needs of the Elbow Brace Project.

## Getting started
I reccommend using a venv to keep the libraries for this project seperate from the main python interpreter. To create a venv, from the project's main directory run `python3 -m venv ./venv`. Now everytome you want to use this venv run `source venv/bin/activate`. To deactivate simpy use the `deactivate` command

This project uses Python3, in order to run it you will need some dependencies. To get them you can run `pip install -r requirements.txt`


## Organization
### 2D-Tensegrity-Sim
The `2D-Tensegrity-Sim` directory contains all the code for the project.

### yaml
The `yaml` directory contains sample yaml files for running the sim

# Ideas for future implementation
* Create GUI to help create yaml files
    * yaml file contains just nodes and gui has interface to define how they are connected
    * Allow easy "tiling" of single cells to n x m cells