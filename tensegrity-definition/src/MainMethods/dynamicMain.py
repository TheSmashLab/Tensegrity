"""
This main method creates the double pendulum example from the MOTES paper. For the code to be considered not broken, we need both the dynamicMain.py and the
icosahedronTesting to create realistic values.
"""
import numpy as np
from typing import List

from src.TensegritySystem import Systems as S, ClassK_Test as ckt, Nodes as N, TensegrityClassKConvert as tkc
from src.Utils import SaveData

if __name__ == "__main__":

    # Make the initial nodes for the system by calling the Node class
    node1: N.Node = N.Node(0, 0, 0)
    node2: N.Node = N.Node(np.sqrt(2) / 2, -np.sqrt(2) / 2, 0)
    node3: N.Node = N.Node(np.sqrt(2), -np.sqrt(2), 0)

    nodeArray: np.ndarray[N.Node] = np.array([node1, node2, node3])

    C_b_in: np.ndarray[np.ndarray[int]] = np.array([[1, 2], [2, 3]])
    C_s_in: np.ndarray[np.ndarray[int]] = np.array([[1, 2], [2, 3]])

    system: S.System = S.System(barConn=C_b_in, nodeArray=nodeArray, stringConn=C_s_in)

    pinnedNodes: List[int] = [1]
    system.setPinned(pinnedNodes)

    # plot.basicPlot(nodeArray,system.GetStringConn(), system.GetBarConn())

    # These are the values that are returned from the KConvert file.  Declared beforehand so type hinting could be accomplished.
    nNew: np.ndarray[np.ndarray[float]]
    cbNew: np.ndarray[np.ndarray[float]]
    csNew: np.ndarray[np.ndarray[float]]
    P: np.ndarray[np.ndarray[float]]
    D: np.ndarray[np.ndarray[float]]
    nodeConstraints: List[List[int]]

    # TODO: The P value here does not match the MATLAB result.  FIX.
    kConvert: tkc.tensegrityKConvert = tkc.tensegrityKConvert(nodeArray, system.getBarConnMat(), system.getStringConnMat(), pinnedNodes)
    nNew, cbNew, csNew, P, D, nodeConstraints = kConvert.returnNeededValues()

    print("converted Class K # of nodes: " + str(len(nNew[0])))
    print("Class k node constraints:")
    for i in range(0, len(nodeConstraints)):
        if 1 < len(nodeConstraints[i]):
            print("Coincident nodes: ", str(nodeConstraints[i]))

    # Specify resetting string lengths.
    # Here we are setting  every string rest length to 70% of the given length.
    s0Percent: np.ndarray[np.ndarray[float]] = np.append(np.array([np.arange(1, len(csNew) + 1)]), np.array([np.ones(len(csNew), dtype=int)]), axis=0).T
    print("percents")
    print(s0Percent)
    s0: np.ndarray[float] = tkc.TensegPercentTo_s0(nNew, csNew, s0Percent)

    print(s0)

    # Add velocity
    V: List[float] = []
    # V = np.zeros([3,len(nNew[0])])
    # V[2,0:len(nodeArray[0])/3] = -2*np.ones([0,len(nodeArray[0])/3])
    # V[1,1] = 10  NOT IMPLEMENTED IN MATLAB CODE, CAN BE USED TO CHECK AGAINST.

    # Add external forces
    W: np.ndarray[np.ndarray[float]] = np.zeros([3, len(nNew[0])])
    W[1, 0] = -0.5 * 9.8
    W[1, 1] = -9.8
    W[1, 2] = -.5 * 9.8

    # Create data structure of system before segmentation.
    classKTest: ckt.ClassK_Test = ckt.ClassK_Test(nNew, cbNew, csNew, system, P, D, s0, V, W, dt=.001, tf=5, axisLength=2)
    classKTest.TensegSimClassKOpen(updateForces=False, damping=.001, updateGround=False, useController=False)

    # The optional datastorage option.
    name = "double_pendulum"
    SaveData.animateMotion(classKTest.axisLength, classKTest.system.barConn, classKTest.dt, classKTest.nodeHist, classKTest.system.stringConn,
                           classKTest.tf, name + ".mp4")
