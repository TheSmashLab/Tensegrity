import matplotlib as pyplyt
import numpy as np
from typing import List


class PayloadModel:
    """
    A class to model the important aspects of a payload.
    """

    def __init__(self, mass, cornerPoints=np.array([[-1, -1, 2], [-1, 1, 2], [-1, -1, 4], [-1, 1, 4], [1, -1, 2], [1, 1, 2], [1, -1, 4], [1, 1, 4]]) * 1 / 4,
                 edgeConnections=np.array([[0, 1], [0, 2], [0, 4], [1, 5], [1, 3], [2, 6], [2, 3], [3, 7], [4, 6], [4, 5], [5, 7], [6, 7]]), maximumShock=4):
        """
        The initialization of the payload.  These are immutable properties except for the actual locations of the corner points, those can be changed by the optimizer for ideal initial placement.
        :param mass: The mass of the payload
        :param cornerPoints: The corner points of the payload, used to define its shape
        :param edgeConnections: The edge connections of the payload, used to show what it looks like in sim.
        :param maximumShock: The maximum shock the payload can take, measured in gs.
        """
        self.cornerPoints = cornerPoints
        self.cornerPointsMod = np.copy(self.cornerPoints)
        self.edgeConnections = edgeConnections
        self.mass = mass
        self.maximumShock = maximumShock
        self.origCOM = self.getCOM()

    def plot(self, plt: pyplyt.figure) -> None:
        """
        used to plot the payload
        :param plt: A already initialized matplotlib plot so that this payload can be plotted with its payload structure about it.
        :return:
        """
        for i in range(len(self.edgeConnections)):
            firstItem: int = self.edgeConnections.item(i, 0)
            secondItem: int = self.edgeConnections.item(i, 1)
            x: List[float] = []
            y: List[float] = []
            z: List[float] = []

            x.append(self.cornerPointsMod.item(firstItem, 0))
            y.append(self.cornerPointsMod.item(firstItem, 1))
            z.append(self.cornerPointsMod.item(firstItem, 2))
            x.append(self.cornerPointsMod.item(secondItem, 0))
            y.append(self.cornerPointsMod.item(secondItem, 1))
            z.append(self.cornerPointsMod.item(secondItem, 2))
            plt.plot(x, y, z, 'b')

    def getMass(self) -> float:
        """
        gets the mass of the payload
        :return: the mass of the payload
        """
        return self.mass

    def getCOM(self) -> np.ndarray[float]:
        """
        returns the current COM of the payload
        :return: COM of the payload.
        """
        location: np.ndarray = np.array([0, 0, 0])

        for i in range(len(self.cornerPointsMod)):
            location = location + self.cornerPointsMod[i]

        location = location / len(self.cornerPointsMod)

        return location

    def getMaxZ(self) -> float:
        """
        Gets the maximum z value of the payload.
        :return: the maximum z value of the payload.
        """
        return self.cornerPointsMod.max()

    def setNewPayloadPosition(self, newCOM) -> None:
        """
        sets a new payload position by changing the existing COM.
        :param newCOM: the new COM of the payload, where the payload where move to.
        :return: None
        """
        for i in range(len(self.cornerPoints)):
            self.cornerPointsMod[i] = self.cornerPoints[i] + (newCOM - self.origCOM)
