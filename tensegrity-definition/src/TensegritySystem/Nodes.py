from typing import List


class Node:
    def __init__(self, initalxLoc: float = 0, initialyLoc: float = 0, initialzLoc: float = 0):
        """
        Intializes the node of the system.
        :param initalxLoc: the initial x position of the node.
        :param initialyLoc: the initial y position of the node.
        :param initialzLoc: the initial z position of the node.
        """
        self.xloc: float = initalxLoc
        self.yloc: float = initialyLoc
        self.zloc: float = initialzLoc

    def changeCoords(self, newx: float, newy: float, newz: float) -> None:
        """
        Change the coordinates used by the system.
        :param newx: new x location of the node.
        :param newy: new y location of the node.
        :param newz: new z location of the node.
        :return: None
        """
        self.xloc = newx
        self.yloc = newy
        self.zloc = newz

    def getCoords(self) -> List[float]:
        """
        Returns the coordinates of the current node.
        :return: the coordinates of the current node.
        """
        return list([self.xloc, self.yloc, self.zloc])

    def toString(self) -> str:
        """
        Creates a string representing the current node.
        :return: a string representing the current node.
        """
        return str(self.xloc) + ", " + str(self.yloc) + ", " + str(self.zloc)
