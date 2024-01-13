import yaml
from os.path import isfile
from typing import List, Tuple

from data_structures import Node, Connection

class yaml_parser:
    """
    A class for parsing YAML files and extracting nodes and connections.

    Args:
        file (str): The path to the YAML file to be parsed.

    Raises:
        FileNotFoundError: If the specified file does not exist.

    Attributes:
        file (str): The path to the YAML file.

    Methods:
        parse: Parses the YAML file and returns a tuple containing a list of nodes and a list of connections.
    """

    def __init__(self, file: str):
        # validate file
        if not isfile(file):
            raise FileNotFoundError(f"The file {file} does not exist.")
                
        self.file = file

    def parse(self) -> Tuple[List[Node], List[Connection]]:
        """
        Parses the YAML file and returns a tuple containing a list of nodes and a list of connections.

        Returns:
            Tuple[List[Node], List[Connection]]: A tuple containing a list of nodes and a list of connections.
        """
        with open(self.file, 'r') as stream:
            data = yaml.safe_load(stream)

            Nodes = {}
            for node in data["nodes"]:
                Nodes[node] = (Node(node, data['nodes'][node]))

            Connections = []
            for connection_type in data["connections"]:
                for connection in data["connections"][connection_type]:
                    Connections.append(Connection(connection_type, [Nodes[n_name] for n_name in connection]))
            
        return list(Nodes.values()), Connections
        