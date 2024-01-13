import argparse

from yaml_parser import yaml_parser
from visualization import Visualization as Viz

def main(file):
    parser = yaml_parser(file)
    Nodes, Connections = parser.parse()
    
    viz = Viz(Nodes, Connections)
    viz.plot()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='2D Tensegrity Simulator')
    parser.add_argument("-f", "--file", help="File to load")

    args = vars(parser.parse_args())
    main(file=args["file"])