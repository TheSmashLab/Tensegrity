import numpy as np
from typing import List, Tuple

from src.TensegritySystem import Nodes


def eqOfLineSolver(point1: np.ndarray[float], point2: np.ndarray[float]) -> List[float]:
    """
    This functions finds the equation of the line between the points on the triangle.
    :param point1: the first point on the line.
    :param point2: the second point on the line
    :return: List containing the slope and intercept of the line.
    """
    m: float = (point1[1] - point2[1]) / (point1[0] - point2[0])
    b: float = -m * point1[0] + point1[1]
    return list([m, b])


def findCOM(nodeVector: np.ndarray[np.ndarray[float]]) -> np.ndarray[np.ndarray[float]]:
    """
    Finds the center of mass of the current system.
    :param nodeVector: The vector containing the positions of the current nodes of the system.
    :return: The center of mass of the system.
    """
    x: float = 0
    y: float = 0
    z: float = 0
    for i in range(len(nodeVector)):
        x = x + nodeVector.item(i, 0)
        y = y + nodeVector.item(i, 1)
        z = z + nodeVector.item(i, 2)
    x = x / len(nodeVector)
    y = y / len(nodeVector)
    z = z / len(nodeVector)
    return np.array([[x], [y], [z]])


def findPerpPoint(triPoint1, triPoint2, otherPoint) -> Tuple[List[float], float]:
    """
    This function finds the point along the line comprised of the triangle points that is perpendicular
    to the triangle line slope and goes through the other point.
    :param triPoint1: The first point that comprises the line on the triangle that will be used for the initial line.
    :param triPoint2: The second point that comprises the line on the triangle that will be used for the initial line.
    :param otherPoint: The point that the line perpendicular to the initial line must pass through.
    :return:
    """
    triLineInfo: List[float] = eqOfLineSolver(triPoint1, triPoint2)

    if triLineInfo[0] != 0:
        mPerp: float = -1 / triLineInfo[0]  # negative recipricol for perpendicular lines.
        bPerp: float = -mPerp * otherPoint[0] + otherPoint[1]
        x: float = (bPerp - triLineInfo[1]) / (triLineInfo[0] - mPerp)
        y: float = mPerp * x + bPerp
    else:
        x = otherPoint[0]
        y = triPoint1[1]

    distance: float = np.sqrt((x - otherPoint[0]) ** 2 + (y - otherPoint[1]) ** 2)
    return [x, y], distance


def getPositionsFromNodeArray(nodeArray: np.ndarray[Nodes.Node]) -> np.ndarray[np.ndarray[float]]:
    """
    This method creates the 3D representation of a node array from a node array.
    :param nodeArray: The node array to be transformed into coordinates.
    :return: The array containing each of the node's coordinates.
    """
    returnArray: np.ndarray[np.ndarray[float]] = np.array([[], [], []])
    for i in range(np.size(nodeArray)):
        thisNode: np.ndarray[float] = nodeArray.item(i).getCoords()
        returnArray = np.append(returnArray, np.array([thisNode]).T, axis=1)

    return returnArray.T