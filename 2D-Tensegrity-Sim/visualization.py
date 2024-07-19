import matplotlib.pyplot as plt
import numpy as np
from mpl_toolkits import mplot3d

class Visualization:
    def __init__(self, Tensegrity, dim=2):
        """
        Initializes a Visualization object.

        Parameters:
        - Nodes (list): A list of Node objects representing the nodes in the tensegrity structure.
        - Connections (list): A list of Connection objects representing the connections between nodes.
        - dim (int): The dimension of the visualization (default is 2).
        """
        self.Nodes = Tensegrity.Nodes
        self.Connections = Tensegrity.Connections
        self.Pins = Tensegrity.Pins
        self.Controls = Tensegrity.Controls

        self.dim = dim

        if dim == 2:
            self.fig, self.ax = plt.subplots()
        elif dim == 3:
            self.fig, self.ax = plt.subplots(subplot_kw={'projection': '3d'})
            self.Surface = Tensegrity.Surface
        else:
            raise ValueError("Invalid dimension. Must be 2 or 3.")
    
    def plot(self, label_nodes: bool = False, label_connections: bool = False, label_forces: bool = False):
        """
        Plot the visualization of the tensegrity structure.

        Args:
            label_nodes (bool): Whether to label the node names in the plot. Default is False.
            label_connections (bool): Whether to label the connection names in the plot. Default is False.
            label_forces (bool): Whether to label the forces on the connections. Default is False.

        Raises:
            NotImplementedError: If the dimension is not 2.

        Returns:
            None
        """
        if self.dim == 3:
            self._plot_3d(label_nodes, label_connections, label_forces)
        else:
            self._plot_2d(label_nodes, label_connections, label_forces)
        
    def _plot_2d(self, label_nodes: bool = False, label_connections: bool = False, label_forces: bool = False):
        """
        Plots the 2D visualization of the tensegrity structure.

        Parameters:
        - label_nodes (bool): If True, labels the nodes on the plot.

        Returns:
        - None
        """
        self.ax.clear()
        self.ax.set_aspect('equal')
        self.ax.set_xlabel('X')
        self.ax.set_ylabel('Y')
        color_index = 1 # Using "CN" color cycle
        color_names = {}
        
        # --- Plot connections ---
        for connection in self.Connections:
            # Strings are dashed lines
            if connection.stiffness > 0:
                # Set color
                color = 'k'
                if connection.name or len(connection.nodes) > 2:
                    color = f"C{color_index}"
                    if connection.name:
                        color_names[connection.name] = color_index
                    color_index += 1
                
                style = '--' if connection.force > 1e-3 else ':'
                # Plot line
                self.ax.plot([node.position[0] for node in connection.nodes], [node.position[1] for node in connection.nodes], f'{color}{style}')
                
            
            # Bars are solid lines
            elif connection.stiffness == 0:
                style = '-' if np.abs(connection.force) > 1e-3 else '-.'
                self.ax.plot([connection.nodes[0].position[0], connection.nodes[1].position[0]], [connection.nodes[0].position[1], connection.nodes[1].position[1]], f'k{style}')

        # --- plot nodes and label ---
        for node in self.Nodes:
            # TODO: How to differentiate between 1D and 2D pinning?
            if node.name in self.Pins:
                self.ax.plot(node.position[0], node.position[1], 'rX')
            else:
                self.ax.plot(node.position[0], node.position[1], 'ko')
            if label_nodes:
                self.ax.annotate(node.name, (node.position[0], node.position[1]), (.2, .2), textcoords='offset fontsize')
        
        if label_forces:
            for connection in self.Connections:
                if connection.name:
                    self.ax.annotate(f"{connection.name}: {connection.force:.2f}", ((connection.nodes[0].position[0] + connection.nodes[1].position[0])/2, (connection.nodes[0].position[1] + connection.nodes[1].position[1])/2), ha='center')
                else:
                    self.ax.annotate(f"{connection.force:.2f}", ((connection.nodes[0].position[0] + connection.nodes[1].position[0])/2, (connection.nodes[0].position[1] + connection.nodes[1].position[1])/2), ha='center')
        elif label_connections:
            for connection in self.Connections:
                if connection.name:
                    self.ax.annotate(connection.name, ((connection.nodes[0].position[0] + connection.nodes[1].position[0])/2, (connection.nodes[0].position[1] + connection.nodes[1].position[1])/2), ha='center')

        # --- plot controls ---
        if self.Controls:
            for control in self.Controls:
                color = f"C{color_names[control.connection.name]}" # Make sure the color matches the associated connection
                self.ax.arrow(control.node.position[0], control.node.position[1], control.direction[0], control.direction[1], head_width=0.05, head_length=0.1, width=.01, color=color)

        self.fig.show()

    def _plot_3d(self, label_nodes: bool = False, label_connections: bool = False, label_forces: bool = False):
        self.ax.clear()
        self.ax.set_aspect('equal')
        self.ax.set_xlabel('X')
        self.ax.set_ylabel('Y')
        self.ax.set_zlabel('Z')
        color_index = 1 # Using "CN" color cycle
        color_names = {}

        def transform(x, y, z=0):
            if self.Surface:
                if self.Surface.shape['surface_type'] == 'cylinder':
                    self.r = self.Surface.shape['properties']['radius']
                    return np.array([self.r*np.cos(x/self.r), self.r*np.sin(x/self.r), y])
            return np.array([x, y, z]) # Default to no transformation

        # --- Plot connections ---
        for connection in self.Connections: 
            # Strings are dashed lines
            if connection.stiffness > 0:
                # Set color
                color = 'k'
                if connection.name or len(connection.nodes) > 2:
                    color = f"C{color_index}"
                    if connection.name:
                        color_names[connection.name] = color_index
                    color_index += 1
                
                style = '--' if connection.force > 1e-3 else ':'
                # Plot line
                postions = [transform(node.position[0], node.position[1]) for node in connection.nodes]
                self.ax.plot3D([pos[0] for pos in postions], [pos[1] for pos in postions], [pos[2] for pos in postions], f'{color}{style}')
            
            # Bars are solid lines
            elif connection.stiffness == 0:
                style = '-' if np.abs(connection.force) > 1e-3 else '-.'
                postions = [transform(node.position[0], node.position[1]) for node in connection.nodes]
                self.ax.plot3D([pos[0] for pos in postions], [pos[1] for pos in postions], [pos[2] for pos in postions], f'k{style}')

        # --- plot nodes and label ---
        for node in self.Nodes:
            # TODO: How to differentiate between 1D and 2D pinning?
            if node.name in self.Pins:
                self.ax.plot3D(*transform(*node.position), 'rX')
            else:
                self.ax.plot3D(*transform(*node.position), 'ko')
            if label_nodes:
                self.ax.text(*transform(*node.position), node.name)

        if label_forces:
            for connection in self.Connections:
                if connection.name:
                    self.ax.text(*(transform(*connection.nodes[0].position) + transform(*connection.nodes[1].position))/2, f"{connection.name}: {connection.force:.2f}")
                else:
                    self.ax.text(*(transform(*connection.nodes[0].position) + transform(*connection.nodes[1].position))/2, f"{connection.force:.2f}")
        elif label_connections:
            for connection in self.Connections:
                if connection.name:
                    self.ax.text(*(transform(*connection.nodes[0].position) + transform(*connection.nodes[1].position))/2, connection.name)

        # --- plot controls ---
        if self.Controls:
            for control in self.Controls:
                color = f"C{color_names[control.connection.name]}" # Make sure the color matches the associated connection
                self.ax.quiver(*transform(*control.node.position), *transform(*control.direction), color=color)
        
        # --- plot surface ---
        if self.Surface:
            if self.Surface.shape['surface_type'] == 'cylinder':
                r = self.Surface.shape['properties']['radius']
                z_max = -np.inf
                z_min = np.inf
                for N in self.Nodes:
                    if transform(*N.position)[2] > z_max:
                        z_max = transform(*N.position)[2]
                    if transform(*N.position)[2] < z_min:
                        z_min = transform(*N.position)[2]
                resolution = 100 # Number of points to plot
                z = np.linspace(z_min, z_max, resolution)
                theta = np.linspace(0, 2*np.pi, resolution)
                theta_grid, z_grid = np.meshgrid(theta, z)
                x_grid = r*np.cos(theta_grid)
                y_grid = r*np.sin(theta_grid)
                self.ax.plot_surface(x_grid, y_grid, z_grid, alpha=0.25, color='gray')

        self.fig.show()