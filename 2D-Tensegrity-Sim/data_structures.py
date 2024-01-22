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

    def __init__(self, Nodes: List[Node], type: str, stiffness: float = 0, pretension: float = 0, name: str = None):
        self.nodes = Nodes

        self.type = type # just stored for debugging purposes
        self.stiffness = stiffness
        self.tension = pretension

        self.length = 0
        for i in range(len(self.nodes)-1):
            self.length += np.linalg.norm(self.nodes[i].position - self.nodes[i+1].position)
            
        if self.stiffness != 0:
            # Length is the distance between the nodes minus how much it is stretched
            # F = kx  ->  x = F/k
            self.length -= pretension/stiffness
        
        self.name = name 