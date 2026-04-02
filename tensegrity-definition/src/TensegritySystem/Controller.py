import numpy as np
import random
from typing import List, Tuple

CONTROLLER_OFFSET: int = 100
CONTROLLER_RECALC: int = 3000


class Controller:
    def __init__(self, barConnections: np.ndarray[np.ndarray[float]], nodes: np.ndarray[np.ndarray[float]], stringConnections: np.ndarray[np.ndarray[float]],
                 stringConnectionsSimple: np.ndarray[np.ndarray[float]], desiredNodesToGoTo: np.ndarray[int] = None):
        """
        Initialized the controller class
        :param barConnections: An array containing information about the bar connection is a square matrix containing only 1s and 0s.
        :param stringConnections:  An array containing information about the string connection is a square matrix containing only 1s and 0s.
        :param desiredNodesToGoTo: An Array contain a sequence of nodes to go to, optional.
        :param nodes:
        :param stringConnectionsSimple:
        """
        self.barConns: np.ndarray[np.ndarray[float]] = barConnections
        self.chooser: int = 0
        self.counter: int = 0
        self.desiredNodesToGoTo: np.ndarray[int] = desiredNodesToGoTo
        self.nextNode: int = 11
        self.nodes: np.ndarray[np.ndarray[float]] = nodes
        self.stringConns: np.ndarray[np.ndarray[float]] = stringConnections
        self.stringConnsSimple: np.ndarray[np.ndarray[float]] = stringConnectionsSimple
        self.target: List[float] = None
        self.targets: np.ndarray[np.ndarray[float]] = np.array([[], []]).T

        # TODO: to optimize the controller, the following ideas were suggested.
        # Choose the higher related node. - for now neglected.
        # Check which bar has no related nodes - neglected
        # Find the higher node on the bar.- neglected

    def control(self) -> List[float]:
        """
        The controller will choose the node path to get to the desired state, or at the very least the next node to
        go to for movement.  This will probably be complicated and will be somewhat complicated, will probably start by
        just trying to get different combinations of nodes on the ground.  Movement and directional control will come
        later.
        :return: A percentage array of where the masses should be to move to the next node.
        """

        if CONTROLLER_OFFSET == self.counter % CONTROLLER_RECALC:

            # This is if you want to control to a specific node.
            if self.desiredNodesToGoTo is not None:
                self.nextNode = self.desiredNodesToGoTo

            # This is if you want to manually control the movements.
            elif self.target is None:
                if 2 > self.chooser:
                    self.nextNode = self.directionControl(np.array([0, 0, 1]), 'up')
                elif 4 > self.chooser:
                    self.nextNode = self.directionControl(np.array([-1, 0, 0]), 'left')
                elif 6 > self.chooser:
                    self.nextNode = self.directionControl(np.array([0, 0, -1]), 'down')
                else:
                    self.nextNode = self.directionControl(np.array([1, 0, 0]), 'right')

                self.chooser = self.chooser + 1

            # Finally, this is if you want to control to a specific point.
            else:
                # First - get the nodes that are needed(probably self.nodes)
                nodes: List[np.ndarray[np.ndarray[float]]]
                nodes, _ = self.getBase()

                downDist: float = -float('inf')
                leftDist: float = -float('inf')
                rightDist: float = -float('inf')
                upDist: float = -float('inf')

                # Next - find distances from each base nodes to the target node, keeping the largest numbers.
                for i in range(len(nodes)):
                    leftDistTemp: float = self.target[0] - nodes[i][0]
                    rightDistTemp: float = nodes[i][0] - self.target[0]
                    upDistTemp: float = self.target[1] - nodes[i][2]
                    downDistTemp: float = nodes[i][2] - self.target[1]

                    if upDistTemp > upDist:
                        upDist = upDistTemp

                    if downDistTemp > downDist:
                        downDist: float = downDistTemp

                    if rightDistTemp > rightDist:
                        rightDist = rightDistTemp

                    if leftDistTemp > leftDist:
                        leftDist = leftDistTemp

                # If all the distances are positive, then the system has arrived at the target.
                if 0 <= upDist and 0 <= downDist and 0 <= leftDist and 0 <= rightDist:
                    print("arrived at target " + str(self.target))
                    self.makeTarget()
                    print("created new target at " + str(self.target) + " going there now.")
                    return self.control()

                # Then - choose the largest distance
                distanceList: List[int] = list([upDist, downDist, rightDist, leftDist])
                wayToGo: int = distanceList.index(max(distanceList))

                # Finally - roll in direction of the largest distance.
                if 0 == wayToGo:
                    self.nextNode = self.directionControl(np.array([0, 0, 1]), 'up')
                elif 1 == wayToGo:
                    self.nextNode = self.directionControl(np.array([0, 0, -1]), 'down')
                elif 2 == wayToGo:
                    self.nextNode = self.directionControl(np.array([-1, 0, 0]), 'left')
                else:
                    self.nextNode = self.directionControl(np.array([1, 0, 0]), 'right')

        self.counter = self.counter + 1
        return self.goToDesiredNode(self.nextNode)

    def directionControl(self, dotVector: np.ndarray[np.ndarray[float]], direction: str) -> int:
        """
        The definitions below will all chose the next node to go to in a greedy way, by choosing the correct string to pivot around, then using the 2 nodes
        on the end of the string to point to the next node (by choosing the node that both of the base nodes have in common.)

        :param dotVector: the vector corresponding with the desired direction of movement.
        :param direction: the direction that that is desired for the system to move.
        :return: the node that corresponds with the desired direction of movement.
        """
        nodes: List[np.ndarray[np.ndarray[float]]]
        nodeNums: List[int]
        nodes, nodeNums = self.getBase()

        # First, choose the node furthest in the desired direction, one of the strings attached to it will be chosen as the string to rotate about.
        theBestNode: int = 0

        if 'up' == direction or 'down' == direction:
            bestz: float = nodes[0].item(2)
        else:
            bestz: float = nodes[0].item(0)

        for i in range(len(nodes)):
            if 'up' == direction:
                if nodes[i][2] > bestz:
                    theBestNode = i
                    bestz = nodes[i].item(2)

            if 'down' == direction:
                if nodes[i][2] < bestz:
                    theBestNode = i
                    bestz = nodes[i].item(2)

            if 'left' == direction:
                if nodes[i][0] < bestz:
                    theBestNode = i
                    bestz = nodes[i].item(0)

            if 'right' == direction:
                if nodes[i][0] > bestz:
                    theBestNode = i
                    bestz = nodes[i].item(0)

        # Next, choose the string to around, this will be done by choosing the minimum dot product between the string and the vector[0,0,1]
        counter: int = 0
        node1: int = -1
        node2: int = -1
        vector1: np.ndarray[np.ndarray[float]] = np.array([[0], [0], [0]])
        vector2: np.ndarray[np.ndarray[float]] = np.array([[0], [0], [0]])

        for i in range(len(nodes)):
            if i == theBestNode:
                pass
            else:
                if 0 == counter:
                    vector1 = nodes[theBestNode] - nodes[i]
                    counter += 1
                    node1 = i
                else:
                    vector2 = nodes[theBestNode] - nodes[i]
                    node2 = i

        dot1: np.ndarray[np.ndarray[float]] = np.abs(np.array(vector1).dot(dotVector))
        dot2: np.ndarray[np.ndarray[float]] = np.abs(np.array(vector2).dot(dotVector))

        # These two variables represent the other 2 base nodes that are connected to the tensegrity system. theOtherNode paired with the original node make
        # the vector that the system rotates about. theLastNode represents the last node on the base around which rotation will not occur and is needed for
        # future control logic.
        theLastNode: int
        theOtherNode: int

        if dot1 <= dot2:
            theLastNode = node2
            theOtherNode = node1
        else:
            theLastNode = node1
            theOtherNode = node2

        # Once vector is chosen, both nodes to pivot about are known, choose the node that is connected by strings to the 2 chosen nodes.
        theNodeConnects: List[int] = []
        theOtherNodeConnects: List[int] = []

        # This for loop determines which nodes are connected to the node furthest in the desired direction.
        for i in range(len(self.stringConnsSimple)):
            if self.stringConnsSimple[i][0] == nodeNums[theBestNode] + 1:
                theNodeConnects.append(self.stringConnsSimple[i][1])

            if self.stringConnsSimple[i][1] == nodeNums[theBestNode] + 1:
                theNodeConnects.append(self.stringConnsSimple[i][0])

            if self.stringConnsSimple[i][0] == nodeNums[theOtherNode] + 1:
                theOtherNodeConnects.append(self.stringConnsSimple[i][1])

            if self.stringConnsSimple[i][1] == nodeNums[theOtherNode] + 1:
                theOtherNodeConnects.append(self.stringConnsSimple[i][0])

        chosenNode: int = -1

        # Determines which node is connected to both theBestNode and theOtherNode.
        for i in range(len(theNodeConnects)):
            for j in range(len(theOtherNodeConnects)):
                if theNodeConnects[i] == theOtherNodeConnects[j] and theNodeConnects[i] != nodeNums[theLastNode] + 1:
                    chosenNode = theNodeConnects[i]

        return chosenNode

    def getBase(self) -> Tuple[List[np.ndarray[np.ndarray[float]]], List[int]]:
        """
        Will return the 3 string vectors connecting lowest nodes, and those nodes, for the system(which is considered the base).
        Based off these vectors, the functions below will choose which strings to pivot on and thereby choose the next node to go to.

        :return: Tuple of nodes and the node numbers corresponding to the base.
        """
        lowest1: float = float('inf')
        lowest2: float = float('inf')
        lowest3: float = float('inf')
        node1: np.ndarray[np.ndarray[float]] = np.array([[]])
        node2: np.ndarray[np.ndarray[float]] = np.array([[]])
        node3: np.ndarray[np.ndarray[float]] = np.array([[]])
        nodeNum1: int = -1
        nodeNum2: int = -1
        nodeNum3: int = -1

        for i in range(len(self.nodes[0])):
            if self.nodes[1][i] < lowest1:
                lowest3 = lowest2
                node3 = node2
                nodeNum3 = nodeNum2
                lowest2 = lowest1
                node2 = node1
                nodeNum2 = nodeNum1
                lowest1 = self.nodes.item(1, i)
                node1 = self.nodes.T[i]
                nodeNum1 = i

            elif self.nodes.item(1, i) < lowest2:
                lowest3 = lowest2
                node3 = node2
                nodeNum3 = nodeNum2
                lowest2 = self.nodes.item(1, i)
                node2 = self.nodes.T[i]
                nodeNum2 = i

            elif self.nodes[1][i] < lowest3:
                lowest3 = self.nodes.item(1, i)
                node3 = self.nodes.T[i]
                nodeNum3 = i

        nodes: List[np.ndarray[np.ndarray[float]]] = [node1, node2, node3]
        nodeNums: List[int] = [nodeNum1, nodeNum2, nodeNum3]
        return nodes, nodeNums

    def goToDesiredNode(self, desiredNode: int) -> List[float]:
        """
        This function's purpose is to determine which nodes are 'related' to the desired node, and set the positions of the masses accordingly.
        'Related' refers to nodes that are attached by a string to the desired node. These are important because these connections tell significant
        information about where the masses should be placed. In these related nodes, 5 of the 6 masses are places with this method. The bar that is not
        connected by the related nodes will simply be placed at whichever node is higher. All the 'mass movement' will be described by forces moving on the
        model to the desired nodes.
        Conditions for the desiredNode is that the node must be one of the nodes that are closest to the ground in the model's current configuration which
        would be nodes that connect to 2 grounded nodes, and that node cannot be part of bar that touches the ground - otherwise that node isn't the lowest.
        However, this function will not control the desired node input, just the placement of forces.

        :param desiredNode: The node that the system will move the masses to go towards.
        :return: the percentage array that the system needs in order to move to that node.
        """

        relatedNodesVec: np.ndarray[float] = self.stringConns.T[desiredNode - 1]
        relatedNodes: List[int] = []
        relatedNodesCol: List[int] = []

        # This for loop gets all the related node information
        for i in range(len(relatedNodesVec)):
            if 0 != relatedNodesVec[i]:
                relatedNodesCol.append(i)

        for i in range(len(relatedNodesCol)):
            for j in range(len(self.stringConns[0])):
                if 0 != self.stringConns[relatedNodesCol[i]][j] and j != desiredNode - 1:
                    relatedNodes.append(j)

        percentageArray: List[float] = []  # the percentages will simply be based off of the negative or positive value of the entries in the bar array.

        # Check to see how related nodes and bars related.
        for i in range(len(self.barConns)):
            whatToMultBy: float = 0

            for j in range(len(self.barConns[0])):  # tests each entry in matrix.
                if j in relatedNodes or j == desiredNode - 1:
                    whatToMultBy = whatToMultBy + self.barConns.item(i, j)

            percentToAppend: float = whatToMultBy * .5 + .5  # this will give the values of either 0, .5, or 1, which will help the force dist.
            percentageArray.append(percentToAppend)

        return percentageArray

    def makeTarget(self, targetPlace: List[float] = None) -> None:
        """
        This function is meant to make it so a target is set for the system. The target will include an x and z coordinates and will be what the simulation
        will try to roll to.
        :param targetPlace:
        :return: None
        """
        if targetPlace is not None:
            self.target = targetPlace
        else:
            self.target = [random.random() * 10 - 5, random.random() * 10 - 5]

        if 0 < len(self.targets):
            self.targets = np.append(self.targets, np.array([self.target]), axis=0)
        else:
            self.targets = np.array([self.target])

    def updateNodes(self, newNodes: np.ndarray[np.ndarray[float]]) -> None:
        """
        Updates the locations of the current nodes of the system.
        :param newNodes: the location of the nodes to update the system to.
        :return: None
        """
        self.nodes = newNodes
