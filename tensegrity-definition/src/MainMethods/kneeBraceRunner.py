import numpy as np
from typing import List

from src.TensegritySystem import Systems as S, ClassK_Test as ckt, Nodes as N, TensegrityClassKConvert as tkc
from src.Utils import TensegrityPlotter as plot, SaveData

if __name__ == "__main__":
    node1: N.Node = N.Node(0, 0, np.sqrt(3) / 6)
    node2: N.Node = N.Node(0, -5, np.sqrt(3) / 6)
    node3: N.Node = N.Node(0, -3.5, np.sqrt(3) / 2)
    node4: N.Node = N.Node(1 / 2, -3.5, 0)
    node5: N.Node = N.Node(-1 / 2, -3.5, 0)
    node6: N.Node = N.Node(1 / 2, -2.5, np.sqrt(3) / 3)
    node7: N.Node = N.Node(0, -2.5, -np.sqrt(3) / 6)
    node8: N.Node = N.Node(-1 / 2, -2.5, np.sqrt(3) / 3)
    node9: N.Node = N.Node(0, -2.5, np.sqrt(3) / 6)
    node10: N.Node = N.Node(0, -3.5, np.sqrt(3) / 6)

    nodeArray: np.ndarray[N.Node] = np.array([node1, node2, node3, node4, node5, node6, node7, node8, node9, node10])

    stringConnections: np.ndarray[np.ndarray[int]] = np.array([[1, 3], [1, 4], [1, 5], [3, 4], [3, 5], [4, 5], [3, 6], [3, 8], [4, 7], [4, 6], [5, 8], [5, 7],
                                                               [6, 7], [6, 8], [7, 8], [6, 2], [7, 2], [8, 2], [3, 10], [4, 10], [5, 10], [6, 9], [7, 9],
                                                               [8, 9]])
    barConnections: np.ndarray[np.ndarray[int]] = np.array([[9, 3], [9, 4], [9, 5], [10, 6], [10, 7], [10, 8], [1, 9], [2, 10]])

    # Creates the system that is being analyzed based off the nodes.
    system: S.System = S.System(barConn=barConnections, barMaterial='Steel', nodeArray=nodeArray, stringConn=stringConnections, stringMaterial='Steel')

    # Creates a basic plot of the system in 3D
    # plot.basicPlot(nodeArray, system.getStringConn(), system.getBarConn())

    # This portion zooms in on the area that surrounds the knee.
    node1 = N.Node(0, -1.5, np.sqrt(3) / 2)
    node2 = N.Node(1 / 2, -1.5, 0)
    node3 = N.Node(-1 / 2, -1.5, 0)
    node4 = N.Node(1 / 2, -.5, np.sqrt(3) / 3)
    node5 = N.Node(0, -.5, -np.sqrt(3) / 6)
    node6 = N.Node(-1 / 2, -.5, np.sqrt(3) / 3)
    node7 = N.Node(0, -.5, np.sqrt(3) / 6)
    node8 = N.Node(0, -1.5, np.sqrt(3) / 6)

    nodeArray1: np.ndarray[N.Node] = np.array([node1, node2, node3, node4, node5, node6, node7, node8])
    stringConnections1: np.ndarray[np.ndarray[int]] = np.array([[1, 2], [1, 3], [2, 3], [1, 4], [1, 6], [2, 5], [2, 4], [3, 6], [3, 5], [4, 5], [4, 6], [5, 6],
                                                               [1, 8], [2, 8], [3, 8], [4, 7], [5, 7], [6, 7]])
    barConnections1: np.ndarray[np.ndarray[int]] = np.array([[7, 1], [7, 2], [7, 3], [8, 4], [8, 5], [8, 6]])

    # Creates the system that is being analyzed based off the nodes.
    system1: S.System = S.System(barConn=barConnections1, barMaterial='Steel', nodeArray=nodeArray1, stringConn=stringConnections1, stringMaterial='Steel')

    # Gives a basic plot of the system in 3D
    # plot.basicPlot(nodeArray1, system1.getStringConn(), system1.getBarConn(), axisLength=1)

    ### END OF ZOOMED IN BRACE ###

    # This pins the first node in all directions.
    pinnedNodes: List[int] = [1]
    system.setPinned(pinnedNodes)

    nNew: np.ndarray[np.ndarray[float]]
    cbNew: np.ndarray[np.ndarray[float]]
    csNew: np.ndarray[np.ndarray[float]]
    P: np.ndarray[np.ndarray[float]]
    D: np.ndarray[np.ndarray[float]]
    nodeConstraints: List[List[int]]

    kConvert: tkc.tensegrityKConvert = tkc.tensegrityKConvert(nodeArray, system.getBarConnMat(), system.getStringConnMat(), pinnedNodes)
    nNew, cbNew, csNew, P, D, nodeConstraints = kConvert.returnNeededValues()

    # Sets the stretch percent as how long the initial string length was compared to the current length.
    s0Percent: np.ndarray[np.ndarray[float]] = np.append(np.array([np.arange(1, len(csNew) + 1)]), np.array([.7 * np.ones(len(csNew), dtype=int)]), axis=0).T
    s0: np.ndarray[float] = tkc.TensegPercentTo_s0(nNew, csNew, s0Percent)

    # Add initial velocity
    V: List[float] = []

    # Sets the force array as based on the total force in each cartesian dimension on the node.
    W: np.ndarray[np.ndarray[float]] = np.zeros([3, len(nNew[0])])
    W[1, 1] = -10

    classKTest: ckt.ClassK_Test = ckt.ClassK_Test(nNew, cbNew, csNew, system, P, D, s0, V, W, dt=.001, tf=3, axisLength=3)
    classKTest.TensegSimClassKOpen(damping=2, updateForces=False,  updateGround=False, useController=False)
    name: str = 'ImmobKneeYforces'

    # plot.plotPath(classKTest.nodeHist, name, classKTest.targets)
    # TODO: needs to be looked at more closely.
    SaveData.animateMotion(classKTest.axisLength, classKTest.system.barConn, classKTest.dt, classKTest.nodeHist, classKTest.system.stringConn, classKTest.tf,
                           name + ".mp4")
    # classKTest.sendInfoToCSVFile(name +'.csv')
