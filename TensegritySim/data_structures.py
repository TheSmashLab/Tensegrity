import numpy as np
from typing import List, Dict, Tuple
from enum import Enum
from scipy.optimize import least_squares

class Node:
    """
    Represents a node in a 2D tensegrity structure.

    Attributes:
        name (str): The name of the node.
        position (numpy.ndarray): The position of the node in 2D or 3D space as a numpy array.
    """

    def __init__(self, name: str, position: list):
        """
        Args:
            name (str): The name of the node.
            position (list): The position of the node in 2D or 3D space as a list of 2 or 3 numbers.
        """
        if len(position) != 2 and len(position) != 3:
            raise ValueError("Position input must contain exactly 2 or 3 numbers.")

        self.name = name
        self.position = np.array(position, dtype=float)

    def __str__(self):
        return f"Node: {self.name}  Position: {self.position}"

    def copy(self):
        return Node(self.name, self.position)

class Connection:
    """
    Represents a connection between nodes in a tensegrity structure.
    
    Attributes:
        nodes (List[Node]): A list of nodes that are part of the connection.
        nodes_original (List[Node]): A list of the original positions of the nodes.
        connection_type (ConnectionType): The type of connection.
        stiffness (float): The stiffness of the connection.
        initial_length (float): The initial length of the connection.
        force (float): The force in the connection.
        name (str, optional): The name of the connection.
        initial_length_ratio (float, optional): The initial length ratio of the connection.
    """
    ConnectionType = Enum("ConnectionType", "STRING BAR")

    def __init__(self, nodes: List[Node], connection_type: ConnectionType, stiffness: float = 0, initial_length: float = None, name: str = None):
        """
        Args:
            nodes (List[Node]): A list of nodes that are part of the connection.
            connection_type (ConnectionType): The type of connection.
            stiffness (float, optional): The stiffness of the connection. Defaults to 0.
            initial_length (float, optional): The initial length of the connection. Defaults to None, meaning the current length as calculated by distance between nodes.
            name (str, optional): The name of the connection. Defaults to None.
        """
        self.nodes = nodes
        self.nodes_original = [node.copy() for node in nodes]

        # connection_type must be a ConnectionType enum
        if not isinstance(connection_type, Connection.ConnectionType):
            raise ValueError("connection_type must be a ConnectionType enum.")

        self.connection_type = connection_type
        self.stiffness = stiffness
        if initial_length is None:
            initial_length = self.current_length()
        self.initial_length = initial_length
        self.force = None
        self.name = name
        self.linear = True
        

    def current_length(self, linked_nodes: List[Tuple[Node, Node]] = None):
        """
        Calculates the current length of the connection, considering linked nodes if provided.

        Args:
            linked_nodes (List[Tuple[Node, Node]], optional): A list of tuples representing linked nodes. Defaults to None.

        Returns:
            float: The current length of the connection.
        """
        if linked_nodes is None:
            linked_nodes = []

        length = 0
        for i in range(len(self.nodes) - 1):
            node1, node2 = self.nodes[i], self.nodes[i + 1]
            if {node1.name, node2.name} in linked_nodes:
                continue  # Skip linked nodes
            length += np.linalg.norm(node1.position - node2.position)
        return length

    def update_force(self, current_length: float):
        """
        Updates the force in the connection using the provided current length.

        Args:
            current_length (float): The current length of the connection.
        """
        force = self.stiffness * (current_length - self.initial_length)
        if self.connection_type == Connection.ConnectionType.STRING:
            force = max(0, force)  # strings can only be in tension

        self.force = force

class NonlinProps:
    """
    Represents the material properties of a non-linear connection.
    
    Attributes:
        strain (numpy.ndarray): The strain values.
        stress (numpy.ndarray): The stress values.
    """
    def __init__(self, strain: np.ndarray, stress: np.ndarray):

        # check that the stress and strain arrays are numpy arrays
        if not isinstance(strain, np.ndarray):
            raise TypeError("Strain must be a numpy array.")
        if not isinstance(stress, np.ndarray):
            raise TypeError("Stress must be a numpy array.")

        # check if the stress and strain arrays are of the same length
        if len(stress) != len(strain):
            raise ValueError("Stress and strain arrays must be of the same length.")

        self.strain = strain
        self.stress = stress

        # Ogden Material Model
        self.stretch = 1. + strain
        stress_true = stress * self.stretch
        
        def ogden_uniaxial(params, stretch):
            mu1, alpha1, mu2, alpha2, mu3, alpha3 = params
            term1 = mu1 * (stretch**alpha1 - stretch**(-alpha1/2.))
            term2 = mu2 * (stretch**alpha2 - stretch**(-alpha2/2.))
            term3 = mu3 * (stretch**alpha3 - stretch**(-alpha3/2.))
            return term1 + term2 + term3
        
        def ogden_residuals(params, stretch, stress_true):
            return ogden_uniaxial(params, stretch) - stress_true

        initial_guess = [128.89, 0.0888, -5.68, 6.99, -6.3, -13.5991] # Ogden parameters for Overture.
        result = least_squares(ogden_residuals, initial_guess, args=(self.stretch, stress_true))
        self.ogden_params = result.x
    

