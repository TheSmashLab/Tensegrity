import argparse
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt


def plotData(dataFile, dataTrueFile=None):
    """
    Plot the accelerometer data and covariance ellipses.

    Parameters:
    dataFile (str): Path to the experimentally collected data file.
    dataTrueFile (str, optional): Path to the ground truth data file. Defaults to None.

    Returns:
    None
    """
    # Read in CSV file
    # Expects data with columns: 'x', 'y', 'cov_xx', cov_xy', 'cov_yx', 'cov_yy'
    data = pd.read_csv(dataFile, header=None).to_numpy()
    num_samples = data.shape[0]
    ft_to_meteres = 0.3048

    # Collect all x, y and cov values
    x = data[:, 1] * ft_to_meteres
    y = data[:, 0] * ft_to_meteres

    cov = data[:, 2:].reshape(-1, 2, 2)

    # Plot the data
    for i in range(num_samples):
        plotCov2D(center=[x[i], y[i]], cov=cov[i] * ft_to_meteres ** 2, color="b")
    plt.plot(x, y, 'bo-', label='Data')

    if dataTrueFile is not None:
        # Data should be in format: x, y
        dataTruth = pd.read_csv(dataTrueFile, header=None).to_numpy()
        x_truth = dataTruth[:, 1] * ft_to_meteres
        y_truth = dataTruth[:, 0] * ft_to_meteres
        plt.plot(x_truth, y_truth, 'ko-', label='Ground Truth')

    plt.gca().set_aspect('equal')
    plt.xlabel('x (m)')
    plt.ylabel('y (m)')
    plt.legend()

    plt.show()


def plotCov2D(center=[0., 0.], cov=[[1., 0.], [0., 1.]], color="red", fillColor=None, nSigma=1, NOP=360):
    """This will plot a 2d error ellipse for the given covariance matrix

    Parameters:
    center: Center of the circle to be plotted, [x, y] default [0, 0]
    cov: The covariance matrix we're plotting - defaultsefaults to the identity matrix, but that's not useful.
    color: What color (use hex for #RGBA) to make the border - default red, full opacity - can provide array for multiple nSigma
    fillColor: What color to fill the circle, defaults to none - can provide array for multiple nSigma
    nSigma: The mahalanobis distance to plot - can provide array
    NOP: The number of points used to draw the error ellipses.  This cannot be an array, they all have to be the same.

    Return:
    None
    """
    color = np.array([color]).reshape(-1)
    fillColor = np.array([fillColor]).reshape(-1)
    nSigma = np.array([nSigma]).reshape(-1)

    color = (np.tile(color, int(np.ceil(len(nSigma) / len(color))))).flatten()[:len(nSigma)] if len(color) < len(nSigma) else color
    fillColor = (np.tile(fillColor, int(np.ceil(len(nSigma) / len(fillColor))))).flatten()[:len(nSigma)] if len(fillColor) < len(nSigma) else fillColor

    evals, evects = np.linalg.eig(cov)
    maxIndex = 0 if np.max(evals) == evals[0] else 1
    minIndex = 1 if maxIndex == 0 else 0
    angle = -np.arctan2(evects[:, maxIndex][1], evects[:, maxIndex][0])

    tSpace = np.linspace(0, 2 * np.pi, NOP)
    ellMat = np.column_stack([np.cos(tSpace), np.sin(tSpace)])

    axisBase = np.sqrt(evals)

    for index in range(len(nSigma)):
        sigma = nSigma[index]
        thisColor = color[index]
        thisFill = fillColor[index]

        majLen = axisBase[maxIndex] * sigma
        minLen = axisBase[minIndex] * sigma
        ellMatCopy = ellMat.copy()
        ellMatCopy[:, 0] *= majLen
        ellMatCopy[:, 1] *= minLen
        rotMatrix = np.array([[np.cos(angle), -np.sin(angle)], [np.sin(angle), np.cos(angle)]])
        rotatedEll = ellMatCopy @ rotMatrix
        plt.plot(center[0] + rotatedEll[:, 0], center[1] + rotatedEll[:, 1], color=thisColor)
        if (thisFill is not None):
            plt.fill(center[0] + rotatedEll[:, 0], center[1] + rotatedEll[:, 1], color=thisFill)


if __name__ == "__main__":
    # plotCov2D(cov=[[4, 0],[0, 1]])

    parser = argparse.ArgumentParser(description='Plot the covariance of the accelerometer data')
    parser.add_argument('data', type=str,
                        help='Path to the experimentally collected data file, should be in CSV format with columns: x, y, cov_xx, cov_xy, cov_yx, cov_yy')
    parser.add_argument('-t', type=str, help='Path to the ground truth data file, should be in CSV format with columns: x, y')
    args = parser.parse_args()

    plotData(args.data, args.t)
