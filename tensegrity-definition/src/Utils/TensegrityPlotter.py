import matplotlib.pyplot as plt
from mpl_toolkits import mplot3d
import numpy as np
from typing import List

from src.TensegritySystem import Nodes
from src.Utils import CalcSystemProperties


# This function does a basic plot of the initial topology of the tensegrity system.
def basicPlot(nodes: np.ndarray[Nodes], connectivityMatrixString: np.ndarray[np.ndarray[float]], connectivityMatrixBars: np.ndarray[np.ndarray[float]]
= np.array([]), axisLength: int = 3) -> None:
    """
    Creates a basic plot of what the tensegrity system looks like.  Uses the string and the bar matrices and creates connections between all the various nodes.
    :param nodes: the nodes that are part of the system.  Contains the coordinates for those nodes, which are used for plotting.
    :param connectivityMatrixString: which nodes are connected by strings.
    :param connectivityMatrixBars: which nodes are connected by bars.
    :param axisLength: the length of the graphing axis.
    :return: None, creates a visual representation of the system.
    """
    # Parameters needed to set up graph and points to plot.
    x: List[float] = []
    y: List[float] = []
    z: List[float] = []
    fig: plt.Figure = plt.figure()
    ax: mplot3d.Axes3D = fig.add_subplot(projection='3d')

    # Gets the coordinate points out of the given nodes.
    for i in range(0, len(nodes)):
        nodeCoords: List[float] = nodes.item(i).getCoords()
        plt.plot(nodeCoords[0], nodeCoords[2], nodeCoords[1], '-go')
        ax.text(nodeCoords[0], nodeCoords[2], nodeCoords[1], str(i + 1))

    # This code plots a scatterplot of the nodes, or in other words, shows the nodes on the graph without lines.
    ax.scatter3D(x, y, z, c=z, cmap='cividis')
    ax.set_xlabel('z')
    ax.set_ylabel('x')
    ax.set_zlabel('y')
    ax.set_xlim(-axisLength, axisLength)
    ax.set_ylim(-axisLength, axisLength)
    ax.set_zlim(-axisLength * 2, 0)

    # This code determines what coordinates are connected by the strings.
    for i in range(0, np.size(connectivityMatrixString, 0)):
        x: List[float] = []
        y: List[float] = []
        z: List[float] = []
        initialCoords: List[float] = nodes.item(connectivityMatrixString[i, 0] - 1).getCoords()
        finalCoords: List[float] = nodes.item(connectivityMatrixString[i, 1] - 1).getCoords()
        x.append(initialCoords[0])
        x.append(finalCoords[0])
        y.append(initialCoords[1])
        y.append(finalCoords[1])
        z.append(initialCoords[2])
        z.append(finalCoords[2])
        plt.plot(x, z, y, 'red')

    # This code determines what coordinates are connected by the bars.
    for i in range(0, np.size(connectivityMatrixBars, 0)):
        x: List[float] = []
        y: List[float] = []
        z: List[float] = []

        initialCoords: List[float] = nodes.item(connectivityMatrixBars[i, 0] - 1).getCoords()
        finalCoords: List[float] = nodes.item(connectivityMatrixBars[i, 1] - 1).getCoords()

        x.append(initialCoords[0])
        x.append(finalCoords[0])
        y.append(initialCoords[1])
        y.append(finalCoords[1])
        z.append(initialCoords[2])
        z.append(finalCoords[2])
        plt.plot(x, z, y, 'blue', linewidth=3)

    plt.show()


def GraphStates(stateCoords: np.ndarray[np.ndarray[float]], tf: float, dt: float) -> None:
    """
    Graphically displays the states of the system over time.  not used much.
    :param stateCoords: a list of all the stateCoords of the system recorded over the length of the simulation.
    :param tf: The final time of the simulation.
    :param dt: The time step of the simulation.
    :return: None
    """
    time = np.arange(0, tf, dt)
    fig = plt.figure(1)
    fig.suptitle('Dynamics of the generalized coordinates')
    for i in range(0, len(stateCoords)):
        if i % 3 == 0:
            ax = fig.add_subplot(int(len(stateCoords) / 3), 1, i / 3 + 1)
            ax.set_title("Node " + str(i / 3 + 1))
            ax.plot(time, stateCoords[i], label='q1')
            ax.plot(time, stateCoords[i + 1], label='q2')
            ax.plot(time, stateCoords[i + 2], label='q3')
            ax.set_xlabel('time (s)')
            ax.set_ylabel('node positions')
            plt.legend()

    fig.tight_layout(pad=1.5)
    plt.show()


