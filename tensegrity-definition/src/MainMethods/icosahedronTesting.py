"""
An icosahedron is the shape of the tensegrity structure that we will be attempting to control, in particular the regular convex icosahedron. It is a polygon
with 20 faces with each face being the same sized equilateral triangle. The structure has 12 vertices and 20 faces,30 edges meaning that 5 faces intersect
at every vertex. The icosahedron can be created by using a cyclic permutation of the coordinates (phi,1,0) including their negative counterparts, and then
taking 1/2 of the calculated nodes, where every other node is discarded. In this code, we will assume that the floor is 0, so the y coordinates at all
points will be translated vertically by 2 units.
"""
import numpy as np
from typing import List
import matplotlib.pyplot as plt

from src.TensegritySystem import Systems as S, ClassK_Test as ckt, Nodes as N, TensegrityClassKConvert as tkc
from src.Utils import CommonMatrixOperations, CalcSystemProperties, SaveData, TensegrityPlotter as plot

# This number was initially determined analytically, and then tuned by hand to get the base of the system as flat as possible for the initial system state.
DEGREES_TO_START_FLAT: float = -41.80901 / 2

if __name__ == "__main__":

    # Make the initial nodes for the system by calling the Node class
    node1: N.Node = N.Node(1, 1.618 + 1.618, 0)
    node2: N.Node = N.Node(1, -1.618 + 1.618, 0)
    node3: N.Node = N.Node(-1, 1.618 + 1.618, 0)
    node4: N.Node = N.Node(-1, -1.618 + 1.618, 0)
    node5: N.Node = N.Node(1.618, 0 + 1.618, 1)
    node6: N.Node = N.Node(1.618, 0 + 1.618, -1)
    node7: N.Node = N.Node(-1.618, 0 + 1.618, 1)
    node8: N.Node = N.Node(-1.618, 0 + 1.618, -1)
    node9: N.Node = N.Node(0, 1 + 1.618, 1.618)
    node10: N.Node = N.Node(0, 1 + 1.618, -1.618)
    node11: N.Node = N.Node(0, -1 + 1.618, 1.618)
    node12: N.Node = N.Node(0, -1 + 1.618, -1.618)

    # Create the needed initial parameters for the System program.
    bar_length = 1.618 + 1.618
    string_length = 2
    nodeArray: np.array(N.Node) = np.array([node1, node2, node3, node4, node5, node6, node7, node8, node9, node10, node11, node12])
    allCoords_orig: np.ndarray[np.ndarray[float]] = np.array([[], [], []])
    nextNodeArray: List[N.Node] = []
    allCoordsRotPureCoords: np.ndarray[np.ndarray[float]] = np.array([[], [], []])
    lever_unit_arms = []
    rc_over_rms = []

    # Moving system so it begins on its base.

    interations = 29

    # Figures 4 and 5 details
    start_degree = 21

    # Figures 6 and 7 interations
    # start_degree = 49
    for j in range(interations):
        allCoords = np.array([[], [], []])
        allCoordsRotPureCoords = np.array([[], [], []])
        nextNodeArray = []
        nodeArray = np.array([node1, node2, node3, node4, node5, node6, node7, node8, node9, node10, node11, node12])
        for i in range(len(nodeArray)):
            allCoords = np.append(allCoords, np.array([nodeArray.item(i).getCoords()]).T, axis=1)

            rotatedCoords: np.ndarray[np.ndarray[float]] = CommonMatrixOperations.rotX(nodeArray.item(i).getCoords(), DEGREES_TO_START_FLAT)

            newNode: N.Node = N.Node(rotatedCoords.item(0), rotatedCoords.item(1), rotatedCoords.item(2))

            # Used to create an initial spiral configuration
            # rotatedCoords: np.ndarray[np.ndarray[float]] = CommonMatrixOperations.rotZ(newNode.getCoords(), 48)
            # newNode: N.Node = N.Node(rotatedCoords.item(0), rotatedCoords.item(1), rotatedCoords.item(2))
            #
            # rotatedCoords: np.ndarray[np.ndarray[float]] = CommonMatrixOperations.rotY(newNode.getCoords(), 47)
            # newNode: N.Node = N.Node(rotatedCoords.item(0), rotatedCoords.item(1), rotatedCoords.item(2))
            #
            # rotatedCoords: np.ndarray[np.ndarray[float]] = CommonMatrixOperations.rotX(newNode.getCoords(), -24)
            # newNode: N.Node = N.Node(rotatedCoords.item(0), rotatedCoords.item(1), rotatedCoords.item(2))
            #
            # rotatedCoords: np.ndarray[np.ndarray[float]] = CommonMatrixOperations.rotY(newNode.getCoords(),-23.9)
            # newNode: N.Node = N.Node(rotatedCoords.item(0), rotatedCoords.item(1), rotatedCoords.item(2))
            #
            # rotatedCoords: np.ndarray[np.ndarray[float]] = CommonMatrixOperations.rotZ(newNode.getCoords(), 8)
            # newNode: N.Node = N.Node(rotatedCoords.item(0), rotatedCoords.item(1), rotatedCoords.item(2))
            #
            # rotatedCoords: np.ndarray[np.ndarray[float]] = CommonMatrixOperations.rotY(newNode.getCoords(),20)
            # newNode: N.Node = N.Node(rotatedCoords.item(0), rotatedCoords.item(1), rotatedCoords.item(2))
            # End spiral config initialization (needs better tuning)

            # START ROTATED POSITION
            rotatedCoords: np.ndarray[np.ndarray[float]] = CommonMatrixOperations.rotY(newNode.getCoords(), 120)
            newNode: N.Node = N.Node(rotatedCoords.item(0), rotatedCoords.item(1), rotatedCoords.item(2))
            rotatedCoords: np.ndarray[np.ndarray[float]] = CommonMatrixOperations.rotX(newNode.getCoords(), (start_degree - j))
            newNode: N.Node = N.Node(rotatedCoords.item(0), rotatedCoords.item(1), rotatedCoords.item(2))

            nextNodeArray.append(newNode)
            allCoordsRotPureCoords = np.append(allCoordsRotPureCoords, np.array([rotatedCoords]).T, axis=1)

        COM = CalcSystemProperties.findCOM(allCoordsRotPureCoords.T)
        for i in range(len(nextNodeArray)):
            current_xy = nextNodeArray[i].getCoords()
            nextNodeArray[i].changeCoords(current_xy[0] - COM[0, 0], current_xy[1] + 1, current_xy[2] - COM[2, 0])
        nodeArray = np.array(nextNodeArray)

        nodesOfInterest: List[int] = [1, 3, 7, 8, 10, 12]  # For the Parallel Best Case.
        # nodesOfInterest: List[int] = [2, 4, 5, 6, 9, 11] # For the Parallel Best move down hill.

        # nodesOfInterest: List[int] = [2, 4, 5, 8, 9, 11]  # This is for the Parallel Worst Case
        # nodesOfInterest: List[int] = [9,7,3,11,8,1]  #This is for the spiral case

        # Be sure to change the line calculated about in the projectPlot code.
        leverage_data = plot.projectionPlot(nodeArray, nodesOfInterest, "Parallel Best Case", trianglePoints=[1, 3, 11], show_plot=False)

        # For figures 4,5
        lever_unit_arm = leverage_data[0] / bar_length
        rc_over_rm = leverage_data[1]

        #For figs 6,7
        # lever_unit_arm = -leverage_data[0] / bar_length
        # rc_over_rm = -leverage_data[1]

        print(lever_unit_arm)
        print(rc_over_rm)
        lever_unit_arms.append(lever_unit_arm)
        rc_over_rms.append(rc_over_rm)

    # This was used for figures 4 and 5.
    plt.plot(range(-start_degree, -(start_degree - interations)), rc_over_rms)
    plt.xlabel("Slope to remain stationary on (deg)", rotation=0, fontsize=10, labelpad=5)
    plt.ylabel(r'$\frac{r_c}{\Sigma r_m}$', rotation=0, fontsize=15, labelpad=15)
    plt.yscale('log')
    plt.show()
    plt.xlabel("Slope to remain stationary on (deg)", rotation=0, fontsize=10, labelpad=5)
    plt.ylabel(r"$\frac{\Sigma r_m}{b_l}$", rotation=0, fontsize=15, labelpad=15)
    plt.plot(range(-start_degree, -(start_degree - interations)), lever_unit_arms)
    plt.show()

    COM = CalcSystemProperties.findCOM(allCoordsRotPureCoords.T)
    for i in range(len(nextNodeArray)):
        current_xy = nextNodeArray[i].getCoords()
        nextNodeArray[i].changeCoords(current_xy[0] - COM[0, 0], current_xy[1], current_xy[2] - COM[2, 0])

    stringConnections: np.ndarray[np.ndarray[float]] = np.array(
        [[1, 3], [1, 5], [1, 6], [1, 9], [1, 10], [2, 4], [2, 5], [2, 6], [2, 11], [2, 12], [3, 7], [3, 8],
         [3, 9], [3, 10], [4, 7], [4, 8], [4, 11], [4, 12], [5, 6], [5, 9], [5, 11], [6, 10], [6, 12], [7, 8],
         [7, 9], [7, 11], [8, 10], [8, 12], [9, 11], [10, 12]])
    barConnections: np.ndarray[np.ndarray[float]] = np.array([[1, 2], [3, 4], [5, 7], [6, 8], [9, 10], [11, 12]])

    # Creates the system that is being analyzed based off the nodes.
    system: S = S.System(barConn=barConnections, barMaterial='Steel', nodeArray=nodeArray, stringConn=stringConnections, stringMaterial='Steel')

    # Gives a basic plot of the system in 3D
    plot.basicPlot(nodeArray, system.getStringConn(), system.getBarConn())

    pinnedNodes: List[int] = []
    system.setPinned(pinnedNodes)

    # These are the values that are returned from the KConvert file.  Declared beforehand so type hinting could be accomplished.
    nNew: np.ndarray[np.ndarray[float]]
    cbNew: np.ndarray[np.ndarray[float]]
    csNew: np.ndarray[np.ndarray[float]]
    P: np.ndarray[np.ndarray[float]]
    D: np.ndarray[np.ndarray[float]]
    nodeConstraints: List[List[int]]

    kConvert: tkc.tensegrityKConvert = tkc.tensegrityKConvert(nodeArray, system.getBarConnMat(), system.getStringConnMat(), pinnedNodes)
    nNew, cbNew, csNew, P, D, nodeConstraints = kConvert.returnNeededValues()

    print("Converted Class K # of nodes: " + str(len(nNew[0])))
    print("Class k node constraints:")
    for i in range(0, len(nodeConstraints)):

        if 1 < len(nodeConstraints[i]):
            print("Coincident nodes: ", str(nodeConstraints[i]))

    # Specify resetting string lengths.
    # Here we are setting  every string rest length to 70% of the given length.
    s0Percent: np.ndarray[np.ndarray[float]] = np.append(np.array([np.arange(1, len(csNew) + 1)]), np.array([.7 * np.ones(len(csNew), dtype=int)]), axis=0).T
    s0: np.ndarray[float] = tkc.TensegPercentTo_s0(nNew, csNew, s0Percent)

    # Add velocity
    V: np.ndarray[np.ndarray[float]] = np.zeros([3, 12])

    # Sets the force array as based on the total force in each cartesian dimension on the node.
    # With percentage control, can either add total weight to one bar node in the pair, or split it between the two, shouldn't make a difference.
    W: np.ndarray[np.ndarray[float]] = np.zeros([3, len(nNew[0])])

    # These need to be relatively low for the accelerometer state predictor to work. But not too low is needed, performance between 1 and 10 seems about the
    # same.
    W[1, 0] = -10
    W[1, 1] = -10
    W[1, 2] = -10
    W[1, 3] = -10
    W[1, 4] = -10
    W[1, 5] = -10
    W[1, 6] = -10
    W[1, 7] = -10
    W[1, 8] = -10
    W[1, 9] = -10
    W[1, 10] = -10
    W[1, 11] = -10

    # This is the code to actually run the simulation. Keep testing to try to figure out why this is angry. Probs unit conversions or something.
    classKTest: ckt.ClassK_Test = ckt.ClassK_Test(nNew, cbNew, csNew, system, P, D, s0, V, W, dt=.001, tf=10, axisLength=3)
    classKTest.TensegSimClassKOpen(damping=2, updateForces=True, updateGround=True, useController=True)
    name: str = 'debug'

    # plot.plotPath(classKTest.nodeHist, "thisPath", classKTest.targets)
    SaveData.animateMotion(classKTest.axisLength, classKTest.system.barConn, classKTest.dt, classKTest.nodeHist, classKTest.system.stringConn, classKTest.tf,
                           name + ".mp4")
    # SaveData.sendInfoToCSVFile(classKTest.forcesOverTime, name + '.csv', classKTest.stateCoords)
