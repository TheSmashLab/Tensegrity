import cv2
import matplotlib.pyplot as plt
from mpl_toolkits import mplot3d
import numpy as np
import os
from typing import List, Optional, Tuple

from src.PayloadOptimizer.PayloadModel import PayloadModel


class SimplifiedTensegrityModel:
    """
    this class' goal is to receive shock in a similar manner that a tensegrity model does, but with simplifying assumptions to make the model easier to modify.
    These assumptions are:
       1. that this simply model will approximate the 20 sided figure as a figure with only a base, a top, and connecting nodes. The flexure of the actual
       system will be approximated by adjusting the spring constant connecting the bottom of the structure to the roof of the structure.  Ideally,
       the spring constant can be determined through optimization.
    """

    def __init__(self, nodeMass: float, springConstant: float, dt: float = .001, timeFinal: float = 5, damping: float = 0.001, springEquToTopScale: float = 1.5,
                 payloadmass=6, payloadCornerPoints: np.ndarray[np.ndarray[float]] = np.array([[-1, -1, 2], [-1, 1, 2], [-1, -1, 4], [-1, 1, 4], [1, -1, 2],
                                                                                               [1, 1, 2], [1, -1, 4], [1, 1, 4]]) * 1 / 4,
                 payloadEdgeConnections: np.ndarray[np.ndarray[float]] = np.array(
                     [[0, 1], [0, 2], [0, 4], [1, 5], [1, 3], [2, 6], [2, 3], [3, 7], [4, 6], [4, 5],
                      [5, 7], [6, 7]]), Ac=.0000001, maximumGs=150):
        """
        The base system information for the simplified model is contained hereIn, see comments around the different sections of code to see what each section does.
        :param nodeMass: The mass of each node of the simulation.
        :param springConstant: The equivalent spring constant that the system passes in, can be changed as a system tuning parameter.
        :param dt: The timestep for the rk4 simulation and used for animating.
        :param timeFinal: the length of the simulation
        :param damping: how to damp the system based off the velocity at each point.
        :param springEquToTopScale: How the spring constant of the system compares to the spring constant of the base.
        :param payloadmass: mass of the payload
        :param payloadCornerPoints: used to define the vertices of the payload
        :param payloadEdgeConnections: used to define how the payload's vertices connect.
        :param Ac: the initial cross-sectional Area of the wires. To be minimized with constraints.
        """
        # something the optimizer can optimize - can be scaled to affect the height of the structure.  Basics will remain the same for the entire model.
        self.bottom: np.ndarray[np.ndarray[float]] = np.array([[1, -np.sqrt(3) / 3, 0], [-1, -np.sqrt(3) / 3, 0], [0, 2 * np.sqrt(3) / 3, 0]])
        self.bottomOrig: np.ndarray[np.ndarray[float]] = np.copy(self.bottom)
        self.top: np.ndarray[np.ndarray[float]] = np.array([[0, -2 * np.sqrt(3) / 3, 2 * 1.618], [-1, np.sqrt(3) / 3, 2 * 1.618],
                                                            [1, np.sqrt(3) / 3, 2 * 1.618]])
        self.topOrig: np.ndarray[np.ndarray[float]] = np.copy(self.top)

        # The initial combined states of each system
        self.combined: np.ndarray[np.ndarray[float]] = np.append(self.top, self.bottom, axis=0)
        self.initialState: np.ndarray[np.ndarray[float]] = np.append(self.bottom, self.top, axis=0)
        self.initialFullState: np.ndarray[np.ndarray[float]] = None

        # These are the vectors of the springs from their base point to their top point.
        self.springVectors: np.ndarray[np.ndarray[float]] = np.array([self.bottom[0] - self.top[0], self.bottom[0] - self.top[2], self.bottom[1] - self.top[0],
                                                                      self.bottom[1] - self.top[1], self.bottom[2] - self.top[2], self.bottom[2] - self.top[1]])

        # self.stringVectorsBases = np.array([self.top[0] - self.top[1], self.top[1] - self.top[2], self.top[2] - self.top[0],
        #                                    self.bottom[0] - self.bottom[1], self.bottom[1] - self.bottom[2], self.bottom[2] - self.bottom[0]])

        # used for setting the plot size in animate
        self.axisLength: float = 3

        self.nodeMassOrig: float = nodeMass
        self.nodeMass: float = nodeMass

        # Initializes the payload
        self.payload: PayloadModel = PayloadModel(payloadmass, payloadCornerPoints, payloadEdgeConnections)
        payloadCOM: np.ndarray[float] = self.payload.getCOM()
        self.payloadCOM: np.ndarray[float] = payloadCOM
        self.origPayloadCOM: np.ndarray[float] = payloadCOM

        # initializes the strings to the center of the payload
        self.stringsToPayload: np.ndarray[np.ndarray[float]] = np.array([self.bottom[0] - payloadCOM, self.bottom[1] - payloadCOM, self.bottom[2] - payloadCOM,
                                                                         self.top[0] - payloadCOM, self.top[1] - payloadCOM, self.top[2] - payloadCOM])

        # original lengths to be used in computing the dynamics.
        self.origBaseLength: float = np.linalg.norm(self.bottom[0] - self.bottom[1])
        self.origSpringLength: float = np.linalg.norm(self.springVectors[0])
        self.originalPayloadStringLengths: np.ndarray[np.ndarray[float]] = np.array([np.linalg.norm(self.stringsToPayload[0]),
                                                                                     np.linalg.norm(self.stringsToPayload[1]),
                                                                                     np.linalg.norm(self.stringsToPayload[2]),
                                                                                     np.linalg.norm(self.stringsToPayload[3]),
                                                                                     np.linalg.norm(self.stringsToPayload[4]),
                                                                                     np.linalg.norm(self.stringsToPayload[5])])

        # The spring constants for the dynamic models, may be changed later
        self.Ac: float = Ac
        self.equivalentSpringConstant: float = springConstant
        self.EStiff: float = 2e11
        self.stiffSpringConstant: List[float] = []
        self.setStiffSpringConstant(Ac)

        self.springEquToTopScale: float = springEquToTopScale
        self.SameSpringConstant: float = springConstant * springEquToTopScale
        self.minDistance: float = 9

        # how long to simulate the model for
        self.dt: float = dt  # used in the integration step
        self.timeFinal: float = timeFinal

        # Inherent system properties
        self.damping: float = damping
        self.gravity: np.ndarray[np.ndarray[float]] = np.array([[0, 0, 9.81]])

        # this is the maximum acceleration that the system felt.
        self.payloadAccel: float = 0
        self.maximumGs: float = maximumGs

    def animateMotion(self, videoName: str = "default.mp4", axisLength: float = 3) -> None:
        """
        animates the motion of the system by graphing the system at various points in time and stitching those graphs together into a video.
        :param videoName: the name to save the video file to.
        :return: None
        """
        # Parameters needed to set up graph and points to plot.
        print("animating")
        path: str = os.getcwd() + '/placeholderFolders/'
        time: np.ndarray[np.ndarray[float]] = np.arange(0, self.timeFinal, self.dt)

        for t in range(int(len(self.stateCoords) / 10)):
            x: List[float] = []
            y: List[float] = []
            z: List[float] = []

            fig: plt.figure = plt.figure()
            ax: mplot3d.Axes3D = fig.add_subplot(projection='3d')
            ax.scatter3D(x, z, y, c=y, cmap='cividis')

            ax.set_xlim(-axisLength, axisLength)
            ax.set_ylim(-axisLength, axisLength)
            ax.set_zlim(0, axisLength * 2)
            ax.set_xlabel('x')
            ax.set_ylabel('z')
            ax.set_zlabel('y')
            bLen: int = len(self.bottom)

            # Plots the base points
            for i in range(bLen):
                x.append(self.stateCoords.item(t * 10, i, 0))
                z.append(self.stateCoords.item(t * 10, i, 1))
                y.append(self.stateCoords.item(t * 10, i, 2))
                plt.plot(x[i], z[i], y[i], '-go')

                if 0 < i:
                    plt.plot(x[i - 1:i + 1], z[i - 1:i + 1], y[i - 1:i + 1], 'r')

                    if i + 1 == bLen:
                        xtmp = [x[0], x[i]]
                        ytmp = [y[0], y[i]]
                        ztmp = [z[0], z[i]]
                        plt.plot(xtmp, ztmp, ytmp, 'r')

            # Plots the top points
            for i in range(len(self.top)):
                x.append(self.stateCoords.item(t * 10, i + 3, 0))
                z.append(self.stateCoords.item(t * 10, i + 3, 1))
                y.append(self.stateCoords.item(t * 10, i + 3, 2))
                plt.plot(x[i + bLen], z[i + bLen], y[i + bLen], '-go')

                if 0 < i:
                    plt.plot(x[i + 2:i + 4], z[i + 2:i + 4], y[i + 2:i + 4], 'r')

                    if i + 1 == bLen:
                        xtmp: List[float] = [x[bLen], x[i + bLen]]
                        ytmp: List[float] = [y[bLen], y[i + bLen]]
                        ztmp: List[float] = [z[bLen], z[i + bLen]]
                        plt.plot(xtmp, ztmp, ytmp, 'r')

            # Plots the springs between base and top
            for i in range(bLen):
                xtmp: List[float] = []
                ytmp: List[float] = []
                ztmp: List[float] = []
                xtmp.append(x[i])
                ytmp.append(y[i])
                ztmp.append(z[i])
                xtmp.append(x[i + 3])
                ytmp.append(y[i + 3])
                ztmp.append(z[i + 3])
                plt.plot(xtmp, ztmp, ytmp, '-y')

                xtmp = []
                ytmp = []
                ztmp = []
                xtmp.append(x[i])
                ytmp.append(y[i])
                ztmp.append(z[i])

                if 2 != i + 2:
                    xtmp.append(x[i + 2])
                    ytmp.append(y[i + 2])
                    ztmp.append(z[i + 2])
                else:
                    xtmp.append(x[i + 5])
                    ytmp.append(y[i + 5])
                    ztmp.append(z[i + 5])

                plt.plot(xtmp, ztmp, ytmp, '-y')

            self.payload.setNewPayloadPosition(self.stateCoords[t * 10][6])
            self.payload.plot(plt)
            self.payloadCOM = self.payload.getCOM()

            for i in range(len(self.combined)):
                xtmp = [self.payloadCOM[0]]
                ztmp = [self.payloadCOM[1]]
                ytmp = [self.payloadCOM[2]]

                xtmp.append(self.stateCoords.item(t * 10, i, 0))
                ytmp.append(self.stateCoords.item(t * 10, i, 2))
                ztmp.append(self.stateCoords.item(t * 10, i, 1))
                plt.plot(xtmp, ztmp, ytmp, '-g')

            tString: str = str(t * 10)
            tLength: int = len(str(int(time[-1] / self.dt)))

            if (len(tString) < tLength):
                strFront: str = ''

                for j in range(len(tString), tLength):
                    strFront = strFront + '0'

                tString = strFront + tString

            plt.savefig(os.path.join(path, 'pngFolder', ('myplot' + tString + ".png")), dpi=75)
            plt.close()

        image_folder: str = os.path.join(path, 'pngFolder')

        images: List[str] = sorted([img for img in os.listdir(image_folder) if img.endswith(".png")])
        frame: np.ndarray[np.ndarray] = cv2.imread(os.path.join(image_folder, images[0]))
        height: int
        width: int
        layers: int

        height, width, layers = frame.shape
        print("creating video")

        videoPath: str = os.path.join(path, 'videoFolder/')
        fourcc: cv2.VideoWriter_fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        video: cv2.VideoWriter = cv2.VideoWriter(videoPath + videoName, fourcc, 20, (width, height))

        for image in images:
            video.write(cv2.imread(os.path.join(image_folder, image)))

        cv2.destroyAllWindows()
        video.release()

        test = os.listdir(image_folder)

        for images in test:
            if images.endswith(".png"):
                os.remove(os.path.join(image_folder, images))

    def constraintDistanceReturn(self, args, returnMore: bool = False) -> Tuple[float] or float:
        """
        Runs the rk4 algorithm to determine the minimum location of the payload
        :param args: The arguments that the system needs.
        :param returnMore: The option to return more information from the simulation.
        :return:
        """
        self.setEquSpringConst(args[0])
        self.setStiffSpringConstant(args[1])
        self.setStructureSize(args[2])
        self.setPayloadLocation(args[3])

        self.rk4(self.initialFullState)
        self.constraintPayloadLocation()
        self.nodeMass = self.nodeMassOrig
        holder: float = self.minDistance + .1
        holder2: float = self.constraintPayloadShock()

        if returnMore:
            return holder, holder2

        return holder

    def constraintPayloadLocation(self):
        """
        sets a constraint saying that the payload must stay within the boundaries of the structure for any given impact,  will return a float where an element is positive only if it is outside of
        the structural bounds.
        :return:

        Inputs:
        cornerPoints - np array with corner points of payload
                        that is adjusted using the center of mass
        stateCoords - np array with coordinates of the bottom points
                        of the structure

        Outputs:
        distance - np array with distance from each point of the payload
                        to the bottom plane of the structure
        """

        stateCoords: np.ndarray[np.ndarray[float]] = self.stateCoords
        cornerPoints: np.ndarray[float] = self.payload.cornerPointsMod

        # Call shortest_distance for each point defining the payload
        distance = np.zeros((len(stateCoords), len(cornerPoints)))
        # loops through each stateCoord

        for j in range(len(stateCoords)):
            p1: np.ndarray[np.ndarray[float]] = stateCoords[j][0]
            p2: np.ndarray[np.ndarray[float]] = stateCoords[j][1]
            p3: np.ndarray[np.ndarray[float]] = stateCoords[j][2]
            planeNorm: np.ndarray[np.ndarray[float]] = self.plane(p1, p2, p3)

            # Place each answer into a np array (for loop)
            # shortest_distance(x1, y1, z1, a, b, c, d)+

            for i in range(len(cornerPoints)):
                distance[j][i] = self.shortest_distance(cornerPoints[i, :] + stateCoords[j][6] - self.payload.getCOM(), p1, planeNorm)

        self.minDistance = np.max(distance)

    def constraintPayloadShock(self):
        """
        returns an array that is only positive if the acceleration on the payload is greater than a specified threshold.
        :return: the payload accelerations felt.
        """
        maximumGs: float = np.copy(self.payloadAccel).item(0)
        self.payloadAccel = 0

        return maximumGs

    def dynamics(self, state: np.ndarray[np.ndarray[float]]):
        """
        This will be a simple dynamic function to describe the acceleration of each node, a simple F = ma analysis using springs on each node and the springs.
        :param state: array of positions and velocities of each node and the payload, all positions then all velocities.  Order: bottom, top, payload, so a 3X14 vector
        :return: stateDot - what the RK4 integrator will integrate to determine the next state.
        """
        # the state will be composed of the x and xdot of each node.  Will return the xdot and xddot of each node.
        # each node connects to 4 other nodes, so only 1 node in each set does not connect.
        # can also think of it like 1 node for each bar, makes sense that 1 wouldn't connect with that logic.
        accelerations: np.ndarray[np.ndarray[float]] = np.zeros([7, 3])
        FOnPayload: np.ndarray[float] = np.array([0, 0, 0])

        for i in range(6):  # one for each node, will do the payload separately at the bottom.
            # pairs for the springs: (0,3),(0,5),(1,3),(1,4),(2,4),(2,5)  Other way:  (3,0),(3,1),(4,1),(4,2),(5,2)(5,0)
            separation1Same: np.ndarray[np.ndarray[float]]
            separation2Same: np.ndarray[np.ndarray[float]]
            separation1Spring: np.ndarray[np.ndarray[float]]
            separation2Spring: np.ndarray[np.ndarray[float]]

            if 3 > i:
                separation1Same = state[i] - state[(i + 1) % 3]  # the new vectors between the same side nodes
                separation2Same = state[i] - state[(i + 2) % 3]  # the new vectors between the same side nodes

                separation1Spring = state[i] - state[3 + (i + 2) % 3]  # the new vectors between the same side nodes
                separation2Spring = state[i] - state[3 + i]  # the new vectors between the same side nodes
            else:
                separation1Same = state[i] - state[(i + 1) % 3 + 3]
                separation2Same = state[i] - state[(i + 2) % 3 + 3]

                separation1Spring = state[i] - state[(i + 1) % 3]  # the new vectors between the same side nodes
                separation2Spring = state[i] - state[i % 3]  # the new vectors between the same side nodes

            length1Same: float = np.linalg.norm(separation1Same)
            length2Same: float = np.linalg.norm(separation2Same)
            unitVec1Same: np.ndarray[np.ndarray[float]] = separation1Same / length1Same
            unitVec2Same: np.ndarray[np.ndarray[float]] = separation2Same / length2Same
            FSameSide: np.ndarray[np.ndarray[float]] = self.SameSpringConstant * (unitVec2Same * (self.origBaseLength - length2Same) + unitVec1Same * (
                    self.origBaseLength - length1Same))  # This is from the unspringy springs.

            length1Spring: float = np.linalg.norm(separation1Spring)
            length2Spring: float = np.linalg.norm(separation2Spring)
            unitVec1Spring: np.ndarray[np.ndarray[float]] = separation1Spring / length1Spring
            unitVec2Spring: np.ndarray[np.ndarray[float]] = separation2Spring / length2Spring
            FSprings: np.ndarray[np.ndarray[float]] = self.equivalentSpringConstant * (unitVec2Spring * (self.origSpringLength - length2Spring)
                                                                                       + unitVec1Spring * (self.origSpringLength - length1Spring))

            separation = state[6] - state[i]
            length = np.linalg.norm(separation)

            if 0 < length - self.originalPayloadStringLengths[i]:
                unitVec: np.ndarray[np.ndarray[float]] = separation / length
                FPayloadString: np.ndarray[np.ndarray[float]] = self.stiffSpringConstant[i] * unitVec * (length - self.originalPayloadStringLengths[i])
                FOnPayload = FOnPayload - FPayloadString
            else:
                FPayloadString = np.array([0, 0, 0])

            acceleration: np.ndarray[np.ndarray[float]] = (1 / self.nodeMass * (FSameSide + FSprings + FPayloadString - self.damping * state[i + 7])
                                                           - self.gravity)
            accelerations[i] = acceleration

        accelerations[6] = FOnPayload / self.payload.getMass() - self.gravity - self.damping * state[13]

        if np.linalg.norm(accelerations[6]) / 9.81 > self.payloadAccel:
            self.payloadAccel = np.linalg.norm(accelerations[6]) / 9.81

        stateDot: np.ndarray[np.ndarray[float]] = np.append(state[7:14], accelerations, axis=0)
        return stateDot

        # Will calc force at each node... From FBD each node has: 2 spring forces, 2 string stablizing forces, 1 string to middle of the payload, and external forces(gravity).
        # As defined in self.stringVectorBases, self.springVectors and self.stringsToPayload
        # solve this at each node for acceleration, then use a rk4 algorithm to integrate over time. update nodes.

    # this function will change over time as more objectives are added to the equation (so the inputs will grow, and more constraints will be added as well.
    # This will assess penalty on the genetic optimizer and minimize all the different constants (which will be weighted according to mass added.).
    def GAValue(self, args) -> float:
        """
        The objective function tailored to the genetic algorithm that was created.
        Parameters
        ----------
        args:  the arguments for the function,

        Returns
        -------

        """
        if 20 >= args[0] or 0 >= args[1] or 0 >= args[2] or 0 >= args[3]:
            return np.inf

        if 1 < args[3]:
            args[3] = 1

        calcSpringConst: float = args[0] + args[1] * 3e6 + args[2] * 10000
        maximumDist: float = self.constraintDistanceReturn(args)
        gsFelt: float = self.constraintPayloadShock()

        if 0 < maximumDist:
            calcSpringConst = maximumDist * 100000 + calcSpringConst
        elif not np.isfinite(maximumDist):
            calcSpringConst = np.inf

        if gsFelt > self.maximumGs:
            calcSpringConst = (gsFelt - self.maximumGs) * 10000 + calcSpringConst

        return calcSpringConst

    # Not used typically, so not annotated.
    def GAParticleValue(self, newEquSpringConst):
        """
        Used in a homework to get a particleSwarm to work correctly.
        Parameters
        ----------
        newEquSpringConst:  The objective function essentially.

        Returns
        -------
        The weighted value for what the spring constant would be.
        """
        calcSpringConst = newEquSpringConst['x1']
        maximumDist = self.constraintDistanceReturn(newEquSpringConst['x1'])
        print(maximumDist)
        if maximumDist < 0:
            pass
        elif np.isnan(maximumDist):
            calcSpringConst = np.inf
        else:
            calcSpringConst = maximumDist * 100000 + calcSpringConst
        print(calcSpringConst)

        return -calcSpringConst

    def getPayload(self) -> PayloadModel:
        """
        returns the payload object
        :return: the payload object.
        """
        return self.payload

    def getInitialState(self) -> np.ndarray[np.ndarray[float]]:
        """
        gets the stored initial state of the system, including that of the payload.
        :return: the initial state of the system.
        """
        return np.append(self.initialState, np.array([self.getPayload().getCOM()]), axis=0)

    def impactBottom(self, v0: np.ndarray[np.ndarray[float]]):
        """
        Simulates the system as if the bottom of the system impacted a surface by giving the bottom of the system an initial velocity
        :param v0: initial velocity of the bottom of the system
        :return: None
        """
        initialPosition: np.ndarray[np.ndarray[float]] = self.getInitialState()
        initialVelocity: np.ndarray[np.ndarray[float]] = np.zeros([7, 3])
        initialState: np.ndarray[np.ndarray[float]] = np.append(initialPosition, initialVelocity, axis=0)
        initialState.T[2][10:13] = np.ones(3) * v0

        self.rk4(initialState)

    def impactTop(self, v0) -> np.ndarray[np.ndarray[float]]:
        """
        Simulates the system as if the top of the system impacted a surface by giving the top of the system an initial velocity
        :param v0: initial velocity of the top of the system
        :return: None
        """
        initialPosition: np.ndarray[np.ndarray[float]] = self.getInitialState()
        initialVelocity: np.ndarray[np.ndarray[float]] = np.zeros([7, 3])
        initialState: np.ndarray[np.ndarray[float]] = np.append(initialPosition, initialVelocity, axis=0)
        initialState.T[2][7:10] = np.ones(3) * -v0

        self.rk4(initialState)

    @staticmethod
    def plane(point1: np.ndarray[float], point2: np.ndarray[float], point3: np.ndarray[float]) -> np.ndarray[np.ndarray[float]]:
        """
        Creates a plane defined by a unit vector given 3 initial points.
        :param point1: first point defining the plane.
        :param point2: second point defining the plane.
        :param point3: third point defining the plane.
        :return:
        """
        # These two vectors are in the plane
        v1: np.ndarray[float] = point3 - point1
        v2: np.ndarray[float] = point2 - point1

        # The cross product is a vector normal to the plane
        cp: np.ndarray[np.ndarray[float]] = np.cross(v1, v2)
        cp = cp / np.linalg.norm(cp)

        return cp

    def plotFigure(self) -> None:
        """
        plots what the figure looks like with the inputted payload.
        :return: None
        """
        x: List[float] = []
        y: List[float] = []
        z: List[float] = []
        fig: plt.figure = plt.figure()
        ax: mplot3d.Axes3D = fig.add_subplot(projection='3d')
        ax.scatter3D(x, z, y, c=y, cmap='cividis')

        ax.set_xlim(-self.axisLength, self.axisLength)
        ax.set_ylim(-self.axisLength, self.axisLength)
        ax.set_zlim(0, self.axisLength * 2)
        ax.set_xlabel('x')
        ax.set_ylabel('y')
        ax.set_zlabel('z')
        bLen = len(self.bottom)

        # plots the base points
        for i in range(bLen):
            x.append(self.bottom.item(i, 0))
            z.append(self.bottom.item(i, 1))
            y.append(self.bottom.item(i, 2))
            plt.plot(x[i], z[i], y[i], '-go')

            if 0 < i:
                plt.plot(x[i - 1:i + 1], z[i - 1:i + 1], y[i - 1:i + 1], 'r')

                if i + 1 == bLen:
                    xtmp: List[float] = [x[0], x[i]]
                    ytmp: List[float] = [y[0], y[i]]
                    ztmp: List[float] = [z[0], z[i]]
                    plt.plot(xtmp, ztmp, ytmp, 'r')

        # plots the top points
        for i in range(len(self.top)):
            x.append(self.top.item(i, 0))
            z.append(self.top.item(i, 1))
            y.append(self.top.item(i, 2))
            plt.plot(x[i + bLen], z[i + bLen], y[i + bLen], '-go')

            if i > 0:
                plt.plot(x[i + 2:i + 4], z[i + 2:i + 4], y[i + 2:i + 4], 'r')

                if i + 1 == bLen:
                    xtmp: List[float] = [x[bLen], x[i + bLen]]
                    ytmp: List[float] = [y[bLen], y[i + bLen]]
                    ztmp: List[float] = [z[bLen], z[i + bLen]]
                    plt.plot(xtmp, ztmp, ytmp, 'r')

        # plots the springs between base and top
        for i in range(bLen):
            xtmp: List[float] = []
            ytmp: List[float] = []
            ztmp: List[float] = []
            xtmp.append(x[i])
            ytmp.append(y[i])
            ztmp.append(z[i])
            xtmp.append(x[i + 3])
            ytmp.append(y[i + 3])
            ztmp.append(z[i + 3])
            plt.plot(xtmp, ztmp, ytmp, '-y')

            xtmp = []
            ytmp = []
            ztmp = []
            xtmp.append(x[i])
            ytmp.append(y[i])
            ztmp.append(z[i])

            if 2 != i + 2:
                xtmp.append(x[i + 2])
                ytmp.append(y[i + 2])
                ztmp.append(z[i + 2])
            else:
                xtmp.append(x[i + 5])
                ytmp.append(y[i + 5])
                ztmp.append(z[i + 5])

            plt.plot(xtmp, ztmp, ytmp, '-y')

        self.payload.plot(plt)

        for i in range(len(self.combined)):
            xtmp = [self.payloadCOM[0]]
            ytmp = [self.payloadCOM[1]]
            ztmp = [self.payloadCOM[2]]
            xtmp.append(self.combined.item(i, 0))
            ytmp.append(self.combined.item(i, 1))
            ztmp.append(self.combined.item(i, 2))
            plt.plot(xtmp, ytmp, ztmp, '-g')

        plt.show()

    def rk4(self, state: List[float]) -> None:
        """
        rk4 is the runge-kutta-4 method which is used for integrating the dynamics over time. includes the method
        call to utilize the controller, saves some data used for other analytics.
        :param state: the initial state of the system.
        :param tspan: the number of time increments that the system is integrated over.
        """
        # TODO:  Need to remove the np.append statement to improve code efficency, should just declare an array of zeros of the final stateCoordSize at the beginning and change by indexing i.

        stateCoords: np.ndarray[np.ndarray[float]] = np.array([state])
        tspan = int(self.timeFinal / self.dt)
        statesToSave: int = 1  # int(1 / self.dt / 100)  # the inverse framerate for the video, 1 is all states are saved.

        # Sets the location on those 2 controllers.
        for i in range(tspan):
            # can move this into its own fuction once completed. Might have to test for positive force going up on the node
            # instead to get the conditional here correct.

            # first k1 iteration is correct
            k1: np.ndarray[np.ndarray[float]] = self.dt * (self.dynamics(state))
            k2: np.ndarray[np.ndarray[float]] = self.dt * (self.dynamics(state + k1 / 2))
            k3: np.ndarray[np.ndarray[float]] = self.dt * (self.dynamics(state + k2 / 2))
            k4: np.ndarray[np.ndarray[float]] = self.dt * (self.dynamics(state + k3))
            k: np.ndarray[np.ndarray[float]] = (k1 + 2 * k2 + 2 * k3 + k4) / 6

            state = state + k

            # will now show every node position instead of just the ones changing with the state.
            if 0 == i % statesToSave and 0 != i:
                stateCoords = np.append(stateCoords, np.array([state]), axis=0)

        self.stateCoords = stateCoords

    def setEquSpringConst(self, EquSpringConst: float) -> None:
        """
        This function changes the equivilant spring constant of the system, this registers more force on the payload, but will slow it down faster.
        :param EquSpringConst: The new equivilant spring constant.
        :return:
        """
        self.equivalentSpringConstant = EquSpringConst
        self.SameSpringConstant = EquSpringConst * self.springEquToTopScale

    def setInitialFullState(self, state: np.ndarray[np.ndarray[float]]) -> None:
        """
        :param state:  The initial state of the system.
        :return: None
        """
        self.initialFullState = state

    def setPayloadLocation(self, COMzOffsetPer: float):
        """
        changes the initial payload location so that the payload's COM is at the COM Location.
        :param COMzOffset: the percentage of the distance between the COM of the object and the top of the structure for the payload to be placed.
        :return:
        """
        # the offset will come as a percentage, the new COM will be the percentage of the distance between the current COM
        # and the scaled top and bottom.

        distance: float = self.top.item(0, 2) - self.payload.getMaxZ()

        if 1 < COMzOffsetPer:
            COMzOffsetPer = 1

        newPayloadLoc: np.ndarray[np.ndarray[float]] = self.payloadCOM + np.array([0, 0, COMzOffsetPer * distance])
        self.payload.setNewPayloadPosition(newPayloadLoc)
        self.initialFullState[6] = self.payload.getCOM()
        payloadCOM: np.ndarray[np.ndarray[float]] = self.payload.getCOM()

        self.stringsToPayload = np.array([self.bottom[0] - payloadCOM, self.bottom[1] - payloadCOM, self.bottom[2] - payloadCOM,
                                          self.top[0] - payloadCOM, self.top[1] - payloadCOM, self.top[2] - payloadCOM])
        self.originalPayloadStringLengths = np.array(
            [np.linalg.norm(self.stringsToPayload[0]), np.linalg.norm(self.stringsToPayload[1]), np.linalg.norm(self.stringsToPayload[2]),
             np.linalg.norm(self.stringsToPayload[3]), np.linalg.norm(self.stringsToPayload[4]), np.linalg.norm(self.stringsToPayload[5])])
        self.setStiffSpringConstant(self.Ac)
        self.payloadCOM = payloadCOM

        # def setPayloadOrientation(self, rotMat):
        #     """
        #     changes the payloads orientation so that it is best situated for impact
        #     :param rotMat: the rotation matrix to specify the new orientation of the payload.  May need to be simplified to a degree for the payload to be rotated about specified axis.
        #     :return:
        #     """

    def setStiffSpringConstant(self, Ac: float) -> None:
        """
        Calculated the stiffSpring constants for each of the payload strings based on the uniform cross sectional areas of the wires and the un-uniform lengths.
        :param Ac: Cross sectional area of the wires
        :return: None
        """
        self.Ac = Ac
        self.stiffSpringConstant = 1 / np.copy(self.originalPayloadStringLengths) * Ac * self.EStiff

    def setStructureSize(self, scalingFactor: float) -> None:
        """
        This function is meant to scale the tensegrity structure to allow for the indicated impact to the system, this is to be minimized so we can have a minimal structural mass.
        :param scalingFactor:
        :return:
        """
        self.bottom = self.bottomOrig * scalingFactor
        self.top = self.topOrig * scalingFactor
        self.combined = np.append(self.top, self.bottom, axis=0)  # used for easier plotting.
        self.initialState = np.append(self.bottom, self.top, axis=0)  # used for easier initialization.

        # These are the vectors of the springs from their base point to their top point.
        self.springVectors = np.array([self.bottom[0] - self.top[0], self.bottom[0] - self.top[2], self.bottom[1] - self.top[0],
                                       self.bottom[1] - self.top[1], self.bottom[2] - self.top[2],
                                       self.bottom[2] - self.top[1]])  # I think what I really care about are the z components.(kinda)

        # self.stringVectorsBases = np.array([self.top[0] - self.top[1], self.top[1] - self.top[2], self.top[2] - self.top[0],
        #                                    self.bottom[0] - self.bottom[1], self.bottom[1] - self.bottom[2], self.bottom[2] - self.bottom[0]])

        # used for setting the plot size in animate
        self.axisLength = self.axisLength * scalingFactor  # should make this dynamically change with the size that the optimizer chooses.

        self.nodeMass = self.nodeMass * scalingFactor  # this is how the dynamics of the model will actually be affected under shock conditions.

        self.payload.setNewPayloadPosition(self.origPayloadCOM * scalingFactor)
        payloadCOM = self.payload.getCOM()

        self.stringsToPayload = np.array([self.bottom[0] - payloadCOM, self.bottom[1] - payloadCOM, self.bottom[2] - payloadCOM,
                                          self.top[0] - payloadCOM, self.top[1] - payloadCOM, self.top[2] - payloadCOM])

        # original lengths to be used in computing the dynamics.
        self.origBaseLength = np.linalg.norm(self.bottom[0] - self.bottom[1])
        self.origSpringLength = np.linalg.norm(self.springVectors[0])
        self.originalPayloadStringLengths = np.array(
            [np.linalg.norm(self.stringsToPayload[0]), np.linalg.norm(self.stringsToPayload[1]), np.linalg.norm(self.stringsToPayload[2]),
             np.linalg.norm(self.stringsToPayload[3]), np.linalg.norm(self.stringsToPayload[4]), np.linalg.norm(self.stringsToPayload[5])])
        self.setStiffSpringConstant(self.Ac)
        self.initialFullState[0:6] = self.initialState
        self.initialFullState[6] = payloadCOM
        self.payloadCOM = payloadCOM

    @staticmethod
    def shortest_distance(cornerPoint: np.ndarray[np.ndarray[float]], basePoint: np.ndarray[np.ndarray[float]], planeNorm: np.ndarray[np.ndarray[float]]) -> (
            float):
        """
        returns the shortest distance between 2 points using the normal vector of a plane.
        :param cornerPoint: the corner of the payload being measured to the ground.
        :param basePoint: the base of the structure, where the ground is.
        :param planeNorm: The normal plane to the ground, the vector to measure distance over.
        :return: the total distance from the corner to the ground.
        """
        # get the length from corner point to base point and dot it with planeNorm
        vector: np.ndarray[np.ndarray[float]] = basePoint - cornerPoint
        return np.dot(vector, planeNorm)