def plotPath(nodeHist: np.ndarray[np.ndarray[np.ndarray[float]]], plotName: str, targets: np.ndarray[np.ndarray[float]], axisLimit: float = 5) -> None:
    """
    Plots the path of the center of mass of the system after it does its route.
    :param nodeHist: The history of all the points each node was at
    :param plotName: The name of the plot will be saved to.
    :param targets: The targets that the robot moved to.
    :param axisLimit: How large the axes are on the plot.
    :return: None
    """
    xCOMs: np.ndarray[np.ndarray[np.ndarray[float]]] = np.zeros(len(nodeHist))
    zCOMs: np.ndarray[np.ndarray[np.ndarray[float]]] = np.zeros(len(nodeHist))

    for i in range(len(nodeHist)):
        COM: np.ndarray[np.ndarray[float]] = CalcSystemProperties.findCOM(nodeHist[i].T)
        xCOMs[i]: np.ndarray[float] = COM[0]
        zCOMs[i]: np.ndarray[float] = COM[2]

    fig: plt.Figure
    ax: plt.Axes
    fig, ax = plt.subplots()

    ax.set_xlim(-axisLimit, axisLimit)
    ax.set_ylim(-axisLimit, axisLimit)

    plt.title("Path Transversed")
    plt.xlabel("x axis of xz plane")
    plt.ylabel("z axis of xz plane")
    ax.plot(xCOMs, zCOMs, label="model path")
    ax.plot(CalcSystemProperties.findCOM(nodeHist[0].T)[0], CalcSystemProperties.findCOM(nodeHist[0].T)[2], '-yo', label="model start point")

    if 0 < len(targets):
        for i in range(len(targets.T[0])):
            ax.plot(np.array(targets).T[0][i], np.array(targets).T[1][i], '-ro', label='target points')

    plt.legend(loc='lower right')
    plt.show()

