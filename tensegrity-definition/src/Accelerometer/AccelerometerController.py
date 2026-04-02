import numpy as np

import src.Accelerometer.AccelerometerSimulator as Accel
from src.TensegritySystem import Controller, Nodes as N
from src.Utils import CalcSystemProperties, CommonMatrixOperations

"""
This class is essentially the same thing as the Controller Class, except uses exclusively the accelerometer to make judgements about control. Inherits from Controller.py.
"""


class AccelerometerController(Controller.Controller):
    def __init__(self, barConnections, stringConnections, desiredNodesToGoTo, nodes, stringConnectionsSimple):
        # TODO.
        """
        Initializes the controller with the needed values. All the parameters above are like those in the ClassK_Test.
        :param barConnections:
        :param:
        :param:
        :param:
        :param:
        """
        super().__init__(barConnections, stringConnections, desiredNodesToGoTo, nodes, stringConnectionsSimple)
        self.controllerType = 'accelerometer controller'
        self.previousBaseNodes = [1, 3, 11]
        self.totalVectors = 0
        self.extrapolatedPosition = np.array([0., -0.57732093])  # the x and z location of the system, the y component does not matter.

    def extrapolatePosition(self, previousBase, currentBase, rotatedCoords):
        """
        This method will keep track of the predicted position of the system by adding in the predicted movement of the system to the previous predicted position of the system. It will only keep
        track of the x, z position of the centroid. That position will then be added to the predicted rotated position of the base nodes of the model from the accelerometer rotation.
        :param: previousBase:  the base of the previous time step
        :param: currentBase:  The current base of the system
        :param: rotatedCoords: The coordinates as rotated by the rotation matrix predicted by the accelerometers.
        """

        # TODO: may have to add in logic if rotatedSlope = 0, or if it is inf for some reason.
        sameNodes = []

        # gets the nodes the system rotated about, so that the rotation vector can be calculated.
        for i in range(len(previousBase)):
            for j in range(len(currentBase)):
                if previousBase[i] == currentBase[j]:
                    sameNodes.append(previousBase[i])

        if 3 == len(sameNodes):
            return
        vectorRotatedAbout = [rotatedCoords[0][sameNodes[0]] - rotatedCoords[0][sameNodes[1]], rotatedCoords[2][sameNodes[0]] - rotatedCoords[2][sameNodes[1]]]

        # find the new node that acts as the base
        nodeRotatedTo = -1
        differentNode = -1
        for i in range(len(currentBase)):
            if currentBase[i] != sameNodes[0] and currentBase[i] != sameNodes[1]:
                nodeRotatedTo = currentBase[i]
                differentNode = currentBase[i - 1]

        # calculate the vector perpendicular to the rotated vector.
        rotatedSlope = vectorRotatedAbout[1] / vectorRotatedAbout[0]
        negRecipSlope = -1 / rotatedSlope

        if rotatedSlope == 0:
            distanceVector = np.array([rotatedCoords[0][nodeRotatedTo] - rotatedCoords[0][differentNode], 0]) * .6
        elif rotatedSlope == float('nan'):
            distanceVector = np.array([0, rotatedCoords[2][nodeRotatedTo] - rotatedCoords[2][differentNode]]) * .6
        else:
            # calculate the point where the perpendicular vector going through the nodeRotatedTo intersects with the vector rotated about - going through its base points.
            A = np.array([[rotatedSlope, -1], [negRecipSlope, -1]])
            b = np.array([rotatedSlope * rotatedCoords[0][sameNodes[0]] - rotatedCoords[2][sameNodes[0]],
                          negRecipSlope * rotatedCoords[0][nodeRotatedTo] - rotatedCoords[2][nodeRotatedTo]])

            intercept = np.linalg.inv(A).dot(b)

            # find the distance vector between current point and the vector point
            distanceVector = np.array([rotatedCoords[0][nodeRotatedTo] - intercept[0], rotatedCoords[2][nodeRotatedTo] - intercept[1]]) * .6

            # add the distance vector to the already stored predicted location.
        self.extrapolatedPosition += distanceVector

    # def getBase(self): # DEFUNCT
    #     """
    #     Will return the 3 string vectors connecting lowest nodes, and those nodes, for the system(which is considered the base). Based off these vectors, the functions below will choose which
    #     strings to pivot on and thereby choose the next node to go to.
    #     """
    #
    #     # This is where the accelerometer simulator will go.  So will call the Accelerometer Simulator, get the accelerometer
    #     # vector, and then extrapolate the base.
    #     accel = Accel.AccelerometerSimulation()
    #
    #     # this should give us the relative place of similar nodes that have moved.  Probs need to move the final nodes to the centroid.
    #     # only need to do this because simulating the accelerometer.  In the real system, won't know where the nodes are. Use the intialCOM to alter the initial nodes too.
    #
    #     # The reason the I use this COM variable, and not something else that I calculated is because this portion of the code is exclusively meant to simulate the accelerometer.  As such, I am using
    #     # information that would not be available to the system to simulate what would actually be available to the system.  As such, the information that the system wouldn't have is only used to
    #     # simulate information the system would have, not not in any way that would invalidate this simulation.
    #     COM = CalcSystemProperties.findCOM(self.nodes.T)
    #
    #     psiAverage = []
    #     thetaAverage = []
    #     phiAverage = []
    #
    #     # Currently has about 90-95% accuracy.
    #     # TODO: move into own function
    #     for i in range(4):
    #         for j in range(4):
    #             for k in range(4):
    #                 # returns what our accelometers would be based on how the system rotated.  Uses that rotation to then rotate the accelerometer vectors.
    #                 accelVector1, accelVector2, accelVector3 = accel.calcNewXYZ((np.array([self.initialNodes.T[i]]).T - self.initialCOM).T[0],
    #                                                                             (np.array([self.nodes.T[i]]).T - COM).T[0],
    #                                                                             (np.array([self.initialNodes.T[i + 4]]).T - self.initialCOM).T[0],
    #                                                                             (np.array([self.nodes.T[i + 4]]).T - COM).T[0],
    #                                                                             (np.array([self.initialNodes.T[i + 8]]).T - self.initialCOM).T[0],
    #                                                                             (np.array([self.nodes.T[i + 8]]).T - COM).T[0])
    #
    #                 # currently the same as those calculated in the calcNewXYZ function.
    #                 psi, theta, phi = accel.determineAngles(np.array([0, -1, 0]), np.array(accelVector1).T[0], np.array([-1, 0, 0]),
    #                                                         np.array(accelVector2).T[0], np.array([0, 0, -1]),
    #                                                         np.array(accelVector3).T[0])
    #
    #                 psiAverage.append(psi)
    #                 thetaAverage.append(theta)
    #                 phiAverage.append(phi)
    #
    #     # now that I have the angles, I need to rotate the system.  Once the system is rotated, the above find base formula works.
    #     allCoordsRotPureCoords1 = np.array([[], [], []])
    #     phiAverageNum = sum(phiAverage) / len(phiAverage)
    #     thetaAverageNum = sum(thetaAverage) / len(thetaAverage)
    #     psiAverageNum = sum(psiAverage) / len(psiAverage)
    #
    #     # TODO: end of function to move.
    #
    #     # IDK if I can do this, bc the COM and the extrapolated position are not equivalant at this point in time, bc the extrapolated distance cannot be added until
    #     # after the rotation has been calculated.
    #     # COM = np.array([[self.extrapolatedPosition[0],1, self.extrapolatedPosition[1]]]).T
    #
    #     for i in range(len(self.initialNodes.T)):
    #         rotatedCoords1 = CommonMatrixOperations.rotX(np.array([self.initialNodes.T[i]]).T - self.initialCOM, phiAverageNum)  # after movement
    #         newNode = N.Node(rotatedCoords1[0], rotatedCoords1[1], rotatedCoords1[2])  # after movement
    #
    #         rotatedCoords1 = CommonMatrixOperations.rotY(newNode.getCoords(), thetaAverageNum)  # after movement
    #         newNode = N.Node(rotatedCoords1[0], rotatedCoords1[1], rotatedCoords1[2])  # after movement
    #
    #         rotatedCoords1 = CommonMatrixOperations.rotZ(newNode.getCoords(), psiAverageNum)  # next movement
    #         allCoordsRotPureCoords1 = np.append(allCoordsRotPureCoords1, rotatedCoords1, axis=1)  # don't need the +COM here bc of how the rotations works.
    #
    #     # print("these are the lowest nodes from the abs values shown in the simulation.")
    #     # # print(nodes)
    #     # print(nodeNums)
    #
    #     # This actually works really well, there may be a few bases that confuses it(2,8,6) vs (2,8,0), but once it rolls, the system is resest and it does a good job
    #     # figuring out its position, would say accuracy between 90% - 95%, might be possible to tune higher.
    #     # TODO: move into own function
    #     nodeChangeCounter = 0  # tracks the nodes that are alike.  If all 3 the same as the previous, then it didn't roll, up the mult,      if   2 the same, normal roll, if 1 or less, momentum roll.
    #     seemsLow = False
    #     while not seemsLow:
    #         nodeChangeCounter += 1
    #         lowest1 = float('inf')
    #         lowest2 = float('inf')
    #         lowest3 = float('inf')
    #         node1Acclerometer = None
    #         node2Acclerometer = None
    #         node3Acclerometer = None
    #         nodeNum1Acclerometer = None
    #         nodeNum2Acclerometer = None
    #         nodeNum3Acclerometer = None
    #
    #         for i in range(len(self.previousBaseNodes)):
    #             if allCoordsRotPureCoords1[1][self.previousBaseNodes[i]] < lowest1:
    #                 lowest2 = lowest1
    #                 node2Acclerometer = node1Acclerometer
    #                 nodeNum2Acclerometer = nodeNum1Acclerometer
    #                 lowest1 = allCoordsRotPureCoords1[1][self.previousBaseNodes[i]]
    #                 node1Acclerometer = allCoordsRotPureCoords1.T[self.previousBaseNodes[i]]
    #                 nodeNum1Acclerometer = self.previousBaseNodes[i]
    #             elif allCoordsRotPureCoords1[1][self.previousBaseNodes[i]] < lowest2:
    #                 lowest2 = allCoordsRotPureCoords1[1][self.previousBaseNodes[i]]
    #                 node2Acclerometer = allCoordsRotPureCoords1.T[self.previousBaseNodes[i]]
    #                 nodeNum2Acclerometer = self.previousBaseNodes[i]
    #
    #         possilbeNodes = self.getPossibleNodes(nodeNum1Acclerometer, nodeNum2Acclerometer)
    #
    #         for i in range(len(possilbeNodes)):
    #             if allCoordsRotPureCoords1[1][possilbeNodes[i]] < lowest3:
    #                 lowest3 = allCoordsRotPureCoords1[1][possilbeNodes[i]]
    #                 node3Acclerometer = allCoordsRotPureCoords1.T[possilbeNodes[i]]
    #                 nodeNum3Acclerometer = possilbeNodes[i]
    #
    #         nodesAcclerometer = [node1Acclerometer, node2Acclerometer, node3Acclerometer]
    #         nodeNumsAcclerometer = [nodeNum1Acclerometer, nodeNum2Acclerometer, nodeNum3Acclerometer]
    #
    #         self.extrapolatePosition(self.previousBaseNodes, nodeNumsAcclerometer, allCoordsRotPureCoords1)
    #         self.previousBaseNodes = nodeNumsAcclerometer
    #
    #         allLow = True
    #         for i in range(len(nodeNumsAcclerometer)):
    #             if allCoordsRotPureCoords1[1][
    #                 nodeNumsAcclerometer[i]] > .15:  # This number is fairly arbitrary number, can change for performance, works really well currently though.
    #                 allLow = False
    #
    #         if allLow:
    #             seemsLow = True
    #         # TODO: end of function to move.
    #
    #     if nodeChangeCounter > 1 and self.previousBase != [0, 0, 0]:
    #         print("THE SYSTEM ROLLED")
    #         self.middleMult = 1
    #         self.multCounter = 0
    #     elif nodeChangeCounter == 0:
    #         self.multCounter += 2
    #         self.middleMult = self.multCounter
    #     else:
    #         self.middleMult = 1
    #         self.multCounter = 0
    #
    #     self.previousBase = nodeNumsAcclerometer
    #
    #     # since the rotation matrix no longer is transformed by the COM originally, nodeAccelerometer needs to be changed by the new extrapolated position.  The y value of the distance should
    #     # remain unchanged, so hopefully it is not important in this part of the algorithm.
    #     for i in range(len(nodesAcclerometer)):
    #         nodesAcclerometer[i][0] += self.extrapolatedPosition[0]
    #         nodesAcclerometer[i][1] += 1.53
    #         nodesAcclerometer[i][2] += self.extrapolatedPosition[1]
    #
    #     self.firstNode = nodesAcclerometer
    #     self.firstNodesNums = nodeNumsAcclerometer

    def getBase(self, initialState, accelerationVector):
        # TODO: DOING THIS BREAKS CODE, MAY NEED TO FIX IF DEBUGGING IS NEEDED.
        """
        Will return the 3 string vectors connecting lowest nodes, and those nodes, for the system(which is considered the base). Based off these vectors, the functions below will choose which
        strings to pivot on and thereby choose the next node to go to.
        """

        arr = initialState.T.dot(np.array([accelerationVector]).T)
        ind = np.argpartition(arr.T, 3)[:3]

        self.firstNodesNums = ind

    def getPossibleNodes(self, node1, node2):
        """
        # TODO
        :param node1:
        :param node2:
        :return:
        """
        node1Conns = []
        node2Conns = []
        for i in range(0, len(self.stringConnsSimple)):
            if self.stringConnsSimple[i][0] == node1 + 1:
                node1Conns.append(self.stringConnsSimple[i][1] - 1)

            if self.stringConnsSimple[i][1] == node1 + 1:
                node1Conns.append(self.stringConnsSimple[i][0] - 1)

            if self.stringConnsSimple[i][0] == node2 + 1:
                node2Conns.append(self.stringConnsSimple[i][1] - 1)

            if self.stringConnsSimple[i][1] == node2 + 1:
                node2Conns.append(self.stringConnsSimple[i][0] - 1)

        similarNodes = []
        for i in range(len(node1Conns)):
            for j in range(len(node2Conns)):
                if node1Conns[i] == node2Conns[j]:
                    similarNodes.append(node2Conns[j])

        return similarNodes

    def setTarget(self, theTarget):
        """
        Sets the target variable as instructed.
        :param theTarget:
        :return: None
        """
        self.target = theTarget
