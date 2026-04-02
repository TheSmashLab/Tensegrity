import cv2
import matplotlib.pyplot as plt
from mpl_toolkits import mplot3d
import numpy as np
import os
import pandas as pd
from typing import List

from src.TensegritySystem import Nodes as N

ROOT_PATH: str = os.getcwd()


def animateMotion(axisLength: float, barConn: np.ndarray[np.ndarray[int]], dt: float, nodeHist: np.ndarray[np.ndarray[np.ndarray[float]]],
                  stringConn: np.ndarray[np.ndarray[int]], tf: float, videoName: str = "default.mp4v") -> None:
    """
    Animates the motion of the system by graphing the system at various points in time and stitching those graphs together into a video.
    :param axisLength: Length of the axis shown in the video
    :param barConn:  The barConnection matrix.
    :param dt: the timestep used in simulation.
    :param nodeHist: The node history array.
    :param stringConn: The string connection matrix.
    :param tf: The final time of the simulation.
    :param videoName: the name to save the video file to.
    :return: None
    """
    # parameters needed to set up graph and points to plot.
    x: List[float] = []
    y: List[float] = []
    z: List[float] = []

    image_folder: str = os.path.join(ROOT_PATH, 'placeholderFolders/pngFolder')

    time: np.ndarray[float] = np.arange(0, tf, dt)
    # This code determines what coordinates are connected by the strings.
    for t in time:
        t: int = int(t / dt)

        if 0 == t % int(1 / dt / 20):
            fig: plt.figure = plt.figure()
            ax: mplot3d.Axes3D = fig.add_subplot(projection='3d')

            # Gets the coordinate points out of the given nodes.
            newNodeArray: List[N.Node] = []
            for i in range(len(nodeHist[t].T)):
                theNode = N.Node(nodeHist[t].T.item(i, 0), nodeHist[t].T.item(i, 1), nodeHist[t].T.item(i, 2))
                newNodeArray.append(theNode)

            # This code plots a scatterplot of the nodes, or in other words, shows the nodes on the graph without lines.
            ax.scatter3D(x, z, y, c=y, cmap='cividis')
            ax.set_xlim(-axisLength, axisLength)
            ax.set_ylim(-axisLength, axisLength)
            ax.set_zlim(-axisLength, axisLength)
            ax.set_xlabel('x')
            ax.set_ylabel('z')
            ax.set_zlabel('y')

            for i in range(0, len(newNodeArray)):
                nodeCoords: List[float] = newNodeArray[i].getCoords()
                x.append(nodeCoords[0])
                z.append(nodeCoords[1])
                y.append(nodeCoords[2])

                plt.plot(nodeCoords[0], nodeCoords[2], nodeCoords[1], '-go')
                ax.text(nodeCoords[0], nodeCoords[2], nodeCoords[1], str(i + 1))

            for i in range(0, np.size(stringConn, 0)):
                x: List[float] = []
                y: List[float] = []
                z: List[float] = []

                initialCoords: List[float] = newNodeArray[int(stringConn[i, 0] - 1)].getCoords()
                finalCoords: List[float] = newNodeArray[int(stringConn[i, 1] - 1)].getCoords()

                x.append(initialCoords[0])
                x.append(finalCoords[0])
                y.append(initialCoords[1])
                y.append(finalCoords[1])
                z.append(initialCoords[2])
                z.append(finalCoords[2])
                plt.plot(x, z, y, 'red')

            # This code determines what coordinates are connected by the bars.
            for i in range(0, np.size(barConn, 0)):
                x: List[float] = []
                y: List[float] = []
                z: List[float] = []

                initialCoords: List[float] = newNodeArray[int(barConn[i, 0] - 1)].getCoords()
                finalCoords: List[float] = newNodeArray[int(barConn[i, 1] - 1)].getCoords()

                x.append(initialCoords[0])
                x.append(finalCoords[0])
                y.append(initialCoords[1])
                y.append(finalCoords[1])
                z.append(initialCoords[2])
                z.append(finalCoords[2])
                plt.plot(x, z, y, 'blue', linewidth=3)

            tString: str = str(t)
            tLength: int = len(str(int(time[-1] / dt)))

            if len(tString) < tLength:
                strFront: str = ''

                for j in range(len(tString), tLength):
                    strFront = strFront + '0'
                tString = strFront + tString

            plt.savefig(os.path.join(image_folder, ('myplot' + tString + ".png")), dpi=75)
            plt.close()

    images: List[str] = sorted([img for img in os.listdir(image_folder) if img.endswith(".png")])
    frame: np.ndarray[np.ndarray[np.ndarray[float]]] = cv2.imread(os.path.join(image_folder, images[0]))

    height: float
    width: float
    layers: float
    height, width, layers = frame.shape

    videoPath: str = os.path.join(ROOT_PATH, 'placeholderFolders/videoFolder/')
    fourcc: cv2.VideoWriter_fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    video: cv2.VideoWriter = cv2.VideoWriter(videoPath + videoName, fourcc, 20, (width, height))

    for image in images:
        video.write(cv2.imread(os.path.join(image_folder, image)))

    video.release()
    cv2.destroyAllWindows()

    # using listdir() method to list the files of the folder
    test: List[str] = os.listdir(image_folder)

    # taking a loop to remove all the images using ".png" extension to remove only png images using os.remove() method to remove the files
    for images in test:
        if images.endswith(".png"):
            os.remove(os.path.join(image_folder, images))


def sendInfoToCSVFile(forcesOverTime: np.ndarray[np.ndarray[float]], name: str, stateCoords: np.ndarray[np.ndarray[float]]) -> None:
    """
    Sends states to a CSV file for future ML training.
    :param forcesOverTime: The forces that were on the system over the duration of simulation.
    :param name: the name for the csv file.
    :param stateCoords:
    :return: None
    """

    allInfo = np.append(stateCoords.T, forcesOverTime.T, axis=0)

    df = pd.DataFrame(allInfo.T)
    df.to_csv(ROOT_PATH + '/placeholderFolders/csvsForLearning/' + name)