def projectionPlot(nodes: np.ndarray[Nodes.Node], nodesOfInterest: List[int], title:str, trianglePoints=None,show_plot=True) -> List[float]:
    """
    TODO: This is not a general method, only words for icosaherdons made in a specific way it appears. To use for other systems, need to modify.
    Will plot the 2D projection of the system onto the xz plane.  will connect triangular base points and project the rest of the nodes onto the plane.
    This code will assume that the base of the triangle is on the ground.
    :param nodes: The nodes that make up the system.
    :return: None, displays a graph of the base.
    """


    if trianglePoints is None:
        trianglePoints: List[int] = []
        for i in range(len(nodes)):
            if nodes.item(i).getCoords()[1] < .2:
                trianglePoints.append(i)

    x: List[float] = []
    z: List[float] = []

    for i in range(len(nodes)):
        initialCoords = nodes.item(i).getCoords()
        x.append(initialCoords[0])
        z.append(initialCoords[2])

    ax: plt.Axes
    fig: plt.Figure
    fig, ax = plt.subplots()
    ax.set_xlim(-2, 2)
    ax.set_ylim(-2.5, 2.5)

    for i in range(len(nodes)):
        if 0 == i:
            plt.plot(x[i], z[i], 'bo', color='blue', label='system xz projection')
        else:
            plt.plot(x[i], z[i], 'bo', color='blue')

        plt.text(x[i] * (1 + 0.01), z[i] * (1 + 0.01), i + 1, fontsize=12)

    triangleNodes: np.ndarray[np.ndarray[float]] = np.array([[], [], []])

    for i in range(len(trianglePoints)):
        x: List[float] = list([])
        z: List[float] = list([])
        initialCoords: List[float] = nodes.item(trianglePoints[-1 + i]).getCoords()
        finalCoords: List[float] = nodes.item(trianglePoints[i]).getCoords()
        triangleNodes = np.append(triangleNodes, np.array([finalCoords]).T, axis=1)
        x.append(initialCoords[0])
        x.append(finalCoords[0])
        z.append(initialCoords[2])
        z.append(finalCoords[2])
        line, = plt.plot(x, z, 'red')

        if 0 == i:
            line.set_label('triangle base')

    nodeRep3d: np.ndarray[np.ndarray[float]] = CalcSystemProperties.getPositionsFromNodeArray(nodeArray=nodes)
    COMTriangle: np.ndarray[np.ndarray[float]] = CalcSystemProperties.findCOM(triangleNodes.T)
    COMSystem: np.ndarray[np.ndarray[float]] = CalcSystemProperties.findCOM(nodeRep3d)
    COMSystemSimple = list([COMSystem.item(0), COMSystem.item(2)])

    plt.plot(COMTriangle[0], COMTriangle[2], 'purple', marker='o', markersize=6, label='triangle COM')
    plt.plot(COMSystem[0], COMSystem[2], 'gold', marker='o', markersize=2.5, label='system COM with moment arm')

    # point1 = [triangleNodes[0, 0], triangleNodes[2, 0]]  # for other tests
    # point2 = [triangleNodes[0, 1], triangleNodes[2, 1]]  # for other tests

    point1: List[float] = [triangleNodes.item(0, 1), triangleNodes.item(2, 1)]  # for parallel best case, other case
    point2: List[float] = [triangleNodes.item(0, 2), triangleNodes.item(2, 2)]  # for parallel best case, other case

    intersectPoint: List[float]
    distanceCOM: float
    intersectPoint, distanceCOM = CalcSystemProperties.findPerpPoint(point1, point2, COMSystemSimple)

    xs: List[float] = []
    zs: List[float] = []
    xs.append(COMSystemSimple[0])
    xs.append(intersectPoint[0])
    zs.append(COMSystemSimple[1])
    zs.append(intersectPoint[1])

    plt.plot(xs, zs, 'gold')
    # print(float(distanceCOM))

    # This is for the parallel case other case version
    leverageDistance: float = 0

    for i in range(len(nodesOfInterest)):
        intersectPoint: List[float]
        distance: float
        otherPoint: List[float] = [nodes.item(nodesOfInterest[i] - 1).getCoords()[0], nodes.item(nodesOfInterest[i] - 1).getCoords()[2]]
        intersectPoint, distance = CalcSystemProperties.findPerpPoint(point1, point2, otherPoint)

        if intersectPoint[1] > otherPoint[1]:
            leverageDistance = leverageDistance + distance
        else:
            leverageDistance = leverageDistance - distance

        xs: List[float] = []
        zs: List[float] = []
        xs.append(otherPoint[0])
        xs.append(intersectPoint[0])
        zs.append(otherPoint[1])
        zs.append(intersectPoint[1])

        if 0 == i:
            plt.plot(xs, zs, 'grey', label='moment arms from masses')
        else:
            plt.plot(xs, zs, 'grey')

    barConnections: np.ndarray[np.ndarray[int]] = np.array([[1, 2], [3, 4], [5, 7], [6, 8], [9, 10], [11, 12]])

    for i in range(len(barConnections)):
        barPoint1: List[float] = nodes.item(barConnections[i, 0] - 1).getCoords()
        barPoint2: List[float] = nodes.item(barConnections[i, 1] - 1).getCoords()
        xs: List[float] = []
        zs: List[float] = []
        xs.append(barPoint1[0])
        xs.append(barPoint2[0])
        zs.append(barPoint1[2])
        zs.append(barPoint2[2])

        if 0 == i:
            plt.plot(xs, zs, 'green', linewidth=.25, label='bar connections')
        else:
            plt.plot(xs, zs, 'green', linewidth=.25)

    ax.set_xlabel("x axis(m)")
    ax.set_ylabel("z-axis(m)")

    plt.title(title)
    box = ax.get_position()
    ax.set_position([box.x0, box.y0 + box.height * 0.1,
                     box.width, box.height * 0.9])

    # Put a legend to the right of the current axis
    ax.legend(loc='upper center', bbox_to_anchor=(0.5, -0.05),
              fancybox=True, shadow=True, ncol=2)
    if show_plot:
        plt.show()
    else:
        plt.close()
    print(-leverageDistance, distanceCOM)
    return [-leverageDistance, distanceCOM / -leverageDistance]
