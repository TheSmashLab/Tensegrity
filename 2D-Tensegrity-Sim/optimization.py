import numpy as np
from typing import List, Tuple, Dict
from scipy.optimize import minimize

from data_structures import Node, Connection, Tensegrity
np.set_printoptions(precision=3, suppress=True) # for debugging


class Optimizer:
    def __init__(self, tensegrity: Tensegrity, d: int = 3) -> None:
            """
            Initializes an Optimization object.

            Parameters:
            - tensegrity (Tensegrity): The tensegrity object containing nodes and connections.
            - d (int): The dimension of the optimization problem (default is 3).

            Raises:
            - ValueError: If connection stiffness is less than 0.
            """
            self.nodes = tensegrity.Nodes
            self.connections = tensegrity.Connections

            self.pinned_nodes = tensegrity.Pins
            self.num_pins = sum([bools.count(True) for bools in self.pinned_nodes.values()]) # QUESTION: is this ever used? If not, remove it.
            
            self.controls = tensegrity.ControlsDict
            
            self.d = d

            # Setup
            self.bar_connections = []
            self.string_connections = []
            for connection in self.connections:
                if connection.stiffness > 0:
                    self.string_connections.append(connection)
                elif connection.stiffness == 0:
                    self.bar_connections.append(connection)
                else:
                    raise ValueError("Connection stiffness must be greater than or equal to 0.") #TODO: Implement stiffness less than 0 (representing bars that can change length)
            
            self.node_indices = {node.name: i for i, node in enumerate(self.nodes)}
            self.bar_indices = {connection: i for i, connection in enumerate(self.bar_connections)}

    
    

    def optimize(self) -> None:
            """
            Optimizes the position of nodes in the tensegrity structure.
            
            This method uses the minimize function from the scipy.optimize module to find the optimal positions of the nodes
            in the tensegrity structure. It iteratively adjusts the positions of the nodes to minimize the objective function,
            which is the sum of squared node equations. The node equations represent the forces acting on each node due to the
            string and bar connections in the structure.
            
            Returns:
                None
            """
            
            constraints = {'type': 'eq', 'fun': self._constraint_function}

            x0 = self._createInputX()
            result = minimize(self._objective, x0, constraints=constraints)
            
            if not result.success:
                print(result)
                raise ValueError("Optimization failed.")
            
            N = self._getFromInputX(result.x)[0]

            for i, node in enumerate(self.nodes):
                node.position = N[i]

            # TODO: update the forces in the connections

            return
    

    # --------------------- INTERNAL FUNCTIONS ---------------------
    @staticmethod
    def _spring(N1: np.ndarray, N2: np.ndarray, l: float, k:float) -> np.ndarray:
        """
        Calculates the force exerted on node1 by node2 modeled as a spring between them.

        Args:
            N1 (np.array([x,y])): The first node.
            N2 (np.array([x,y])): The second node.
            l (float): The length of the upstretched spring.
            k (float): The spring constant.

        """
        if np.linalg.norm(N2 - N1) - l < 0:
            return np.zeros(N1.shape)
        return k * (np.linalg.norm(N2 - N1) - l) * (N2 - N1) / np.linalg.norm(N2 - N1)
    
    def _springConnection(self, connection: Connection, N: np.ndarray) -> Dict[str, np.ndarray]:
        """
        Calculates the forces exerted by a spring connection on the nodes.

        Args:
            connection (Connection): The spring connection object.
            N (np.ndarray): The current positions of all nodes.

        Returns:
            Dict[str, np.ndarray]: A dictionary containing node names as keys and the forces exerted on them by the spring connection as values.
        """

        # current length
        l = 0
        for i in range(len(connection.nodes) - 1):
            l += np.linalg.norm(N[self.node_indices[connection.nodes[i].name]] - N[self.node_indices[connection.nodes[i+1].name]])

        # scalar force
        F = connection.stiffness * (l - connection.length)

        forces = {node.name: np.zeros(self.d) for node in connection.nodes}
        for i in range(len(connection.nodes) - 1):
            N1 = N[self.node_indices[connection.nodes[i].name]]
            N2 = N[self.node_indices[connection.nodes[i+1].name]]

            # Vector forces
            forces[connection.nodes[i].name] += F * (N2 - N1) / np.linalg.norm(N2 - N1)
            forces[connection.nodes[i+1].name] += F * (N1 - N2) / np.linalg.norm(N2 - N1)
        
        # Add in force from control string pull
        if connection.name and connection.name in self.controls:
            control = self.controls[connection.name]
            forces[control.node.name] += F * control.direction[:self.d] / np.linalg.norm(control.direction[:self.d])
        
        connection.tension = F # TODO: only need to save tension after solved, not at each iteration

        return forces
              
    
    @staticmethod
    def _barConstraint(N1: np.ndarray, N2: np.ndarray, l: float) -> float:
        """
        The constraint function for a bar. 
        The length should stay the same and thus when optimized this function should return 0.

        Args:
            N1 (np.array([x,y])): The first node.
            N2 (np.array([x,y])): The second node.
            l (float): The length of the bar.

        """
        return np.linalg.norm(N2 - N1) - l
    
    def _constraint_function(self, x):
        """
        Calculates the constraints for the optimization problem based on the given input vector x.

        Parameters:
        - x: The input vector containing the values of Node positions and B_forces.

        Returns:
        - constraints: A list of constraint values calculated based on the given input vector x.
        """
        N, B_forces = self._getFromInputX(x)
        
        constraints = []
        # Add the bar constraints (length must stay the same)
        for connection in self.bar_connections:
            N1 = N[self.node_indices[connection.nodes[0].name]]
            N2 = N[self.node_indices[connection.nodes[1].name]]
                
            constraints.append(self._barConstraint(N1, N2, connection.length))
        
        return constraints
    
    def _createInputX(self) -> np.ndarray:
        """
        Creates the input vector x0 for the optimization problem.

        Returns:
            np.ndarray: The input vector x0. 
                        The first d*len(nodes) elements are the node positions (except those that are pinned) 
                        and the last len(bar_connections) elements are the bar forces.
        """
        x0 = np.array([node.position[:self.d] for node in self.nodes]).flatten() # position of the nodes
        
        x0 = np.delete(x0, [self.node_indices[node]*self.d + i for node, bools in self.pinned_nodes.items() for i in range(self.d) if bools[i]])

        x0 = np.append(x0, [0]*len(self.bar_connections)) # Add the bar forces to the initial guess (all zeros)
        return x0
    
    def _getFromInputX(self, x: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        """
        Extracts node positions and bar forces from the input vector.

        Parameters:
            x (np.ndarray): The input vector containing node positions and bar forces.

        Returns:
            tuple[np.ndarray, np.ndarray]: A tuple containing the extracted node positions and bar forces including those removed from the input because they were pinned.
        """
        N = x[:-len(self.bar_connections)] # Get the node positions from the input vector
            
        # Add back in pinned nodes
        ins_index = {}
        for node, bools in self.pinned_nodes.items():
            index = self.node_indices[node]*self.d
            for i in range(self.d):
                if bools[i]:
                    ins_index[index + i] = self.nodes[self.node_indices[node]].position[i]
        for index, value in ins_index.items(): # QUESTION: Will this always work as expected? Insert in the correct order?
            N = np.insert(N, index, value)
        
        N = N.reshape(-1, self.d)

        B_forces = x[-len(self.bar_connections):] # Get the bar forces from the input vector (last len(bar_connections) elements)

        return N, B_forces
    
    def _objective(self, x: np.ndarray) -> float:
        N, B_forces = self._getFromInputX(x)

        node_equations = np.zeros((len(self.nodes), self.d)) # d equations for each node that must sum to zero
        
        for connection in self.string_connections:
            forces = self._springConnection(connection, N)
            for node, force in forces.items():
                node_equations[self.node_indices[node]] += force

        for connection in self.bar_connections:
            N1 = N[self.node_indices[connection.nodes[0].name]]
            N2 = N[self.node_indices[connection.nodes[1].name]]
            
            F = B_forces[self.bar_indices[connection]] * (N2 - N1) / np.linalg.norm(N2 - N1)
            node_equations[self.node_indices[connection.nodes[0].name]] += F
            node_equations[self.node_indices[connection.nodes[1].name]] += -F
            connection.tension = np.linalg.norm(F) #TODO: only need to save tension after solved, not at each iteration
        
        return np.square(node_equations).sum()