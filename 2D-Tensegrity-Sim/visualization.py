import matplotlib.pyplot as plt

class Visualization:
    def __init__(self, Nodes, Connections, dim=2):
        """
        Initializes a Visualization object.

        Parameters:
        - Nodes (list): A list of Node objects representing the nodes in the tensegrity structure.
        - Connections (list): A list of Connection objects representing the connections between nodes.
        - dim (int): The dimension of the visualization (default is 2).
        """
        self.Nodes = Nodes
        self.Connections = Connections

        self.dim = dim
    
    def plot(self):
        """
        Plots the visualization of the tensegrity structure.
        """
        if self.dim == 2:
            self.plot_2d()
        else:
            raise NotImplementedError("3D visualization not implemented yet.")
        
    def plot_2d(self):
        """
        Plots the 2D visualization of the tensegrity structure.
        """
        fig, ax = plt.subplots()
        ax.set_aspect('equal')
        
        for connection in self.Connections:
            # TODO: Generalize beyond just bars and strings (or specific names)???
            if connection.type == "bar":
                ax.plot([connection.nodes[0].position[0], connection.nodes[1].position[0]], [connection.nodes[0].position[1], connection.nodes[1].position[1]], 'k-')
            elif connection.type == "string":
                if len(connection.nodes) == 2:
                    ax.plot([connection.nodes[0].position[0], connection.nodes[1].position[0]], [connection.nodes[0].position[1], connection.nodes[1].position[1]], 'k--')
                else:
                    # Allow the color to change for each string connected through multiple nodes 
                    ax.plot([node.position[0] for node in connection.nodes], [node.position[1] for node in connection.nodes], '--') 
            else:
                raise ValueError(f"Connection type {connection.type} not recognized.")
        
        plt.show()