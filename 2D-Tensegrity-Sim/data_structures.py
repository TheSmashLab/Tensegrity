import numpy as np
from typing import List

class Node:
    """
    Represents a node in a 2D tensegrity structure.

    Attributes:
        name (str): The name of the node.
        position (numpy array(3,)): The position of the node in 3D space as a numpy array.
    """

    def __init__(self, name: str, position: list):
        if len(position) != 3:
            raise ValueError("Position input must contain exactly 3 numbers.")
        
        self.name = name
        self.position = np.array(position, dtype=float)

    def __str__(self):
        return f"Node: {self.name}  Position: {self.position}"

class Connection:
    """
    Represents a connection between nodes in a tensegrity structure.

    Attributes:
        type (str): The type of connection.
        nodes (List[Node]): The nodes involved in the connection.
    """

    def __init__(self, type: str, Nodes: List[Node]):
        self.type = type
        self.nodes = Nodes
