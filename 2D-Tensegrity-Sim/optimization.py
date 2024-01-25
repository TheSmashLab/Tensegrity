import numpy as np
from typing import List
from scipy.optimize import minimize

from data_structures import Node, Connection

class Optimizer:
    def __init__(self, nodes: List[Node], connections: List[Connection], d: int = 3) -> None:
        self.nodes = nodes
        self.connections = connections
        self.d = d

        self.bar_connections = []
        self.string_connections = []
        for connection in self.connections:
            if connection.stiffness > 0:
                self.string_connections.append(connection)
            elif connection.stiffness == 0:
                self.bar_connections.append(connection)
            else:
                raise ValueError("Connection stiffness must be greater than or equal to 0.")

    def optimize(self) -> None:
        # Spring function
        def f(N1: np.array([float, float]), N2: np.array([float, float]), l: float, k:float) -> np.array([float, float]):
            """
            Calculates the force exerted on node1 by node2 modeled as a spring between them.

            Args:
                N1 (np.array([x,y])): The first node.
                N2 (np.array([x,y])): The second node.
                l (float): The length of the upstretched spring.
                k (float): The spring constant.

            """
            return k * (np.linalg.norm(N2 - N1) - l) * (N2 - N1) / np.linalg.norm(N2 - N1)
    
        def bar(N1: np.array([float, float]), N2: np.array([float, float]), l: float) -> float:
            """
            The constraint function for a bar. 
            The length should stay the same and thus when optimized this function should return 0.

            Args:
                N1 (np.array([x,y])): The first node.
                N2 (np.array([x,y])): The second node.
                l (float): The length of the bar.

            """
            return np.linalg.norm(N2 - N1) - l
        
        node_indices = {node.name: i for i, node in enumerate(self.nodes)}
        bar_indices = {connection: i for i, connection in enumerate(self.bar_connections)}
        
        
        def objective(x: np.array([float])) -> float:
            N = x[:self.d*len(self.nodes)].reshape(-1, self.d)
            B_forces = x[self.d*len(self.nodes):]

            node_equations = np.zeros((len(self.nodes), self.d))
            for connection in self.string_connections:
                N1 = N[node_indices[connection.nodes[0].name]]
                N2 = N[node_indices[connection.nodes[1].name]]
                
                node_equations[node_indices[connection.nodes[0].name]] += f(N1, N2, connection.length, connection.stiffness)
                node_equations[node_indices[connection.nodes[1].name]] += f(N2, N1, connection.length, connection.stiffness)
            
            
            for connection in self.bar_connections:
                N1 = N[node_indices[connection.nodes[0].name]]
                N2 = N[node_indices[connection.nodes[1].name]]
                
                node_equations[node_indices[connection.nodes[0].name]] += B_forces[bar_indices[connection]] * (N2 - N1) / np.linalg.norm(N2 - N1)
                node_equations[node_indices[connection.nodes[1].name]] += B_forces[bar_indices[connection]] * (N1 - N2) / np.linalg.norm(N1 - N2)
            return np.square(node_equations).sum() # TODO: have to add forces the bar carries
        
        def bar_constraints(x):
            constraints = []
            for connection in self.connections:
                if connection.stiffness == 0:
                    N1 = np.array([x[2 * node_indices[connection.nodes[0].name]], x[2 * node_indices[connection.nodes[0].name] + 1]])
                    N2 = np.array([x[2 * node_indices[connection.nodes[1].name]], x[2 * node_indices[connection.nodes[1].name] + 1]])
                    
                    constraints.append(bar(N1, N2, connection.length))
            return constraints

        
        constraints = {'type': 'eq', 'fun': bar_constraints}

        # TODO: remove pinned nodes from optimization input

        x0 = np.array([node.position[:self.d] for node in self.nodes]).flatten() # position of the nodes
        
        x0 = np.append(x0, [0]*len(self.bar_connections)) # Add the bar forces to the initial guess

        result = minimize(objective, x0, constraints=constraints)
        
        if not result.success:
            raise ValueError("Optimization failed.")
        
        N = result.x[:self.d*len(self.nodes)].reshape(-1, self.d)

        for i, node in enumerate(self.nodes):
            node.position = N[i]

        return