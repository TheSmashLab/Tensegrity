from src.TensegritySystem import Systems as S, Nodes as N
import numpy as np

if __name__ == "__main__":

    """make the initial nodes for the system by calling the Node class"""
    node1 = N.Node(-1, 0 , 0)
    node2 = N.Node(0, -1 , 0)
    node3 = N.Node(1, 0, 0)
    node4 = N.Node(0, 1, 0)

    """create the needed initial parameters for the System program."""
    nodeArray = np.array([node1, node2, node3, node4])
    stringConnections = np.array([[1,3],[2,4]])
    barConnections = np.array([[1,2],[2,3],[3,4],[4,1]])

    """creates the system that is being analyzed based off the nodes."""
    system = S.System(barConn=barConnections, nodeArray=nodeArray, stringConn=stringConnections)

    """gives a basic plot of the system in 3D"""
    #plot.basicPlot(nodeArray,system.GetStringConn(), system.GetBarConn())

    """sets the force array as based on the total force in each cartesian dimension on the node."""
    W = np.zeros([3,len(nodeArray)])
    W[0, 0] = 10000
    W[0, 2] = -10000
    system.setForce(W)

    """creates a pinned location for the system, or what joint is pinned and in which dimensions."""
    pinned_nodes = [[2, 1, 1, 1]]
    system.setPinned(pinned_nodes)

    """runs the equilibrium minimizer"""
    system.tensegrityEquilibriumMinimalMass()
