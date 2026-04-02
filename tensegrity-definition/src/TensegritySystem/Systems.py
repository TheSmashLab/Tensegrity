from cvxopt import spdiag, matrix
import numpy as np
from typing import List

from src.TensegritySystem import Nodes


class System:
    """
    The class that represents the overall tensegrity system.
    """

    def __init__(self, barConn: np.ndarray[np.ndarray[float]] = np.array([]),
                 barMaterial: str = 'Aluminum',
                 failMode: str = 'yeildAndBuckle',
                 nodeArray: np.ndarray[Nodes.Node] = np.array([]),
                 stringConn: np.ndarray[np.ndarray[float]] = np.array([]),
                 stringMaterial: str = 'Aluminum'):
        """
        Initializes all the relavant variables for a tensegrity system.
        :param barConn: The bar connection matrix.
        :param barMaterial: The material the bar is made out of.
        :param failMode: The way the system will be analyzed for failure.
        :param nodeArray: An array consisting of the nodes that comprise the system.
        :param stringConn: The string connection matrix.
        :param stringMaterial: The material the string is made out of.
        """
        self.barConn: np.ndarray[np.ndarray[float]] = barConn
        self.barMaterial: str = barMaterial
        self.failMode: str = failMode
        self.force: np.ndarray[np.ndarray[float]] = np.zeros([3, len(nodeArray)])
        self.labels = np.array([])
        self.mass_member = np.array([])
        self.mass_member_buckle = np.array([])
        self.nodeArray: np.ndarray[Nodes.Node] = nodeArray
        self.ns: int = 0
        self.pinnedConnections: np.ndarray[np.ndarray[int]] = np.array([[]])
        self.stringConn: np.ndarray[np.ndarray[float]] = stringConn
        self.stringMaterial: str = stringMaterial
        self.x0: matrix = matrix(1.0, (1, 1))

        # These variables require the variables above to be defined.
        self.connMatrixBar: np.ndarray[np.ndarray[float]] = self.makeConnMatrix(barConn)
        self.connMatrixString: np.ndarray[np.ndarray[float]] = self.makeConnMatrix(stringConn)

    def getBarConn(self) -> np.ndarray[np.ndarray[float]]:
        """
        returns the compressed (direct connection) barConn matrix.
        :return: the compressed barConn matrix.
        """
        return self.barConn

    def getBarConnMat(self) -> np.ndarray[np.ndarray[float]]:
        """
        returns the uncompressed(0s and 1s) barConn matrix.
        :return: the uncompressed barConn matrix.
        """
        return self.connMatrixBar

    def getNode(self, indicie: int) -> Nodes.Node:
        """
        Gets a particular node in the system.
        :param indicie: the node in question that is to be returned.
        :return: The node in question.
        """
        return self.nodeArray.item(indicie)

    def getPinned(self) -> np.ndarray[np.ndarray[int]]:
        return self.pinnedConnections

    def getStringConn(self) -> np.ndarray[np.ndarray[float]]:
        """
        returns the compressed (direct connection) stringConn matrix.
        :return: the compressed stringConn matrix.
        """
        return self.stringConn

    def getStringConnMat(self) -> np.ndarray[np.ndarray[float]]:
        """
        returns the uncompressed(0s and 1s) stringConn matrix.
        :return: the uncompressed stringConn matrix.
        """
        return self.connMatrixString

    def makeConnMatrix(self, compressedIndecies: np.ndarray[np.ndarray[float]]) -> np.ndarray[np.ndarray[float]]:
        """
        Creates an uncompressed connection matrix consisting of 0s and 1s using the existing raw connection information.
        :param compressedIndecies: The raw array that shows which nodes are connected.
        :return: The uncompressed connection matrix.
        """
        numOfConnections: int = np.size(compressedIndecies, 0)
        size: int = self.nodeArray.size
        ConnMat: np.ndarray[np.ndarray[float]] = np.zeros([size, numOfConnections])

        for i in range(0, numOfConnections):
            startNode: int = int(compressedIndecies.item(i, 0) - 1)
            endNode: int = int(compressedIndecies.item(i, 1) - 1)

            ConnMat[startNode, i] = -1
            ConnMat[endNode, i] = 1

        return ConnMat.T

    def materialPropertiesBar(self):
        """
        A method that contains all the material properties that the bars could have. This will have to be changed in the future if the list becomes too long.
        :return: list of material parameters.
        """
        if 'Steel' == self.barMaterial:
            E_b: float = 200e09
            rho_b: float = 8000
            sigma_b: float = 300e06
        elif 'UHMWPE' == self.barMaterial:
            E_b: float = 120e09
            rho_b: float = 970
            sigma_b: float = 2.7e09
        elif 'Aluminum' == self.barMaterial:
            E_b: float = 60e09
            rho_b: float = 2700
            sigma_b: float = 110e06
        else:
            print('Edit the material database, all values set to 1')
            E_b: float = 1
            rho_b: float = 1
            sigma_b: float = 1

        return list[E_b, rho_b, sigma_b]

    def materialPropertiesString(self) -> List[float]:
        """
        A method that contains all the material properties that the strings could have. This will have to be changed in the future if the list becomes too long.
        :return: list of material parameters.
        """
        if 'Steel' == self.barMaterial:
            E_b: float = 200e09
            rho_b: float = 8000
            sigma_b: float = 300e06
        elif 'UHMWPE' == self.barMaterial:
            E_b: float = 120e0
            rho_b: float = 970
            sigma_b: float = 2.7e09
        elif 'Aluminum' == self.barMaterial:
            E_b: float = 60e09
            rho_b: float = 2700
            sigma_b: float = 110e06
        else:
            print('Edit the material database, all values set to 1')
            E_b: float = 1
            rho_b: float = 1
            sigma_b: float = 1

        return list([E_b, rho_b, sigma_b])

    def NodeArrayAsCoords(self) -> np.ndarray[np.ndarray[float]]:
        """
        transforms an array of Nodes into an array that contains all the node's coordinates.
        :return:
        """
        nodeArrayLong: np.ndarray[np.ndarray[float]] = np.array([[]])
        for i in range(0, len(self.nodeArray)):
            currentNode: np.ndarray[np.ndarray[float]] = np.array([self.nodeArray.item(i).GetCoords()]).T

            if 0 == nodeArrayLong.size:
                nodeArrayLong = currentNode
            else:
                nodeArrayLong = np.append(nodeArrayLong, currentNode, axis=1)

        return nodeArrayLong

    def nonlinearForceDensityMinimalMass(self, x=None, z=None):
        """
        NOTE: This function is not used often, so it is not annotated.
        This function is a calculation of mass of each structural member and the total mass.
        Essentially, trying to minimize mass, so F

        Inputs:
            x:force densities in strings and bars
            ns: number of strings
            label: a vector that denotes if the bar is in yielding or buckling
            mass_member_buckle: material constants for buckling calculation

        Outputs:
            F: mass of each structure element
            FF: Total mass of all the bars and strings`
        """
        if x == None:
            return 0, self.x0
        if min(x) < 0:
            return None
        FF = np.array(self.mass_member_buckle[0:self.ns]).T * (np.array(x[0:self.ns])).T  # mass of string subject to yielding
        for i in range(self.ns, len(self.mass_member_buckle)):
            if self.label[i - self.ns - 1] == 1:
                FF = np.append(FF, self.mass_member_buckle[i] * np.sqrt(x.T[0, i]))
            else:
                FF = np.append(FF, self.mass_member[i] * np.sqrt(x[0, i]))

        F = np.sum(FF)
        Df = 1 / 2 * (x ** (-1 / 2)).T
        if z == None:
            return F, Df
        H = spdiag(z[0] * -1 / 4 * x ** (-3 / 2))
        return F, Df, H

    def setForce(self, forceMatrix: np.ndarray[np.ndarray[int]]) -> None:
        """
        Sets the force acting on the system.
        :param forceMatrix: the new force matrix that acts on the system.
        :return: None
        """
        self.force = forceMatrix

    def setNodeArray(self, nodeArray: np.ndarray[Nodes.Node]) -> None:
        """
        Sets the nodes used in the system.
        :param nodeArray: The node array that represents the system.
        :return: None
        """
        self.nodeArray = nodeArray

    def setPinned(self, pinnedArray: List[int]) -> None:
        """
        Sets the pinned nodes for the system.
        :param pinnedArray: The pinned array that represents which nodes are pinned.
        :return: None
        """
        self.pinnedConnections = np.array(pinnedArray)

    def tensegrityEquilibriumMinimalMass(self):
        """
        Determines the minimal mass solution at system equilibrium.
        :return: None
        NOTE: Not used, so not annotated.
        """
        k1 = np.array([[]])
        for i in range(0, len(self.nodeArray)):
            # the diag function you see here changes each of the columns into a diagonal matrix for correct multiplication purposes.

            stringPart = np.array(self.connMatrixString.T.dot(np.diag(self.connMatrixString[:, i].T)))
            barPart = np.array(self.connMatrixBar.T.dot(np.diag(self.connMatrixBar[:, i].T)))

            # append the two parts together -
            E = np.append(stringPart, -1 * barPart, axis=1)
            # k matches the Code, I think that the code in matlab ends up appending the Ks together.
            K = self.NodeArrayAsCoords().dot(E)
            if np.size(k1) == 0:
                k1 = K
            else:
                k1 = np.append(k1, K, axis=0)

        # reshapes the self.force into a vector in the needed form for future programming.
        force = np.reshape(self.force.T, (self.force.size, 1))

        # This code block removes the potential force vectors that can work on the system based on which nodes are pinned in which directions.
        # So it essentially takes into account the pinned areas.
        if len(self.pinnedConnections) != 0:
            remove = np.array([])
            j = 0
            k2 = np.array([])
            nc = self.pinnedConnections.T[0]
            for i in range(0, len(nc)):
                if self.pinnedConnections[i, 1] == 1:
                    if np.size(k2) == 0:
                        k2 = [k1[3 * nc[i] - 3, :]]

                    else:
                        k2 = np.append(k2, [k1[3 * nc[i] - 3, :]], axis=1)
                    remove = np.append(remove, 3 * nc[i] - 3)
                    j = j + 1

                if self.pinnedConnections[i, 2] == 1:
                    if np.size(k2) == 0:
                        k2 = [k1[3 * nc[i] - 2, :]]
                    else:
                        k2 = np.append(k2, [k1[3 * nc[i] - 2, :]], axis=1)
                    remove = np.append(remove, 3 * nc[i] - 2)
                    j = j + 1

                if self.pinnedConnections[i, 3] == 1:
                    if np.size(k2) == 0:
                        k2 = [k1[3 * nc[i] - 1, :]]
                    else:
                        k2 = np.append(k2, [k1[3 * nc[i] - 1, :]], axis=1)
                    remove = np.append(remove, 3 * nc[i] - 1)
                    j = j + 1
                # the logic of the line of code below might be incorrect, but worked for 1 case so far.
                k2 = np.reshape(k2, (len(remove), len(k1[0])))
            for i in range(0, len(remove)):
                k1 = np.delete(k1, int(remove[i] - i), 0)
                force = np.delete(force, int(remove[i] - i), 0)

        barMats = self.materialPropertiesBar()
        E_b = barMats[0]
        rho_b = barMats[1]
        sigma_b = barMats[2]
        stringMats = self.materialPropertiesString()
        E_s = stringMats[0]
        rho_s = stringMats[1]
        sigma_s = stringMats[2]
        # final optimization

        B = self.NodeArrayAsCoords().dot(self.connMatrixBar.T)
        S = self.NodeArrayAsCoords().dot(self.connMatrixString.T)
        self.ns = len(S[0])
        nb = len(B[0])
        barLen = np.diag(B.T.dot(B))
        strLen = np.diag(S.T.dot(S))
        mass_gamma = rho_s / sigma_s * strLen
        mass_lambda = rho_b / sigma_b * barLen
        self.mass_member = np.append(mass_gamma, mass_lambda)

        mass_gamma_buckle = rho_s / sigma_s * strLen
        mass_lambda_buckle = 2 * rho_b / np.sqrt(np.pi * E_b) * np.power(barLen, (5 / 4))
        self.mass_member_buckle = np.append(mass_gamma_buckle, mass_lambda_buckle)

        # Assume that all bars will buckle, thsi lead to all labels for the bars to be 1, otherwise it will be 0.

        forceDen = np.zeros((50, 1))  # essentially makes it so the most loops that can happen is 50.  might edit the code to make it so more loops can happen.
        self.label = np.ones((nb, 1), dtype=int)
        self.x0 = matrix(.01, (self.ns + nb, 1))
        # the Nonlinear Density functions now works.
        # print(solvers.cp(self.NonlinearForceDensityMinimalMass)['x'])   #maybe work on this with the professor?  just walk through it and try to figure it out.

        """
        lambdaTest = forceDen[0,len(S[0,:])+1:]
        for i in range(0,nb):
            if lambdaTest[i] >= 4*pow(sigma_b,2)*np.sqrt(barLen[i])/(np.pi*  E_b):
                label[i] = 0
            else:
                label[i] = 1

        loop = 1
        x0 = 1e-2*np.ones(ns+nb, 1)

        forceDen = self.NonlinearForceDensityMinimalMass(x0,ns,label,mass_member_buckle,mass_member)

        #THE BELOW MAY HAVE TO CHANGE DUE TO LOOP PROBS.
        while abs(forceDen[loop] - forceDen[loop-1])>10e-2:
            lambdaTest = forceDen[loop,len(S[0,:])+1]
            for i in range(0,nb):
                if lambdaTest[i] >= 4 * pow(sigma_b, 2) * np.sqrt(barLen[i]) / (np.pi * E_b):
                    label[i] = 0
                else:
                    label[i] = 1

            loop += 1
            x0 = 1e-2 * np.ones(ns+nb,1)

            forceDen = self.NonlinearForceDensityMinimalMass(x0, ns, label, mass_member_buckle, mass_member)

        MM = []
        mass_bar = []
        mass_string = []
        MM = mass_member_buckle.dot(forceDen[loop,0:ns]) # It looks like force den is just an array that has a different way to call the initial elements.  probably can just add another dimension
        #onto another array in np to replicate it.
        for i in range(ns,len(mass_member_buckle)):
            if label[i-ns] == 1:
                MM[i] = mass_member_buckle[i]*np.sqrt(forceDen[loop,i])
            else:
                MM[i] = mass_member[i]*forceDen[loop,i]

        mass_string = MM[0:ns]
        mass_bar = MM[ns:]
        minMass, ff = self.NonlinearForceDensityMinimalMass(forceDen[loop],ns,label,mass_member_buckle,mass_member)
        #Below shows the plots that bars and strings thickness is proportional to their actual radius.

        r_bar = []
        r_string = []
        barWidth_in = []
        stringWidth_in = []

        #radius of bars
        r_bar = (mass_bar/(rho_b*np.pi*barLen^(1/2)))^(1/2)  #this will have to be redone
        #radius of strings
        r_string = (mass_string/(rho_s*np.pi*strLen)^(1/2))^(1/2)

        if np.max(r_bar) - np.min(r_bar) < 1e-6:
            barWidth_in = 8*np.ones(np.size(r_bar))
        else:
            #bar with least radius, line width is 2, bars with largest radius, line width is 8.
            barWidth_in = 2 + (8-2)*(r_bar-np.min(r_bar))/(np.max(r_bar)- np.min(r_bar))

        if np.max(r_string) - np.min(r_string) < 10e-6:
            stringWidth_in = 2 * np.ones(np.size(r_string))
        else:
            stringWidth_in = 2 + (8-2)*(r_string-np.min(r_string))/(np.max(r_string)- np.min(r_string))

        if self.pinnedConnections.size == 0:
            supportLoad = 0
        else:
            supportLoad = k2*forceDen[loop]
        """

    def toString(self) -> str:
        """
        Creates a string that represents the system's state.
        :return: a string representing the system.
        """
        returnString: str = ""

        for i in range(0, len(self.nodeArray)):
            stringFromNode: str = self.nodeArray.item(i).toString()
            returnString = returnString + "Node " + str(i) + ": " + stringFromNode + '\n'

        return returnString
