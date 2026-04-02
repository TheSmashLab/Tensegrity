import numpy as np


def linearTransform(coordArray: np.ndarray[np.ndarray[float]], transformArray: np.ndarray[np.ndarray[float]]) -> np.ndarray[np.ndarray[float]]:
    """
    Moves each entry in coord array in the direction of transform array
    :param coordArray: The current coordinates of the system.
    :param transformArray: The transformation that we need the coordinate array to go through.
    :return:
    """
    coordArrayUse: np.ndarray[np.ndarray[float]] = coordArray.T
    coordArrayNew: np.ndarray[np.ndarray[float]] = np.array([[], [], []])

    for i in range(len(coordArrayUse)):
        coordArrayNew = np.append(coordArrayNew, np.array([coordArrayUse[i]]).T + transformArray, axis=1)

    return coordArrayNew


def rotX(inputVector: np.ndarray[np.ndarray[float]], degrees: float) -> np.ndarray[np.ndarray[float]]:
    """
    Rotates a matrix in the X direction.
    :param inputVector: the vector to be rotated.
    :param degrees: the number of degrees to be rotated.
    :return: the rotated input vector.
    """
    radDegs: float = float(degrees / 360 * 2 * np.pi)
    rotXMat: np.ndarray[np.ndarray[float]] = np.array([[1, 0, 0],
                                                       [0, np.cos(radDegs), -np.sin(radDegs)],
                                                       [0, np.sin(radDegs), np.cos(radDegs)]])
    return rotXMat.dot(inputVector)


def rotY(inputVector: np.ndarray[np.ndarray[float]], degrees: float) -> np.ndarray[np.ndarray[float]]:
    """
    Rotates a matrix in the Y direction.
    :param inputVector: the vector to be rotated.
    :param degrees: the number of degrees to be rotated.
    :return: the rotated input vector.
    """
    radDegs: float = float(degrees / 360 * 2 * np.pi)
    rotYMat: np.ndarray[np.ndarray[float]] = np.array([[np.cos(radDegs), 0, np.sin(radDegs)],
                                                       [0, 1, 0],
                                                       [-np.sin(radDegs), 0, np.cos(radDegs)]])
    return rotYMat.dot(inputVector)


def rotZ(inputVector: np.ndarray[np.ndarray[float]], degrees: float) -> np.ndarray[np.ndarray[float]]:
    radDegs: float = float(degrees / 360 * 2 * np.pi)
    rotZMat: np.ndarray[np.ndarray[float]] = np.array([[np.cos(radDegs), -np.sin(radDegs), 0],
                                                       [np.sin(radDegs), np.cos(radDegs), 0],
                                                       [0, 0, 1]])
    return rotZMat.dot(inputVector)

def skew(vector: np.ndarray[float]) -> np.ndarray[np.ndarray[float]]:
    """
    This is meant to do the skew operator, meaning skew the input vector.
    :param vector: The vector to be transformed into a skew matrix.  Assume a 1D array
    :return: The skew matrix of the input vector.
    """
    skewMat: np.ndarray[np.ndarray[float]] = np.zeros([3, 3])
    skewMat[0, 1] = -vector[2]
    skewMat[0, 2] = vector[1]
    skewMat[1, 0] = vector[2]
    skewMat[2, 0] = -vector[1]
    skewMat[1, 2] = -vector[0]
    skewMat[2, 1] = vector[0]
    return skewMat
