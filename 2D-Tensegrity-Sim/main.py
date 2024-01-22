import argparse
import numpy as np
from yaml_parser import yaml_parser

from visualization import Visualization as Viz
from sim import Sim
from optimization import Optimizer

def main(file):
    parser = yaml_parser(file)
    Nodes, Connections = parser.parse()
    
    viz = Viz(Nodes, Connections)
    viz.plot(label_nodes=True, label_connections=True)



if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='2D Tensegrity Simulator')
    parser.add_argument("filename", help="YAML file to load", default="yaml/1-box.yaml")

    args = vars(parser.parse_args())
    main(file=args["filename"])