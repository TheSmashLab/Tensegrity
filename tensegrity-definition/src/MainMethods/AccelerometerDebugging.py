import numpy as np
from typing import List

import src.Accelerometer.AccelerometerSimulator as sim
import src.TensegritySystem.Nodes as N
from src.TensegritySystem import Systems as S
from src.Utils import CalcSystemProperties, CommonMatrixOperations, TensegrityPlotter as plot


DEGREES_TO_START_FLAT: float = -41.80901 / 2
STRING_LENGTH: float = ((1-1.618)**2 + 1.618**2+1)**(1/2)


def main():
    # 1 6 10 base
    accel1 = np.array([-0.00, 1.00, 0.01])

    # 2 4 12 base
    # accel1 = np.array([-9.43, -2.19, -1.86]) / np.linalg.norm(np.array([-2.19, -1.86, -9.43]))

    # 2 6 12
    # accel1 = np.array([3.97, 0.37, -9.12]) / np.linalg.norm(np.array([3.97, 0.37, -9.12]))

    # 2 5 6
    # accel1 = np.array([-6.33, 3.01, 7.06])

    # # 1 5 6
    accel1 = np.array([1.16, 8.13, 6.06]) / np.linalg.norm(np.array([1.16, 8.13, 6.06]))

    # # 1 5 9 base
    # accel1 = np.array([5.58, 3.59, 7.41])/np.linalg.norm(np.array([5.58, 3.59, 7.41]))

    # 6, 10, 12

    accel1 = np.array([1.16, 8.13, 6.06]) / np.linalg.norm(np.array([1.16, 8.13, 6.06]))

    angle = np.arccos(np.sqrt(3)/3)

    # accelB2 = CommonMatrixOperations.rotX(accelB1,90) #Doesn't work bc won't make vectors perfectly orthogonal.
    # accelB3 = CommonMatrixOperations.rotY(accelB1,90)

    # accelB2 = np.array([-9.34, -2.57, -1.58]) / np.linalg.norm(np.array([-9.34, -2.57, -1.58]))
    # accelB3 = np.array([-1.85, -9.50, -2.02]) / np.linalg.norm(np.array([-1.85, -9.50, -2.02]))


    accelSim = sim.AccelerometerSimulation()


    # Make the initial nodes for the system by calling the Node class
    node1: N.Node = N.Node(1, 1.618, 0)
    node2: N.Node = N.Node(1, -1.618, 0)
    node3: N.Node = N.Node(-1, 1.618, 0)
    node4: N.Node = N.Node(-1, -1.618, 0)
    node5: N.Node = N.Node(1.618, 0, 1)
    node6: N.Node = N.Node(1.618, 0, -1)
    node7: N.Node = N.Node(-1.618, 0, 1)
    node8: N.Node = N.Node(-1.618, 0, -1)
    node9: N.Node = N.Node(0, 1, 1.618)
    node10: N.Node = N.Node(0, 1, -1.618)
    node11: N.Node = N.Node(0, -1, 1.618)
    node12: N.Node = N.Node(0, -1,  -1.618)

    stringConnections: np.ndarray[np.ndarray[float]] = np.array(
        [[1, 3], [1, 5], [1, 6], [1, 9], [1, 10], [2, 4], [2, 5], [2, 6], [2, 11], [2, 12], [3, 7], [3, 8],
         [3, 9], [3, 10], [4, 7], [4, 8], [4, 11], [4, 12], [5, 6], [5, 9], [5, 11], [6, 10], [6, 12], [7, 8],
         [7, 9], [7, 11], [8, 10], [8, 12], [9, 11], [10, 12]])
    barConnections: np.ndarray[np.ndarray[float]] = np.array([[1, 2], [3, 4], [5, 7], [6, 8], [9, 10], [11, 12]])


    # Create the needed initial parameters for the System program.
    nodeArray: np.array(N.Node) = np.array([node1, node2, node3, node4, node5, node6, node7, node8, node9, node10, node11, node12])
    system: S = S.System(barConn=barConnections, barMaterial='Steel', nodeArray=nodeArray, stringConn=stringConnections, stringMaterial='Steel')

    # plot.basicPlot(nodeArray, system.getStringConn(), system.getBarConn())

    allCoords: np.ndarray[np.ndarray[float]] = np.array([[], [], []])
    nextNodeArray: List[N.Node] = []
    allCoordsRotPureCoords: np.ndarray[np.ndarray[float]] = np.array([[], [], []])

    # Moving system so it begins on its base.
    for i in range(len(nodeArray)):
        allCoords = np.append(allCoords, np.array([nodeArray.item(i).getCoords()]).T, axis=1)

        # 2, 4, 12 base.
        # rotatedCoords: np.ndarray[np.ndarray[float]] = CommonMatrixOperations.rotX(nodeArray.item(i).getCoords(), DEGREES_TO_START_FLAT)

        # 2,5,6 base
        # rotatedCoords: np.ndarray[np.ndarray[float]] = CommonMatrixOperations.rotZ(nodeArray.item(i).getCoords(), DEGREES_TO_START_FLAT*3.3)

        # 1,6,10 base
        rotatedCoords: np.ndarray[np.ndarray[float]] = CommonMatrixOperations.rotZ(nodeArray.item(i).getCoords(), DEGREES_TO_START_FLAT*6.4)
        newNode: N.Node = N.Node(rotatedCoords.item(0), rotatedCoords.item(1), rotatedCoords.item(2))
        rotatedCoords: np.ndarray[np.ndarray[float]] = CommonMatrixOperations.rotX(newNode.getCoords(), DEGREES_TO_START_FLAT*1.7)
        newNode: N.Node = N.Node(rotatedCoords.item(0), rotatedCoords.item(1), rotatedCoords.item(2))

        nextNodeArray.append(newNode)
        allCoordsRotPureCoords = np.append(allCoordsRotPureCoords, np.array([rotatedCoords]).T, axis=1)

    # plot.basicPlot(np.array(nextNodeArray), system.getStringConn(), system.getBarConn())

    # rotationTestCoords = R.dot(allCoordsRotPureCoords)
    # print(R)
    # print(rotationTestCoords[1])
    #
    # thetax = (np.arctan2(R[2, 1], R[2, 2]))
    # thetay = (np.arctan2(-R[2, 0], np.sqrt(R[2, 1] ** 2 + R[2, 2] ** 2)))
    # thetaz = (np.arctan2(R[1, 0], R[0, 0]))

    # Down here will be the new way I am going to implement base guessing.
    # SUDO CODE:
    # For every item it rotated Coords:
    # check the dot product of the current accelerometer reading with the positions of the original nodes
    # select th three highest dot products at the new base.

    # This is the new "getBase code."
    accel1 = CommonMatrixOperations.rotY(accel1, 150) # So this is a correction factor to get the accelerometer to match the model.
    arr = allCoordsRotPureCoords.T.dot(np.array([accel1]).T)
    ind = np.argpartition(arr.T, 3)[:3]
    # plot.basicPlot(np.array(nextNodeArray), system.getStringConn(), system.getBarConn())

    # Now we are going to back out a rotation matrix
    # The steps to take are as follows:
    # 1. Assume each rotation occurs sequentially. For this, that will mean keeping track of old nods and new nodes, and then finding how it rotated.
    # 2. Find the 2 nodes that are different between the current and previous steps
    # 3. Find the 2D vector approximation of the vector between the two constant nodes.
    # 4. Find the perpendicular unit vector to that vector on the Z plane.
    # 5. Find the midpoint of the 2 constant nodes
    # 6. Use the current location of the current node and the midpoint to determine if the perp vector is facing the correct way.
    # 7. Set the x,z coordinates of the new node to the mid-point of the 2 nodes, plus the perpendicular vector times the length of the string* sqrt(3)/2 (
    #       assuming equilateral)
    # 8. Set the y coordinate to the average of the y coordinates of the 2 constant nodes.
    # 9. Find the centroid of the current nodes and the new node now located on the ground.
    # 10. Subtract out the centroid to move the model to be located about the origin again.
    # 11. Use the new points as well as the old points to find the rotation matrix that makes that transformation possible.
    # NOTES: This method will need to keep track of: old node position, original system position, and new node position information.
    #        This method will assume that the rotation matrix represents the rotation for the t-1 position to the current position, not from original
    #        position to current position, however, adding the rotation matrix to describe original position to current position would be simple,
    #        since you would represent the original R as I, and then multiple that R by the new calculated rotation to get the total rotation.

    # INITIAL ROT SETUP IMPLEMENTATION:

    # Step 2.
    indPrev = np.array([1, 6, 10])
    uniqueNodePrev = np.setdiff1d(indPrev, ind[0,:3] + 1)
    uniqueNodeCurr = np.setdiff1d(ind[0,:3] + 1, indPrev)
    print(uniqueNodePrev)
    print(uniqueNodeCurr)

    # Step 3
    sameNodes = np.setdiff1d(indPrev, uniqueNodePrev)
    sameNodeConnection = np.array([allCoordsRotPureCoords.T[sameNodes[1]-1][0]-allCoordsRotPureCoords.T[sameNodes[0]-1][0],
                                   allCoordsRotPureCoords.T[sameNodes[1]-1][2]-allCoordsRotPureCoords.T[sameNodes[0]-1][2]])
    print(sameNodeConnection)

    # Step 4
    perp = np.array([-sameNodeConnection[1], sameNodeConnection[0]])
    unitperp = perp/np.linalg.norm(perp)

    print(unitperp)

    # Step 5
    midpoint = np.array([(allCoordsRotPureCoords.T[sameNodes[1]-1][0]+allCoordsRotPureCoords.T[sameNodes[0]-1][0])/2,
                         (allCoordsRotPureCoords.T[sameNodes[1]-1][2]+allCoordsRotPureCoords.T[sameNodes[0]-1][2])/2])
    print(midpoint)

    # Step 6
    directionVector = np.array([allCoordsRotPureCoords.T[uniqueNodeCurr[0]-1][0] - midpoint[0], allCoordsRotPureCoords.T[uniqueNodeCurr[0]-1][2] - midpoint[1]])

    if 0 > directionVector.dot(unitperp):
        unitperp = -1 * unitperp

    print(unitperp)

    # Step 7/8
    displacement = unitperp*STRING_LENGTH
    currentLoc = np.array([midpoint[0] + displacement[0], (allCoordsRotPureCoords.T[sameNodes[1]-1][1]+allCoordsRotPureCoords.T[sameNodes[0]-1][1])/2,
                            midpoint[1] + displacement[1]])
    print(currentLoc)

    # Step 9
    # TODO: WILL NEED TO SAVE CURRENT NODES SOMEWHERE FOR THIS TO BE ABLE TO TRACK MOVEMENT. FOR NOW WILL JUST NOT REINITIALIZE.
    currentNodes = np.array([allCoordsRotPureCoords.T[sameNodes[0]-1], allCoordsRotPureCoords.T[sameNodes[1]-1], currentLoc])
    COM = CalcSystemProperties.findCOM(currentNodes)
    print(currentNodes)
    print(COM)
    COM[1] = 0

    # Step 10
    movedToOriginNodes = (currentNodes.T-COM).T
    print(movedToOriginNodes)

    # Step 11
    print()
    print(currentNodes[0])
    print(movedToOriginNodes[0])
    print(currentNodes[1])
    print(movedToOriginNodes[1])
    print(allCoordsRotPureCoords.T[uniqueNodeCurr[0]-1])
    print(movedToOriginNodes[2])

    print()

    R = accelSim.determineAngles(currentNodes[0], movedToOriginNodes[0], currentNodes[1], movedToOriginNodes[1], allCoordsRotPureCoords.T[uniqueNodeCurr[0]-1],
                                 movedToOriginNodes[2])

    print(R)

# TODO: WHEN R IS EXTRACTED, ALSO UPDATE STATE ESTIMATE. THEN THE ESTIMATION OF THE STATE OF THE SYSTEM WILL BE EXTRACTED BY FIRST ROTATING THE SYSTEM,
#  AND THEN ADDING THE ESTIMATION (which would be: the calculated displacement - the original xy location of the new node) TO THE RESULT OF THE ROTATION. IF
#  A KALMAN FILTER IS IMPLEMENTED ON THIS SYSTEM, THIS WOULD SERVE AS THE AX+BU+epsilon PORTION OF THE ESTIMATION FILTER.


if __name__ == "__main__":
    main()
