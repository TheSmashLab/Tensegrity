import numpy as np

from src.TensegritySystem import Nodes as N
from src.Utils import CommonMatrixOperations


class AccelerometerSimulation:
    """The function of this class is simply to return the force of gravity(normally in the -y direction) as a combination
        of the x,y,and z locations of its own readings.  This will help determine the orientation of the tensegrity structure."""

    def __init__(self, accel1=np.array([]), accel2=None, accel3=None):
        # an accelerometer oriented so that the gravity initially works in the negative y direction.
        self.x1 = 0
        self.y1 = -1
        self.z1 = 0

        # an accelerometer oriented so that the gravity initially works in the negative x direction.
        self.x2 = -1
        self.y2 = 0
        self.z2 = 0

        # an accelerometer oriented so that the gravity initially works in the negative z direction.
        self.x3 = 0
        self.y3 = 0
        self.z3 = -1

    # TODO: UPDATE THIS MODEL, WILL ESSENTIALLY SERVE AS THE "A" IF USED IN A KALMAN FILTER.
    def calcNewXYZ(self, node1Init, node1Final, node2Init, node2Final, node3Init, node3Final):
        """uses Newton-Euler angles to calculate the new accelerations in the x, y, and z directions each time it is called.
        will then update the self.x, self.y, and self.z variables accordingly. Uses the roll, pitch, and yaw to
        determine these new accelerations.  In the physcial system, the rotation of the system will give the new
        accelerations automatically, so this won't have to be done.
        parameters:
        roll: the degrees it rolled about its x axis
        pitch: the degrees it rolled about its y axis
        yaw: the degrees it rolled about its z axis.

        returns:
            accelVector1: x, y, z values from the rotation matrix using the initial accelerometer 1 reading as reference.
            accelVector2: x, y, z values from the rotation matrix using the initial accelerometer 2 reading as reference."""

        psi, theta, phi = self.determineAngles(node1Init, node1Final, node2Init, node2Final, node3Init, node3Final)

        rotArray1 = [[self.x1], [self.y1], [self.z1]]
        # rotatedCoords = usefulTransforms.rotX(nodeArray[i].GetCoords(), 41.80901 / 2)
        accelVector1 = CommonMatrixOperations.rotX(rotArray1, phi)  # after movement
        newNode = N.Node(accelVector1[0], accelVector1[1], accelVector1[2])

        accelVector1 = CommonMatrixOperations.rotY(newNode.getCoords(), theta)
        newNode = N.Node(accelVector1[0], accelVector1[1], accelVector1[2])

        accelVector1 = CommonMatrixOperations.rotZ(newNode.getCoords(), psi)

        rotArray2 = [[self.x2], [self.y2], [self.z2]]
        # rotatedCoords = usefulTransforms.rotX(nodeArray[i].GetCoords(), 41.80901 / 2)
        accelVector2 = CommonMatrixOperations.rotX(rotArray2, phi)  # after movement
        newNode = N.Node(accelVector2[0], accelVector2[1], accelVector2[2])

        accelVector2 = CommonMatrixOperations.rotY(newNode.getCoords(), theta)
        newNode = N.Node(accelVector2[0], accelVector2[1], accelVector2[2])

        accelVector2 = CommonMatrixOperations.rotZ(newNode.getCoords(), psi)

        rotArray3 = [[self.x3], [self.y3], [self.z3]]
        # rotatedCoords = usefulTransforms.rotX(nodeArray[i].GetCoords(), 41.80901 / 2)
        accelVector3 = CommonMatrixOperations.rotX(rotArray3, phi)  # after movement
        newNode = N.Node(accelVector3[0], accelVector3[1], accelVector3[2])

        accelVector3 = CommonMatrixOperations.rotY(newNode.getCoords(), theta)
        newNode = N.Node(accelVector3[0], accelVector3[1], accelVector3[2])

        accelVector3 = CommonMatrixOperations.rotZ(newNode.getCoords(), psi)

        return [accelVector1, accelVector2, accelVector3]

    # TODO: THIS FUNCTION NEED TO HAVE ITS INPUTS CHANGED WHEN CALLED, WON'T USE ACCEL DATA ANYMORE, BUT WILL USE NODE DATA.
    @staticmethod
    def determineAngles(node1Init, node1Final, node2Init, node2Final, node3Init, node3Final):
        """This function is used to determine the amount that the system rotated about its x, y, and z axes by doing a
        system of equations on the Euler angles.  This is done by using the fact that:
        node1Final = Rotx(roll)Roty(pitch)Rotz(yaw)*node1Initial.  As you can see, this is only 1 equation with 3 unknowns,
        so 3 node pairings would be required for this.
        params:
            nodeXInit:  the location of the node relative to the CENTROID of the system before the rotation occurs
            nodeXFinal: the location of the node relative to the CENTROID of the system after rotation occurs.
        returns:
            roll: the degrees the system rotated in the x direction
            pitch: the degrees the system rotated in the y direction
            yaw: the degrees the system rotated in the z direction.
            """
        # https://math.stackexchange.com/questions/3998207/how-to-calculate-the-rotation-matrix-from-other-known-values is fairly useful.

        # This is the matrix that corresponds to the actual current accelerometer values.
        F = np.array([node1Final, node2Final, node3Final]).T

        # Is this even valid for acceleration? I don't think so...
        # deltaF = np.array([node2Final-node1Final, node3Final-node1Final, np.cross(node2Final-node1Final, node3Final-node1Final)]).T

        # This is the matrix that represents the initial values of the system's accelerometers.
        I = np.array([node1Init, node2Init, node3Init]).T

        # deltaI = np.array([node2Init-node1Init, node3Init-node1Init, np.cross(node2Init-node1Init, node3Init-node1Init)]).T
        # R is the rotation that occured to get from I to F.  So the equation is F = R*I; R = F*I^-1

        R = F.dot(np.linalg.inv(I))
        # R = deltaF.dot(np.linalg.inv(deltaI))

        if np.linalg.det((R)) < 0:

            R = F.dot(np.linalg.inv(I))

        for i in range(len(R)):
            R[i, :] = R[i, :]/np.linalg.norm(R[i,:])
        return R
        # thetax = (np.arctan2(R[2, 1], R[2, 2]))
        # thetay = (np.arctan2(-R[2, 0], np.sqrt(R[2, 1] ** 2 + R[2, 2] ** 2)))
        # thetaz = (np.arctan2(R[1, 0], R[0, 0]))
        # degrees = np.array([thetaz, thetay, thetax]) * (180 / np.pi)
        #
        # return degrees  # returns in degrees.


if __name__ == "__main__":
    accel = AccelerometerSimulation()
    # accel.determineAngles(1,2,3,4,5,6)
