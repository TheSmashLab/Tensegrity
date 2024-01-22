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
    
    def plot(self, label_nodes: bool = False, label_connections: bool = False):
            """
            Plots the visualization of the tensegrity structure.

            Parameters:
            - label_nodes (bool): Whether to label the nodes in the plot.

            Raises:
            - NotImplementedError: If the visualization is not implemented for 3D structures.
            """
            if self.dim == 2:
                self.plot_2d(label_nodes, label_connections)
            else:
                raise NotImplementedError("3D visualization not implemented yet.")
        
    def plot_2d(self, label_nodes: bool = False, label_connections: bool = False):
            """
            Plots the 2D visualization of the tensegrity structure.

            Parameters:
            - label_nodes (bool): If True, labels the nodes on the plot.

            Returns:
            - None
            """
            fig, ax = plt.subplots()
            ax.set_aspect('equal')
            
            for connection in self.Connections:
                # Strings are dashed lines
                if connection.stiffness > 0:
                    if len(connection.nodes) == 2:
                        ax.plot([connection.nodes[0].position[0], connection.nodes[1].position[0]], [connection.nodes[0].position[1], connection.nodes[1].position[1]], 'k--')
                    else:
                        # Allow the color to change for each string connected through multiple nodes 
                        ax.plot([node.position[0] for node in connection.nodes], [node.position[1] for node in connection.nodes], '--') 
                
                # Bars are solid lines
                elif connection.stiffness == 0:
                    ax.plot([connection.nodes[0].position[0], connection.nodes[1].position[0]], [connection.nodes[0].position[1], connection.nodes[1].position[1]], 'k-')

            # plot nodes and label
                for node in self.Nodes:
                    ax.plot(node.position[0], node.position[1], 'ko')
                    if label_nodes:
                        ax.annotate(node.name, (node.position[0], node.position[1]))
                
                if label_connections:
                    for connection in self.Connections:
                        if connection.name:
                            ax.annotate(connection.name, ((connection.nodes[0].position[0] + connection.nodes[1].position[0])/2, (connection.nodes[0].position[1] + connection.nodes[1].position[1])/2), ha='center')
                
            plt.show()
