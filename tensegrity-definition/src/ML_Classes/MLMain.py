"""Will be used to run the MLTraining program, where different methods will be tested as well."""
import numpy as np

from src.TensegritySystem import Systems as S, Nodes as N
import MLTraining_Eval_Use

if __name__ == "__main__":
    """make the initial nodes for the system by calling the Node class"""
    # node1 = N.Node(1.618, 0, 1)
    # node2 = N.Node(1.618, 0, -1)
    node1 = N.Node(1, 1.618 + 1.618, 0)
    node2 = N.Node(1, -1.618 + 1.618, 0)
    # node5 = N.Node(-1.618, 0, 1)
    # node6 = N.Node(-1.618, 0, -1)
    node3 = N.Node(-1, 1.618 + 1.618, 0)
    node4 = N.Node(-1, -1.618 + 1.618, 0)

    node5 = N.Node(1.618, 0 + 1.618, 1)
    node6 = N.Node(1.618, 0 + 1.618, -1)
    # node11 = N.Node(1, 1.618, 0)
    # node12 = N.Node(1, -1.618, 0)
    node7 = N.Node(-1.618, 0 + 1.618, 1)
    node8 = N.Node(-1.618, 0 + 1.618, -1)
    # node15 = N.Node(-1, 1.618, 0)
    # node16 = N.Node(-1, -1.618, 0)

    # node17 = N.Node(0,1.618,  1)
    # node18 = N.Node(0,1.618,  -1)
    node9 = N.Node(0, 1 + 1.618, 1.618)
    node10 = N.Node(0, 1 + 1.618, -1.618)
    # node21 = N.Node(0,-1.618,  1)
    # node22 = N.Node(0,-1.618,  -1)
    node11 = N.Node(0, -1 + 1.618, 1.618)
    node12 = N.Node(0, -1 + 1.618, -1.618)

    """create the needed initial parameters for the System program."""
    nodeArray = np.array([node1, node2, node3, node4, node5, node6, node7, node8, node9, node10, node11, node12])
    # norm(nodeArray)
    stringConnections = np.array(
        [[1, 3], [1, 5], [1, 6], [1, 9], [1, 10], [2, 4], [2, 5], [2, 6], [2, 11], [2, 12], [3, 7], [3, 8], [3, 9],
         [3, 10], [4, 7], [4, 8], [4, 11], [4, 12], [5, 6], [5, 9], [5, 11], [6, 10], [6, 12]
            , [7, 8], [7, 9], [7, 11], [8, 10], [8, 12], [9, 11], [10, 12]])
    # the one below doesn't have strings connecting parallel bars.
    # stringConnections = np.array(
    #    [[1, 5], [1, 6], [1, 9], [1, 10], [2, 5], [2, 6], [2, 11], [2, 12], [3, 7], [3, 8], [3, 9],
    #     [3, 10], [4, 7], [4, 8], [4, 11], [4, 12],  [5, 9], [5, 11], [6, 10], [6, 12]
    #        ,  [7, 9], [7, 11], [8, 10], [8, 12]])
    barConnections = np.array([[1, 2], [3, 4], [5, 7], [6, 8], [9, 10], [11, 12]])

    """creates the system that is being analyzed based off the nodes."""
    system = S.System(barConn=barConnections, nodeArray=nodeArray, stringConn=stringConnections)

    MLalgorithm = MLTraining_Eval_Use.trainMethod(system)
    MLalgorithm.train()  # can comment out this unless training a new network.
    MLalgorithm.test()
