import argparse
from yaml_parser import yaml_parser

from visualization import Visualization as Viz
from optimization import Optimizer

def main(file):
    parser = yaml_parser(file)
    tensegrity_system = parser.parse()
    
    viz = Viz(tensegrity_system)
    viz.plot(label_nodes=True, label_connections=True)

    opt = Optimizer(tensegrity_system, d=2)
    tensegrity_system.change_connection_length("String1", -.3)
    opt.optimize()

    viz.plot(label_nodes=True, label_forces=True)

    return



if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='2D Tensegrity Simulator')
    parser.add_argument("filename", help="YAML file to load", default="yaml/1-box.yaml")

    args = vars(parser.parse_args())
    main(file=args["filename"])