class ConnectionNonlinear(Connection):
    """
    Represents a non-linear connection between nodes in a tensegrity structure.
    Inherits from the Connection class.

    Attributes:
    """
    height = 1.2 # mm
    width = 1.2 # mm
    area = height*width # mm^2
    def __init__(self, nodes: List[Node], connection_type: Connection.ConnectionType, material_properties: NonlinProps, initial_length: float = None, area: float = area, name: str = None):
        """
        Args:
            nodes (List[Node]): A list of nodes that are part of the connection.
            connection_type (Connection.ConnectionType): The type of connection.
            material_properties (NonlinProps): The material properties of the connection.
            initial_length (float, optional): The initial length of the connection. Defaults to None, meaning the current length as calculated by distance between nodes.
            area (float, optional): The cross-sectional area of the connection. Defaults to the original area used in prototyping.
            name (str, optional): The name of the connection. Defaults to None.
        """
        super().__init__(nodes, connection_type, 0, initial_length, name)
        self.material_properties = material_properties
        self.strain = self.material_properties.strain
        self.stress = self.material_properties.stress
        self.area = area
        self.stiffness = self.area*np.gradient(self.stress, self.strain, edge_order=2)[0]/self.current_length()
        self.linear = False

        # create a lookup table for length, energy, and derivative of energy
        self.lengths = self.strain * self.initial_length + self.initial_length
        self.dV_dL = self.area * self.current_length() * np.gradient(self.stress, self.strain, edge_order=2)

    # def dV_dq(self):
    #     """
    #     Returns the derivative of the potential energy with respect to the generalized coordinates.
    #     """
    #     dV_dq = {}
    #     for i in range(len(self.nodes) - 1):
    #         # TODO:
    #         dV_dq[self.nodes[i].name] = self.material_properties.dV_dq(self.length, width, height) # return x and y components        
    #     pass


class Surface:
    """
    Represents a surface in the simulation.

    Attributes:
        shape (dict): The shape of the surface. Contains 'surface_type' and 'properties'.
        linked_nodes (List[Tuple[Node, Node]]): A list of tuples representing the linked nodes that form the seam on the surface.
    """

    def __init__(self, shape: Dict, linked_nodes: List[Tuple[Node, Node]]):
        """
        Args:
            shape (Dict): The shape of the surface. Contains 'surface_type' and 'properties'.
            linked_nodes (List[Tuple[Node, Node]]): A list of tuples representing the linked nodes that form the seam on the surface.
        """
        self.shape = shape
        self.linked_nodes = linked_nodes


class Tensegrity:
    """
    Represents a tensegrity structure.
    
    Attributes:
        nodes (List[Node]): A list of nodes in the tensegrity structure.
        connections (List[Connection]): A list of connections between the nodes.
        pins (Dict[str, List[bool]], optional): A dictionary representing the pinned nodes. Defaults to an empty dictionary.
        controls (List[Connection], optional): A list of control connections. Defaults to an empty list.
        surface (Surface, optional): The surface on which the tensegrity structure is placed. Defaults to None.
        dim (int, optional): The dimension of the tensegrity structure. Should be 2, 2.5, or 3. Defaults to None (will automatically be set).
    """

    def __init__(self, nodes: List[Node], connections: List[Connection], pins: Dict[str, List[bool]] = None, controls: List[Connection] = None, surface: Surface = None, dim: int = None):
        """
        Args:
            nodes (List[Node]): A list of nodes in the tensegrity structure.
            connections (List[Connection]): A list of connections between the nodes.
            pins (Dict[str, List[bool]], optional): A dictionary representing the pinned nodes. Defaults to an empty dictionary.
            controls (List[Connection], optional): A list of control connections. Defaults to an empty list.
            surface (Surface, optional): The surface on which the tensegrity structure is placed. Defaults to None.
            dim (int, optional): The dimension of the tensegrity structure. Should be 2, 2.5, or 3. Defaults to None (will automatically be set).
        """
        if pins is None:
            pins = {}
        if controls is None:
            controls = []

        self.nodes = nodes
        self.connections = connections
        self.pins = pins
        self.controls = controls
        self.surface = surface

        self.control_starting_lengths = [control.initial_length for control in self.controls]

        self.update_forces()

        if dim is None:
            if surface:
                dim = 2.5
            elif any([len(node.position) == 2 for node in self.nodes]):
                    dim = 2
            else:
                dim = 3
        self.dim = dim

    def update_forces(self):
        """
        Updates the forces in all connections.
        Call after updating the positions of the nodes.
        """
        for connection in self.connections:
            current_length = connection.current_length(self.surface.linked_nodes if self.surface else None)
            connection.update_force(current_length)

    def get_control_order(self):
        """
        Returns a comma-separated string of the names of the control connections.

        Returns:
            str: A comma-separated string of the names of the control connections.
        """
        return ", ".join([control.name for control in self.controls])

    def change_control_lengths(self, *delta_lengths):
        """
        Changes the lengths of the control connections by the given delta lengths.

        Args:
            *delta_lengths (float): Variable number of arguments representing the changes in lengths 
                                    for each control connection.

        Raises:
            ValueError: If the number of delta lengths provided does not match the number of control connections.
        """
        # Check if the number of delta lengths is equal to the number of control connections
        if len(delta_lengths) != len(self.controls):
            raise ValueError("Number of delta lengths must be equal to the number of control connections.")

        for i, delta_length in enumerate(delta_lengths):
            self.controls[i].initial_length += delta_length

    def reset_control_lengths(self):
        """
        Resets the lengths of the control connections to their original lengths.
        """
        for i, control in enumerate(self.controls):
            control.initial_length = self.control_starting_lengths[i]