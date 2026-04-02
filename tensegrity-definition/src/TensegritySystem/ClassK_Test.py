import numpy as np
import numpy.linalg as la
from typing import List, Tuple

import src.Accelerometer.AccelerometerController
from src.TensegritySystem import Systems, Controller, Nodes as N
from src.Utils import CommonMatrixOperations

PATH: str = '/'
FOLDER_PATH: str = r'/pngFolder'


class ClassK_Test():
    def __init__(self, nodes: np.ndarray[np.ndarray[float]], barConn: np.ndarray[np.ndarray[float]], strConn: np.ndarray[np.ndarray[float]],
                 system: Systems.System, P: np.ndarray[np.ndarray[float]], D: np.ndarray[np.ndarray[float]], s0: np.ndarray[float], Nd0: List[float],
                 W: np.ndarray[np.ndarray[float]], tf: float = .5, dt: float = .0001, axisLength: float = 3):
        """
        The init method intializes the system for the upcoming dynamics.
        :param nodes: the nodes of the system
        :param barConn: the bar connection matrix
        :param strConn: the string connection matrix
        :param system: the system as defined in system.py, has useful properties that are needed later in the dynamics.
        :param P: the system decomposition matrix
        :param D: TODO: another matrix
        :param s0: initial prestress conditions
        :param Nd0: initial velocity of each node of the system.
        :param W: initial forces
        :param tf: final time of the simulation.
        :param dt: the time step
        :param axisLength: the size of the axes in the animation graph.
        """
        self.nodes: np.ndarray[np.ndarray[float]] = nodes
        self.barConn: np.ndarray[np.ndarray[float]] = barConn
        self.strConn: np.ndarray[np.ndarray[float]] = strConn
        self.system: Systems.System = system
        self.P: np.ndarray[np.ndarray[float]] = P
        self.D: np.ndarray[np.ndarray[float]] = D
        self.s0: np.ndarray[float] = s0
        self.Nd0: np.ndarray[np.ndarray[float]] = Nd0
        self.W: np.ndarray[np.ndarray[float]] = W
        self.tf: float = tf
        self.dt: float = dt

        self.currentNode: np.ndarray[np.ndarray[float]]

        # W_orig is used to work with pinned Nodes. By doing this, the original forces are available, so the W matrix can be properly updated.
        self.W_orig: np.ndarray[np.ndarray[float]] = np.copy(W)

        # The following are needed to set the correct 3D graph properties, assume the graph is cubic, so the range of each axis is identical.
        self.axisLength: int = axisLength

        # The following if created to save the node history of the model, since it is not the equivilant of the state.
        self.nodeHist: np.ndarray[np.ndarray[np.ndarray[float]]] = np.array([[[]]])
        self.stateHist: np.ndarray[np.ndarray[np.ndarray[float]]] = np.array([[[]]])
        self.counter: int = -1

        # These three are important for machine learning applications.
        self.stateCoords: np.ndarray[np.ndarray[float]] = np.array([[]])
        self.forcesOverTime: np.ndarray[np.ndarray[float]] = np.array([[]])

        # The following are placeholders for defaults set in a later function, probably can be changed to defaults set upon initialization in future iterations.
        self.m: np.ndarray[float]
        self.ms: np.ndarray[float]
        self.mgyro: np.ndarray[float]
        self.gyro_r: np.ndarray[float]
        self.gyro_h: np.ndarray[float]
        self.pDef: List[float]
        self.dDef: List[float]
        self.wDef: np.ndarray[float]
        self.k: np.ndarray[float]
        self.c: np.ndarray[float]
        self.gyro_omega: np.ndarray[float]

        # These following are to store the new matrices needed for dynamics.
        self.nB: np.ndarray[float]
        self.nS: np.ndarray[float]
        self.c_sb: np.ndarray[float]
        self.c_ss: np.ndarray[float]
        self.c_bb: np.ndarray[float]
        self.cr: np.ndarray[float]
        self.c_nb: np.ndarray[float]
        self.c_ns: np.ndarray[float]

        # Additional needed properties
        self.len_hat: np.ndarray[float]
        self.Jt_hat: np.ndarray[float]
        self.Ja_hat: np.ndarray[float]
        self.alpha: np.ndarray[float]
        self.beta: np.ndarray[float]
        self.sigma: np.ndarray[float]
        self.M: np.ndarray[float]
        self.mInv: np.ndarray[float]

        # Used for plotting
        self.targets: np.ndarray[np.ndarray[float]] = np.array([[]])

        # Creates a placeholder for the controllers.
        self.theController: Controller.Controller = Controller.Controller(self.barConn, self.nodes, self.strConn, self.system.stringConn)
        self.theAccelerometerController: src.Accelerometer.AccelerometerController = (
            src.Accelerometer.AccelerometerController.AccelerometerController(self.barConn,
                                                                              self.strConn,
                                                                              None,
                                                                              self.nodes,
                                                                              self.system.stringConn))

        # Used in the rk4 simulation
        self.currentNode: np.ndarray[np.ndarray[float]] = np.array([[]])

    def allNodesCoords(self, state: np.ndarray[np.ndarray[float]]) -> np.ndarray[np.ndarray[float]]:
        """
        Gets the node locations even from the pinned nodes of the system.  used to get the full states of the system for other functions.
        :param state: the current state of the system.
        :return: fullstate:  the state of the system after pinned nodes are added back in.
        """

        nodesToAdd: List[int] = self.system.getPinned()
        nodeArray: np.ndarray[np.ndarray[float]] = state[:int(len(state) / 2)]
        nodeArray = np.reshape(nodeArray, [int(len(state)/6), 3])

        velocityArray: np.ndarray[np.ndarray[float]] = state[int(len(state) / 2):]
        velocityArray = np.reshape(velocityArray, [int(len(state)/6), 3])

        # This portion adds in the nodes that were removed in the last iteration through the algorithm.
        for j in range(len(nodesToAdd)):
            nodeToAdd = np.array([self.system.getNode(nodesToAdd[j] - 1).getCoords()])
            nodeArray = np.insert(nodeArray, nodesToAdd[j] - 1, nodeToAdd, axis=0)
            velToAdd = np.zeros([1, 3])
            velocityArray = np.insert(velocityArray, nodesToAdd[j] - 1, velToAdd, axis=0)

        fullStateNodes: np.ndarray[np.ndarray[float]] = np.reshape(nodeArray.T, (np.size(nodeArray), 1))
        fullStateVelocities: np.ndarray[np.ndarray[float]] = np.reshape(velocityArray.T, (np.size(velocityArray), 1))
        fullState: np.ndarray[np.ndarray[float]] = np.reshape(np.append(fullStateNodes, fullStateVelocities), (np.size(fullStateNodes) + np.size(
            fullStateVelocities), 1))

        return fullState

    # TODO: annotate method below, not done before since not used.
    def BarLengthCorrectionClassK(self, n: np.ndarray[np.ndarray[float]], nd: np.ndarray[np.ndarray[float]]):
        """the function is to correct the bar length errors due to numerical simulation errors
            for ClassK structures.

            Inputs:
                received from the class

            Outputs:
                nCor: corrected nodel matrix
                nDotCor: corrected nDot matrix."""
        cR: np.ndarray[np.ndarray[float]] = 1 / 2 * np.abs(self.barConn)
        q: float = .50

        B: np.ndarray[np.ndarray[float]] = n.dot(self.barConn.T)
        Bdot: np.ndarray[np.ndarray[float]] = nd.dot(self.barConn.T)
        R: np.ndarray[np.ndarray[float]] = n.dot(cR.T)
        Rdot: np.ndarray[np.ndarray[float]] = nd.dot(cR.T)

        for j in range(0, len(B[0])):
            lenInd = self.len_hat[j, j]
            BdotRowArray = np.array([Bdot[:, j]])
            BRowArray = np.array([B[:, j]])
            a0 = float((q * lenInd) ** 2 * la.norm(Bdot[:, j]) ** 2 * ((BRowArray.dot(BdotRowArray.T)) ** 2 - la.norm(B[:, j]) ** 2 *
                                                                       la.norm(Bdot[:, j]) ** 2))
            a1 = float(2 * (q * lenInd) ** 2 * ((BRowArray.dot(BdotRowArray.T)) ** 2 - la.norm(B[:, j]) ** 2 * la.norm(Bdot[:, j]) ** 2))

            a2 = la.norm(Bdot[:, j]) ** 4 - (q * lenInd) ** 2 * la.norm(B[:, j]) ** 2
            a3 = 2 * la.norm(Bdot[:, j]) ** 2
            x = np.roots([1, a3, a2, a1, a0])
            x = x.real
            J = np.zeros(len(x))
            for i in range(0, len(x)):  # Good to here, loop 1
                arrayToInv = (x[i] * np.eye(3) + BdotRowArray.T.dot(BdotRowArray))  # insigificantly different, ran it on MATLAB with both and both worked fine.
                if la.det(arrayToInv) == 0:
                    J[i] = np.inf
                else:
                    v = q * lenInd * (la.inv(arrayToInv).dot(np.array([B[:, j]]).T))
                    p = lenInd * v - np.array([B[:, j]]).T
                    r = -v.dot(v.T).dot(BdotRowArray.T).T
                    J[i] = q * la.norm(p) ** 2 + la.norm(r) ** 2

            min = np.inf
            index = 0
            for i in range(len(J)):
                if J[i] < min:
                    min = J[i]
                    index = i
            arrayToInv = (x[index] * np.eye(3) + BdotRowArray.T.dot(BdotRowArray))
            v = q * lenInd * (la.inv(arrayToInv).dot(np.array([B[:, j]]).T))
            p = lenInd * v - np.array([B[:, j]]).T
            r = -v.dot(v.T).dot(BdotRowArray.T).T
            B[:, j] = B[:, j] + p.flatten()
            Bdot[:, j] = Bdot[:, j] + r.flatten()

        U, Sigma, V = np.linalg.svd(cR.dot(self.P))
        Sigma1 = np.diag(Sigma)
        rankSigma = np.linalg.matrix_rank(Sigma1)
        U1 = U[:, :rankSigma]
        U2 = U[:, rankSigma:]
        V1 = V[:, 0:rankSigma + 1]
        V2 = V[:, rankSigma + 1:]

        exist = (.5 * self.D - .25 * B.dot(self.barConn).dot(self.P)).dot(V2)
        if max(exist) <= 1e-5:
            R = (.5 * self.D - .25 * B.dot(self.barConn).dot(self.P)).dot(V1).dot(Sigma1 ** -1).dot(U1.T) + R.dot(U2.dot(U2.T))
            Rdot = -.25 * Bdot.dot(self.barConn).dot(self.P).dot(V1).dot(Sigma1 ** -1).dot(U1.T) + Rdot.dot(U2.dot(U2.T))

        nCorTop = np.append(B, R, axis=1)
        bottom = la.inv(np.append(self.barConn.T, cR.T, axis=1))
        nDotCorTop = np.append(Bdot, Rdot, axis=1)
        nCor = nCorTop.dot(bottom)
        nDotCor = nDotCorTop.dot(bottom)

        if la.norm(self.barConn[:, len(self.barConn[0]) - 1]) == 0:
            for k in range(0, len(self.barConn[0]) - 2 * len(B[0]) - 1):
                nCor[:, 2 * len(B[0]) + k - 1] = n[:, 2 * len(B[0]) + k - 1]
                nDotCor[:, 2 * len(B[0]) + k - 1] = nd[:, 2 * len(B[0]) + k - 1]
        return nCor, nDotCor

    def changeForceMatrix(self, currentMassLocsPercentages: List[float]) -> None:
        """
        currentMassLocsPercentages will be given through position feedback from a controller, or through a position
        simulator, like a position test sine wave.  should be as many entries as bars in the matrix. currentMassLocsPercentages
        order needs to match the order in the barconnectivity input used in the GUI.  The percentage should be relative
        to the first node in the bar connectivity inputs.
        :param currentMassLocsPercentages: The location of the current masses as a percentage of where they are along the bar.
        :return: None, sets the forces matrixes to approximate where the mass would be.
        """
        for i in range(0, len(self.system.barConn)):
            # adds the forces acting onthe nodes in question together, assumes a class 1 tensegrity structure. Otherwise, would have to assume equal masses.
            totalWeight: float = self.W_orig[1][self.system.barConn[i][0] - 1] + self.W_orig[1][self.system.barConn[i][1] - 1]

            self.W[1][self.system.barConn[i][0] - 1] = totalWeight * (1 - currentMassLocsPercentages[i])
            self.W[1][self.system.barConn[i][1] - 1] = totalWeight * currentMassLocsPercentages[i]

            self.W_orig[1][self.system.barConn[i][0] - 1] = totalWeight * (1 - currentMassLocsPercentages[i])
            self.W_orig[1][self.system.barConn[i][1] - 1] = totalWeight * currentMassLocsPercentages[i]

    def getNodeHist(self) -> np.ndarray[np.ndarray[np.ndarray[float]]]:
        """
        Returns the node history of the system. Used for graphing purposes.
        :return: the node history of the system.
        """
        return self.nodeHist

    def getPercentages(self, currentTime: float, useController: bool = False) -> List[float]:
        """
        get percentages is a function that will return the current position of the masses in terms of percentages.
        When a controller is created, it will be the responsibility of the controller to relay where the mass is
        supposed to be, and when hardware is created, it will return where the mass actually is.  Otherwise, it
        will simulate the mass moving in a sinusoidal motion.
            """
        percentages: List[float] = []
        if useController:
            # uses original controller nominally
            self.theController.updateNodes(self.currentNode.T)
            self.theAccelerometerController.updateNodes(self.currentNode.T)
            percentages = self.theController.control()
            # percentages = self.theAccelerometerController.control()
        else:
            for i in range(len(self.system.barConn)):
                percentages.append(np.sin((currentTime * self.dt) / np.pi * 5) / 2 + .5)

        return percentages

    def rk4(self, state: np.ndarray[np.ndarray[float]], tspan: np.ndarray[float], damping: float = .1, printIterations: int = 1000, updateForces: bool = False,
            updateGround: bool = False, useController: bool = False) -> None:
        """
        rk4 is the runge-kutta-4 method which is used for integrating the dynamics over time. Includes the method call to utilize the controller,
        saves some data used for other analytics.
        :param state: the initial state of the system.
        :param tspan: the number of time increments that the system is integrated over.
        :param damping: the damping matrix that adds stability to the system.
        :param printIterations: the number of algorithm iterations before printing system state to the terminal.
        :param updateForces: a boolean on whether to update forces, needed for control and testing.
        :param updateGround: update pinned nodes, or in the case of the no nodes, updating the ground.
        :param useController: a boolean to use the controller, otherwise the system will settle.
        :return: None
        """
        stateCoords: np.ndarray[np.ndarray[float]] = np.array([[]])
        forces: np.ndarray[np.ndarray[float]] = np.array([[]])

        # Sets the location on those 2 controllers.
        self.theController.makeTarget()
        print("the target is " + str(self.theController.target))

        for i in range(len(tspan)):
            if updateForces:
                # Changes the forces before the next dynamic iteration.
                nodeArray: np.ndarray[np.ndarray[float]] = state[:int(len(state) / 2)]
                self.currentNode = np.reshape(nodeArray, [int(len(state) / 6), 3])

                # The percentages passed into the function are retrieved using the percentage function.
                self.changeForceMatrix(self.getPercentages(i, useController=useController))

            # Instead to get the conditional here correct.
            stateCoordsToAppend: np.ndarray[np.ndarray[float]]

            if updateGround and 0 < i:
                state, stateCoordsToAppend = self.updateGround(state)
            else:
                stateCoordsToAppend = self.allNodesCoords(state)
                # This gets the pinned nodes from the last iteration.

            k1: np.ndarray[np.ndarray[float]] = self.dt * (self.TensegDynCKOpenFnc(state, tspan, damping))
            k1 = np.reshape(k1, (k1.size, 1), order='F')

            k2: np.ndarray[np.ndarray[float]] = self.dt * (self.TensegDynCKOpenFnc(state + k1 / 2, tspan, damping))
            k2 = np.reshape(k2, (k1.size, 1), order='F')

            k3: np.ndarray[np.ndarray[float]] = self.dt * (self.TensegDynCKOpenFnc(state + k2 / 2, tspan, damping))
            k3 = np.reshape(k3, (k1.size, 1), order='F')

            k4: np.ndarray[np.ndarray[float]] = self.dt * (self.TensegDynCKOpenFnc(state + k3, tspan, damping))
            k4 = np.reshape(k4, (k1.size, 1), order='F')

            k: np.ndarray[np.ndarray[float]] = (k1 + 2 * k2 + 2 * k3 + k4) / 6
            state = state + k

            if 0 == np.size(stateCoords):
                stateCoords = stateCoordsToAppend.T
            else:
                stateCoords = np.append(stateCoords, stateCoordsToAppend.T, axis=0)

            if 0 == np.size(forces):
                forces = np.array([self.W_orig.flatten()])
            else:
                forces = np.append(forces, np.array([self.W_orig.flatten()]), axis=0)

            if 0 == i % printIterations:
                print("forces at " + str(i * self.dt) + " seconds:")
                print(self.W[1])
                print()

        self.forcesOverTime = forces
        self.stateCoords = stateCoords
        self.targets = self.theController.targets

    def svdRobust(self) -> Tuple[np.ndarray[np.ndarray[float]], np.ndarray[np.ndarray[float]],
    np.ndarray[np.ndarray[float]], np.ndarray[np.ndarray[float]], np.ndarray[np.ndarray[float]]]:
        """
        This is used to help the system function in the case of no pinned nodes.  Allows the model to exist outside the other boundaries.
        :return U1: Left side of the svd U matrix
        :return U2 Right side of svd U matrix
        :return V1: left side of svd V matrix
        :return Sigma1: the diagonal matrix of Sigma
        :return U: the entire U matrix from the svd process.
        """
        Sigma: np.ndarray[np.ndarray[float]]
        Sigma1: np.ndarray[np.ndarray[float]]
        U: np.ndarray[np.ndarray[float]]
        V: np.ndarray[np.ndarray[float]]
        rankSigma: int

        if 1 > np.size(self.P):
            self.P = np.array([[]])
            U = np.eye(len(self.nodes[0]), len(self.nodes[0]))
            V1: np.ndarray[np.ndarray[float]] = np.array([])
            Sigma1 = np.array([])
            rankSigma = 0
        else:
            U, Sigma, V = np.linalg.svd(self.P)
            Sigma1 = np.diag(Sigma)
            rankSigma = np.linalg.matrix_rank(Sigma1)
            V1 = V[:, 0:rankSigma + 1]

        U1: np.ndarray[np.ndarray[float]] = U[:, :rankSigma]
        U2: np.ndarray[np.ndarray[float]] = U[:, rankSigma:]  # this would be true for no hidden nodes, change to add extra to sigma for virtual nodes.

        return U1, U2, V1, Sigma1, U

    def TensegConvertCmats(self) -> None:
        """
        Converts given 'simple' connectivity matricies (C_b, C_s) into the connectivity matrices used in the full
        string -to-string dynamics (C_bb, C_ns, C_nb, C_r)  Sets private variables to the calculated matricies.
        :return: None
        """
        n: int = len(self.nodes[0])
        beta: int = len(self.barConn)

        # Check if there is a string point mass nodes.
        sigma: int = n - 2 * beta

        self.nB = self.nodes[:, 0:2 * beta]
        self.nS = self.nodes[:, 2 * beta + 1:]

        # Convert to separate matrices for dynamics (also calc of consts M, Minv)
        self.c_sb = self.strConn[:, 0:2 * beta]
        self.c_ss = self.strConn[:, 2 * beta + 1:]
        self.c_bb = self.barConn[:, 0: 2 * beta]
        self.cr = 1 / 2 * np.abs(self.barConn[:, 0:2 * beta])
        self.c_nb = np.append(np.eye(2 * beta), np.zeros([2 * beta, sigma]), axis=1)
        self.c_ns = np.append(np.zeros([sigma, 2 * beta]), np.eye(sigma), axis=1)

    def TensegDefaults(self, nodeNum, beta, alpha, sigma) -> None:
        """
        Sets the default inputs based on beta, alpha, nodenum, and sigma.
        :param nodeNum: the number of nodes in the system.
        :param beta: A system property?
        :param alpha: A system property?
        :param sigma: A sytem property?
        :return: None
        """

        # structure definitions
        self.m = np.ones([1, beta])
        self.ms = 0.1 * np.ones([1, sigma])
        self.mgyro = np.zeros([1, beta])
        self.gyro_r = np.zeros([1, beta])
        self.gyro_h = np.zeros([1, beta])

        # Initial conditions
        self.Nd0 = np.zeros([3, nodeNum])
        self.wDef = np.zeros([3, nodeNum])
        self.k = 100 * np.ones([1, alpha])
        self.c = np.zeros([1, alpha])
        self.gyro_omega = np.zeros([1, beta])

    def TensegDynCKOpenFnc(self, state, tspan, damping=.1):
        """
        This function is used in computing the dynamic behavior of an open-loop class k tensegrity structure.
        Essentially, xdot = [nd, ndd] is computed from x = [n, nd], and t is included for use with a fixed
        time step rk4 integrator.  Sctructure-specifiic definitions are provided through private variables, and
        functionality is included that allows for the logging of internally computed variables throughout a
        simulation, such as bar length and string force densities.

        :param state: the current state of the system.
        :param tspan: the timespan the simulation occurs over.
        :param damping: the amount of damping felt by the system.
        :return: ndot and nddot values based of current state.
        """
        ETA1: np.ndarray[np.ndarray[float]]
        U1: np.ndarray[np.ndarray[float]]
        U2: np.ndarray[np.ndarray[float]]
        V1: np.ndarray[np.ndarray[float]]
        Sigma1: np.ndarray[np.ndarray[float]]
        U: np.ndarray[np.ndarray[float]]
        U1, U2, V1, Sigma1, U = self.svdRobust()

        if 0 == len(V1):
            ETA1 = np.array([])
        else:
            ETA1 = self.D.dot(V1).dot(np.linalg.inv(Sigma1))

        xeta2: np.ndarray[np.ndarray[float]] = state[0:int(np.size(state) / 2)]  # position state values, compound for big problems.
        xeta2d: np.ndarray[np.ndarray[float]] = state[int(np.size(state) / 2):]
        ETA2: np.ndarray[np.ndarray[float]] = np.reshape(xeta2, (3, int(np.size(xeta2) / 3)), order='F')
        eta2d: np.ndarray[np.ndarray[float]] = np.reshape(xeta2d, (3, int(np.size(xeta2d) / 3)), order='F')

        n: np.ndarray[np.ndarray[float]]
        nd: np.ndarray[np.ndarray[float]]

        if 1 > np.size(ETA1):
            n = ETA2.dot(U.T)
            nd = eta2d.dot(U.T)
        else:
            n = np.append(ETA1, ETA2, axis=1).dot(U.T)
            nd = np.append(np.zeros([len(ETA1), len(ETA1[0])]), eta2d, axis=1).dot(U.T)

        if 0 < self.nodeHist.size:
            if 4 == self.counter:
                self.nodeHist = np.append(self.nodeHist, np.array([n]), axis=0)
                self.counter = 0
        else:
            self.nodeHist = np.array([n])

        self.counter += 1

        ETA2 = n.dot(U2)

        # Compute bar lengths - needs to be done at each time step so numerical errors are at least self-consistent
        B: np.ndarray[np.ndarray[float]]

        if 0 < len(self.barConn):
            B = n.dot(self.barConn.T)
        else:
            B = np.array([])

        currentLenHat: np.ndarray[np.ndarray[float]] = np.sqrt(np.diag(np.diag(B.T.dot(B))))

        # Get current external forces, assumes that W doesn't change/ is initialized correctly.
        W: np.ndarray[np.ndarray[float]] = self.W

        # Compute gamma
        s: np.ndarray[np.ndarray[float]] = n.dot(self.strConn.T)
        sd: np.ndarray[np.ndarray[float]] = nd.dot(self.strConn.T)

        # Initialize diagonal gamma matrix
        gammaHat: np.ndarray[np.ndarray[float]] = np.zeros([len(self.strConn), len(self.strConn)])

        # Get current resting string lengths, assume s_0 correctly initialized.
        s0Hat: np.ndarray[np.ndarray[float]] = np.zeros([len(self.s0), len(self.s0)])
        np.fill_diagonal(s0Hat, self.s0.flatten())

        # Go through each string and figure out its force density
        # The damping term might be alterable to make it so there is only damping on the strings?
        for j in range(0, len(self.strConn)):
            if np.linalg.norm(s[:, j]) > s0Hat[j, j]:
                gammaHat[j, j] = self.k[0, j] * (1 - s0Hat[j, j] / la.norm(s[:, j]))
                dampingTerm: float = self.c[0, j] * (s[:, j].T.dot(sd[:, j])) / la.norm(s[:, j]) ** 2
                gammaHat[j, j] = gammaHat[j, j] + dampingTerm

            if 0 > gammaHat[j, j]:
                gammaHat[j, j] = 0

        # CLASS K dynamics
        # Compute B_dot if the structure has bars
        bD: np.ndarray[np.ndarray[float]]

        if 0 < np.size(self.barConn):
            bD = nd.dot(self.barConn.T)
        else:
            bD = np.array([])

        gyroOmegaHat: np.ndarray[np.ndarray[float]] = np.diag(self.gyro_omega.flatten())  # good to here

        # Make Bcross MAtrix (for gyro dynamics)
        bCross: np.ndarray[np.ndarray[float]] = np.zeros([3, 3 * self.beta])
        for ii in range(self.beta):
            bCross[:, ii * 3: ii * 3 + 3] = CommonMatrixOperations.skew(B[:, ii])

        # Make bd_har, Q matrices (for gyro dynamics)
        bdHat: np.ndarray[np.ndarray[float]] = np.zeros([3 * self.beta, self.beta])
        for ii in range(self.beta):
            bdHat[ii * 3: ii * 3 + 3, ii] = bD[:, ii]

        Q: np.ndarray[np.ndarray[float]] = bCross.dot(bdHat)

        # ANALYTICAL METHOD - FULL ORDER
        mHat = np.diag(self.m.flatten())

        currentLenHat2d: np.ndarray[np.ndarray[float]]
        qDotAppen: np.ndarray[np.ndarray[float]]
        wsGryoCurrent: np.ndarray[np.ndarray[float]]

        if 0 < np.size(self.P):
            bc: np.ndarray[np.ndarray[float]] = self.P.T.dot(self.barConn.T)
            bd: np.ndarray[np.ndarray[float]] = self.barConn.dot(self.mInv).dot(self.P)
            be: np.ndarray[np.ndarray[float]] = self.P.T.dot(self.mInv).dot(self.P)
            e: np.ndarray[np.ndarray[float]] = np.eye(3)
            currentLenHat2d = currentLenHat ** (-2)
            currentLenHat2d = np.nan_to_num(currentLenHat2d, copy=True, posinf=0)

            ba: np.ndarray[np.ndarray[float]] = (-s.dot(gammaHat).dot(self.strConn).dot(self.mInv).dot(self.P) +
                                                 B.dot(np.diag(np.diag(.5 * currentLenHat2d.dot(B.T).dot((s.dot(gammaHat).dot(self.strConn) - W))
                                                                       .dot(self.barConn.T) - 1 / 12 * currentLenHat2d.dot(mHat).dot((bD.T.dot(bD))))))
                                                 .dot(self.barConn).dot(self.mInv).dot(self.P) + W.dot(self.mInv).dot(self.P))

            lagMat: np.ndarray[np.ndarray[float]] = np.array([[[]]])

            for j in range(len(self.barConn)):
                if j == 0:
                    lagMat = 1 / (2 * currentLenHat[j, j] ** 2) * np.kron(np.array([bc[:, j]]), np.kron(np.array([B[:, j]]).T, (
                        np.array([B[:, j]]).T.dot(np.array([bd[j, :]]))).T))
                else:
                    lagMat = lagMat + 1 / (2 * currentLenHat[j, j] ** 2) * np.kron(np.array([bc[:, j]]), np.kron(np.array([B[:, j]]).T, (
                        np.array([B[:, j]]).T.dot(np.array([bd[j, :]]))).T))

            kronBe0: np.ndarray[np.ndarray[float]] = np.kron(be, e[0, :])
            kronBe1: np.ndarray[np.ndarray[float]] = np.kron(be, e[1, :])
            kronBe2: np.ndarray[np.ndarray[float]] = np.kron(be, e[2, :])
            kronBe: np.ndarray[np.ndarray[float]] = np.append(kronBe0, kronBe1, axis=0)
            kronBe = np.append(kronBe, kronBe2, axis=0)
            lagMat: np.ndarray[np.ndarray[float]] = lagMat - kronBe

            omegaLegrangeVec: np.ndarray[np.ndarray[float]] = la.inv(lagMat).dot(np.array([ba.flatten()]).T)
            omegaLegrange: np.ndarray[np.ndarray[float]] = np.reshape(omegaLegrangeVec, (3, int(omegaLegrangeVec.size / 3)), 'F')

            # Using lagrangian multipliers, solve for Ndd from the dynamic equations
            qDotAppen = np.append(Q.dot(self.Ja_hat).dot(gyroOmegaHat).dot(currentLenHat2d).dot(self.c_bb), np.zeros([3, self.sigma]), axis=1)
            wsGryoCurrent = W + qDotAppen + omegaLegrange.dot(self.P.T)
        else:
            currentLenHat2d = currentLenHat ** (-2)
            currentLenHat2d = np.nan_to_num(currentLenHat2d, copy=True, posinf=0)
            qDotAppen = np.append(Q.dot(self.Ja_hat).dot(gyroOmegaHat).dot(currentLenHat2d).dot(self.c_bb),
                                  np.zeros([3, self.sigma]), axis=1)
            wsGryoCurrent = W + qDotAppen

        F: np.ndarray[np.ndarray[float]] = wsGryoCurrent - n.dot(self.strConn.T).dot(gammaHat).dot(self.strConn)

        lambdaHat: np.ndarray[np.ndarray[float]]

        # Currently only lambdahat is sig diff.
        if 0 < len(self.barConn):
            lambdaHat = -self.Jt_hat.dot(currentLenHat2d).dot(np.diag(np.diag(bD.T.dot(bD)))) - 1 / 2 * currentLenHat2d.dot(
                np.diag(np.diag(B.T.dot(F).dot(self.barConn.T))))
        else:
            lambdaHat = np.array([[]])

        K: np.ndarray[np.ndarray[float]] = np.append(self.strConn.T.dot(gammaHat).dot(self.c_sb) - self.c_nb.T.dot(self.c_bb.T).dot(lambdaHat).dot(self.c_bb),
                                                     self.strConn.T.dot(gammaHat).dot(self.c_ss), axis=1)
        mBar: np.ndarray[np.ndarray[float]] = U2.T.dot(self.M).dot(U2)
        kBar: np.ndarray[np.ndarray[float]] = U2.T.dot(K).dot(U2)
        wBar: np.ndarray[np.ndarray[float]] = (W + qDotAppen).dot(U2) - ETA1.dot(U1.T).dot(K).dot(U2)

        ETA2ddot: np.ndarray[np.ndarray[float]] = (wBar - ETA2.dot(kBar)).dot(la.inv(mBar))
        xeta2ddot: np.ndarray[np.ndarray[float]] = np.array([ETA2ddot.flatten('F')]).T - xeta2d * damping

        xd: np.ndarray[np.ndarray[float]] = np.append(xeta2d, xeta2ddot, axis=0)
        return xd  # check to make sure that the test dot and the normal dot are actually different.

    def TensegSimClassKOpen(self, damping: float = .1, updateForces: bool = False, updateGround: bool = False, useController: bool = False) -> None:
        """
        This function performs simulation of a given CLASS K, OPEN LOOP tensegrity simulation task.
        Specification of the simulation task is done with the 'sim_task' input data structure,
        described below.  Outputs include a data structure containing node position time histories,
        and a data structure containing relevant internal values used in performing the simulation.
        :param damping: The damping of the system's velocity
        :param updateForces: whether to update the forces on the system - makes the system a dynamic environment.
        :param updateGround: whether to update which nodes are on the ground.
        :param useController: whether to use a controller.
        :return: None.
        """

        # Generate full sim task data structure from inputs
        self.TensegStructGen()

        tspan: np.ndarray[float] = np.arange(0, self.tf, self.dt)
        U1: np.ndarray[np.ndarray[float]]
        U2: np.ndarray[np.ndarray[float]]
        V1: np.ndarray[np.ndarray[float]]
        Sigma1: np.ndarray[np.ndarray[float]]

        # For reduced order
        if 0 == len(self.P):
            self.P = np.array([[]])

        U1, U2, V1, Sigma1, _ = self.svdRobust()

        ETA20: np.ndarray[np.ndarray[float]] = self.nodes.dot(U2)
        ETA2d0: np.ndarray[np.ndarray[float]] = self.Nd0.dot(U2)
        XETA20: np.ndarray[np.ndarray[float]] = np.reshape(ETA20.T, (np.size(ETA20), 1))
        XETA2d0: np.ndarray[np.ndarray[float]] = np.reshape(ETA2d0.T, (np.size(ETA2d0), 1))

        # X0 is used to describe the initial state of the system.
        X0: np.ndarray[np.ndarray[float]] = np.reshape(np.append(XETA20, XETA2d0), (np.size(ETA20) + np.size(ETA2d0), 1))

        # Use all the step-up data, send to an integration program.  First, need the tenseg dynamics file.
        # I may need to alter this so that I can get the needed state information for the animations.
        # next up is an RK4 algorithm.  each iteration through the dynamic function will need to log the state in private variables.
        self.rk4(X0, tspan, damping=damping, updateForces=updateForces, updateGround=updateGround, useController=useController)

    def TensegStructGen(self):
        """
        This code fully populates all fields of a tensegrity simulation task data structure given an initial
        data structure containing the required fields. Default values are loaded and added as fields as necessary.
        :return: None
        """

        # Get basic structure values
        nodeNum: int = len(self.nodes[0])
        beta: int = len(self.barConn)
        alpha: int = len(self.strConn)

        # Check if we have string point mass nodes
        sigma: int = nodeNum - 2 * beta

        # load all default input values
        self.TensegDefaults(nodeNum, beta, alpha, sigma)

        # don't need the to set the struct stuff, all the info is contained in the class.

        if 0 != np.size(self.barConn):
            checkVel: np.ndarray[np.ndarray[float]] = np.diag((self.nodes.dot(self.barConn.T)).T.dot(self.Nd0.dot(self.barConn.T)))

            if 1e-5 <= np.linalg.norm(checkVel):
                print("incorrect Initial Velocities")
                return

        # Continue to ensure structure properly initialized, makes new connectivity matrices.  To be saved to private vars.
        self.TensegConvertCmats()

        # If only one point mass value is specified, assume all point masses have that value.
        if 1 == len(self.ms):
            self.m = self.m[0] * np.ones([1, beta])

        # Check if structure has bar members
        length: np.ndarray[np.ndarray[float]]
        if beta:
            self.len_hat = np.sqrt(np.diag(np.diag(self.nodes.dot(self.barConn.T).T.dot(self.nodes.dot(self.barConn.T)))))  # bar lengths diagonal matrix
            length = np.array([np.diag(self.len_hat)])
        else:
            self.len_hat = np.array([[]])
            length = np.array([[]])

        # Moments of inertia - already initialized since all in this class.
        k_val: float = (1.0 / 12 * np.power(length, 2)) * (3 * np.power(self.gyro_r, 2) + np.power(self.gyro_h, 2))
        mb: np.ndarray[np.ndarray[float]] = self.m
        Jt: np.ndarray[np.ndarray[float]] = mb / 12 + k_val * self.mgyro
        self.Jt_hat = np.diag(Jt.flatten())

        Ja: np.ndarray[np.ndarray[float]] = 1 / 2 * self.mgyro / length * np.power(self.gyro_r, 2)
        self.Ja_hat = np.diag(Ja.flatten())

        # Initialize constants - basically already done, probably will need to add the alpha, beta, sigmas to the class def.
        self.alpha = alpha
        self.beta = beta
        self.sigma = sigma

        mTotHat: np.ndarray[np.ndarray[float]] = np.diag(self.m + self.mgyro)
        msHat: np.ndarray[np.ndarray[float]] = np.diag(self.ms)
        JtHat: np.ndarray[np.ndarray[float]] = self.Jt_hat

        self.M = np.append(self.c_nb.T.dot((self.c_bb.T.dot(JtHat)).dot(self.c_bb) + (self.cr.T * mTotHat).dot(self.cr)), self.c_ns.T * msHat, axis=1)
        self.mInv = np.linalg.inv(self.M)

        if 1 == len(self.k):
            self.k = self.k * np.ones([1, alpha])

        if 1 == len(self.c):
            self.c = self.c * np.ones([1, alpha])

    def updateGround(self, state: np.ndarray[np.ndarray[float]]) -> Tuple[np.ndarray[np.ndarray[float]], np.ndarray[np.ndarray[float]]]:
        """
        A function used to update ground nodes, especially during the model rolling.
        :param state: the current state of the system.
        :return:
        """
        xForceConstant: float = 100
        yForceConstant: float = 10000
        zForceConstant: float = 100

        # Initializes node states with the infor that I have
        nodeArray: np.ndarray[np.ndarray[float]] = state[:int(len(state) / 2)]
        nodeArray = np.reshape(nodeArray, [int(len(state) / 6), 3])
        velArray: np.ndarray[np.ndarray[float]] = state[int(len(state) / 2):]
        velArray = np.reshape(velArray, [int(len(state) / 6), 3])

        # this loop updates the pinned array, uses conditionals where the position = 0, and the velocity < 0 to make the node a pinned node.
        # may need to reset positions and velocities to zero in this loop.
        for j in range(0, int(len(nodeArray))):
            if 0 >= nodeArray[j][1]:
                self.W[0][j] = xForceConstant * -velArray[j][0]
                self.W[1][j] = yForceConstant * np.abs(nodeArray[j][1])
                self.W[2][j] = zForceConstant * -velArray[j][2]
            else:
                self.W[0][j] = self.W_orig[0][j]
                self.W[1][j] = self.W_orig[1][j]
                self.W[2][j] = self.W_orig[2][j]

        return state, self.allNodesCoords(state)
