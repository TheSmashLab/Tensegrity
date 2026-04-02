import math
import numpy as np
from typing import List, Optional, Tuple

from src.TensegritySystem import Nodes


class tensegrityKConvert():
    """ This class convers a given class k tensegrity structure into a corresponding class 1 structure
        with constrained physical and virtual nodes.

        INPUTS:
            nodes: initial (class k) node matrix
            barConn: Initial bar connectivity matrix
            stringConn: Initial string connectivity matrix
            pinnedNodes: indicies of nodes that are pinned.

        OUTPUTS:
            nNew: Converted node matrix with physical and virtual nodes
            barConnNew: Converted bar connectivity matrix
            stringConnNew: Converted string connectivity matrix.
            P: constraint matrix containing N*P = D.
            nodeConstraints: Cell array in which each cell gives constrained node indicies
                corresponding to the initial nodes."""

    def __init__(self, nodes: np.ndarray[Nodes], barConn: np.ndarray[np.ndarray[float]], stringConn: np.ndarray[np.ndarray[float]], pinnedNodes: List[int] =
    []):

        # These are from the initialization arguments.
        self.barConn: np.ndarray[np.ndarray[float]] = barConn
        self.nodes: np.ndarray[Nodes] = nodes
        self.pinnedNodes: List[int] = pinnedNodes
        self.stringConn: np.ndarray[np.ndarray[float]] = stringConn

        # These are made through the Convert() method
        self.barConnNew: np.ndarray[np.ndarray[float]] = np.array([])
        self.D: np.ndarray[np.ndarray[float]] = np.array([])
        self.nNew: np.ndarray[np.ndarray[float]] = np.array([])
        self.nodeConstraints: List[List[int]] = []
        self.nodesNew: np.ndarray[np.ndarray[float]] = np.array([])
        self.P: np.ndarray[np.ndarray[float]] = np.array([])
        self.stringConnNew: np.ndarray[np.ndarray[float]] = np.array([])

        # Creates the second set of variables based off of the initial inputs.
        self.convert()

    def returnNeededValues(self) -> Tuple[np.ndarray[np.ndarray[float]], np.ndarray[np.ndarray[float]], np.ndarray[np.ndarray[float]], np.ndarray[np.ndarray[
        float]], np.ndarray[np.ndarray[float]], List[List[int]]]:
        """
        Returns relevant information needed for creating the system.
        :return: The generated portions of the convert() method.
        """
        return self.nodesNew, self.barConnNew, self.stringConnNew, self.P, self.D, self.nodeConstraints

    def nodeArrayAsCoords(self) -> np.ndarray[np.ndarray[float]]:
        """
        Changes a 1D array of Nodes into a 2D array of the node coordinates.
        :return: 2D np array of Coordinates.
        """
        nodeArrayLong: np.ndarray[np.ndarray[float]] = np.array([[]])

        for i in range(0, len(self.nodes)):
            currentNode: np.ndarray[np.ndarray[float]] = np.array([self.nodes.item(i).getCoords()]).T

            if 0 == nodeArrayLong.size:
                nodeArrayLong = currentNode
            else:
                nodeArrayLong = np.append(nodeArrayLong, currentNode, axis=1)

        return nodeArrayLong

    @staticmethod
    def binom(nodeConstraints: List[int], k: int) -> List[float]:
        """
        Creates the Binomial function needed for conversion
        :param nodeConstraints: the nodeConstraints calculated to be on the system.
        :param k: other side of the binomial function
        :return: The binomial function.
        """
        toReturn: List[float] = []

        for i in range(0, len(nodeConstraints)):
            toReturn.append(math.factorial(nodeConstraints[i]) // math.factorial(k) // math.factorial(nodeConstraints[i] - k))
        return toReturn

    def convert(self) -> None:
        """
        Creates needed information for the system based off of the initial system inputs.  That information is stored as variables within the class.
        :return: None: sets the internal variables to the unknown values.
        """

        # Get class of each node, and total number of virtual nodes.
        nodeClass: np.ndarray[int] = np.sum(np.abs(self.barConn), axis=0, dtype=int)  # adding along the columns.
        numOfVirtNodes: np.ndarray[float] = np.sum(nodeClass) - np.sum(nodeClass > 0)
        num: int = nodeClass.size

        # initialize matrix of virtual nodes.
        nVirt: np.ndarray[np.ndarray[float]] = np.zeros([3, numOfVirtNodes])

        # Go through all nodes.  If a node has one or more coincident virtual nodes, copy that node position into nVirt.  Also create nodeConstraints
        #  along the way, which keeps track of which final nodes are constrained to be coincident.
        virtualNodeInd: int = 0
        nodeConstraints: List[List[int]] = []

        for i in range(0, num):
            appendNodeConstraints: List[int] = [i]

            for j in range(0, nodeClass[i] - 1):
                nVirt[:, virtualNodeInd] = self.nodeArrayAsCoords()[:, i]
                appendNodeConstraints.append(num + virtualNodeInd)
                virtualNodeInd += 1
            nodeConstraints.append(appendNodeConstraints)

        nNew: np.ndarray[np.ndarray[float]] = np.append(self.nodeArrayAsCoords(), nVirt, axis=1)

        # Go through each row of given bar connectivity matrix and move entries for class k nodes to the appropriate virtual node indicies.
        barConnNew: np.ndarray[np.ndarray[float]] = np.copy(self.barConn)

        for i in range(0, num):
            for j in range(0, len(nodeConstraints[i]) - 1):
                nodeInd: int = nodeConstraints[i][j]

                if nodeInd <= np.size(self.barConn, axis=1):
                    checkArr: np.ndarray[float] = np.abs(barConnNew[:, nodeInd])
                    barInd: List[int] = []
                    for k in range(0, len(checkArr)):

                        if 0 != checkArr[k]:
                            barInd.append(k)
                    barInd: np.ndarray[int] = np.array(barInd)

                    for k in range(0, barInd.size - 1):

                        while len(barConnNew) <= k + 1:
                            add: np.ndarray[np.ndarray[float]] = np.zeros(1, [len(barConnNew[0])])
                            barConnNew = np.append(barConnNew, add, axis=0)

                        while len(barConnNew[0]) <= nodeConstraints[i][k + 1]:
                            add: np.ndarray[np.ndarray[float]] = np.zeros([len(barConnNew), 1])
                            barConnNew = np.append(barConnNew, add, axis=1)
                        barConnNew[barInd[k + 1], nodeConstraints[i][k + 1]] = barConnNew[barInd[k + 1], nodeInd]
                        barConnNew[barInd[k + 1], nodeInd] = 0

        # Pad barConnNew with zeros to match dimension of the new N matrix.,
        add: np.ndarray[float] = np.zeros([len(self.stringConn), numOfVirtNodes])
        stringConnNew: np.ndarray[float] = np.append(self.stringConn, add, axis=1)

        # Generate P constraint matrix
        P: np.ndarray[float] = np.array([[]])

        # THE FOLLOWING CODE MAY BE UNSTABLE FOR OTHER SYSTEMS.
        for i in range(0, len(nodeConstraints)):

            if 1 < len(nodeConstraints[i]):
                constraintsToAddMore: List[float] = self.binom(nodeConstraints[i], 1)
                constraintsToAdd: np.ndarray[float] = np.array([constraintsToAddMore[0:len(nodeConstraints[i])]])
                P_add: np.ndarray[np.ndarray[float]] = np.zeros([len(nNew[0]), len(constraintsToAdd)])
                for j in range(0, len(constraintsToAdd)):
                    P_add[constraintsToAdd[j, 0], j] = 1
                    P_add[constraintsToAdd[j, 1], j] = -1

                # Here we replace any 0 values in the P matrix with non-zero values found in the P_add matrix.
                for i in range(len(P_add)):
                    if 0 == np.size(P):
                        P = P_add

                    if 0 < P_add[i, 0]:
                        P[i, 0] = P_add[i, 0]

                if 1 == P.ndim:
                    P = np.array([P]).T

        # Rearrange stuff to put into form : N = [Nb, Ns]
        # THIS PART SKIPPED SINCE IT DID NOT AFFECT THE MODEL FOR THE DOUBLE PEND, NEED DIFFERENT EXAMPLE TO MAKE SENSE OF IT.
        # skipped N_New, C_s_new, C_b_new
        # TODO: implement.
        stringNodeInd = np.zeros(len(nodeClass) + numOfVirtNodes)
        for i in range(len(nodeClass)):
            if 0 == nodeClass[i]:
                stringNodeInd[i] = 1

        # Generate D Matrix
        if 0 < (len(P)):
            D: np.ndarray[np.ndarray[float]] = np.zeros([3, len(P[0])])
        else:
            D: np.ndarray[np.ndarray[float]] = np.zeros([3, 0])

        for i in range(0, len(self.pinnedNodes)):
            dAdd: np.ndarray[np.ndarray[float]] = np.array([self.nodeArrayAsCoords().T[int(self.pinnedNodes[i] - 1)]]).T
            D = np.append(D, dAdd, axis=1)

        self.D = D

        # Generate constraint matrix for pinned nodes.
        P_pinned: np.ndarray[int] = np.array([])

        for i in range(0, len(self.pinnedNodes)):
            P_add: np.ndarray[int] = np.zeros([len(nNew[0]), 1])
            P_add[int(self.pinnedNodes[i] - 1)] = 1

            if 0 == len(P_pinned):
                P_pinned = P_add
            else:
                P_pinned = np.append(P_pinned, P_add, axis=1)

        if 0 != P.size:
            if 0 != P_pinned.size:
                P = np.append(P, P_pinned, axis = 1)

        if 0 == P.size:
            self.P = P_pinned
        else:
            # TODO: implement rest of logic for more complicated systems.
            # Ps = P[string]
            self.P = P

        self.nodeConstraints = nodeConstraints
        self.stringConnNew = stringConnNew
        self.barConnNew = barConnNew
        self.nodesNew = nNew


# TODO: The function below needs to be checked/updated if segmented strings are desired.
def TensegPercentTo_s0(nodes: np.ndarray[np.ndarray[float]], cs: np.ndarray[np.ndarray[float]], percents: np.ndarray[np.ndarray[float]],
                       parents: Optional[np.ndarray[float]] = None) -> np.ndarray[float]:
    """s_0 = TENSEGPERCENTTO_SO(nNew, csNew, percents, parents) creates a vector
       containing all resting string lengths for a set of string segments based
       on specified rest length percentages for the "parent" strings.

        INPUTS:
            nodes: node matrix
            cs: string connectivity matrix (after segmentation)
            percents: m x 2 matrix for m parent stringsthat have resting lengths
                that differ from their specified initial lengths.  The first column
                gives the index of the mth parent string, and the second column
                gives the percent of the initial length that defines the rest
                length.  If values are being specified for every string, indices can
                be left out.  If all strings have the same percent, can be a single value.
            parents (optional): REQUIRED if working with segmented strings.  Vector
                containing original string indices associated with each string
                segment. (from 'tenseg_string_segment').  Not needed otherwise.

        OUTPUTS:
            s0: vector containing rest lengths of all string segments.

        Example:
            s0 = TensegPercentTo_s0(nodes, cs, [[1, 0.8],[2, 0.8],[3, 0.7]]"""

    # Each string is its own parent if not otherwise specified.
    if None == parents:
        parents = np.arange(1, len(cs))

    if 1 == len(percents):
        percents = percents * np.ones(len(parents))

    if 1 == len(percents[0]) and len(percents) == len(parents):
        # I think I translated the code below incorrectly, but shouldn't be called if proper
        # parameters passed in.
        percents = np.array([[1, len(parents)], percents * np.ones(len(parents))]).T

    # Get all initial string lengths
    s0: np.ndarray[float] = np.array([np.sqrt(np.diag(nodes.dot(cs.T).T.dot(nodes.dot(cs.T))))]).T

    # compute ith string rest length
    for i in range(0, len(percents)):
        # Get parent string index
        pInd: int = int(percents[i, 0] - 1)

        # Get percentage by which to scale rest length
        scale: float = percents.item(i, 1)

        # Scale all string members associated with parent string index.
        s0[pInd] = scale * s0[pInd]

    return s0
