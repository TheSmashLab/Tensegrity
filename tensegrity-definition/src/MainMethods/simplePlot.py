import numpy as np
import matplotlib.pyplot as plt


if __name__ == "__main__":
    #square commands
    x_S = np.array([0, 0, .5, 0, -.3, -.6, 0, .6, .7])
    y_s = np.array([0, .5, 1, .5, .5, -0, -.3, -.5, -1])

    #target same path
    # x_S = np.array([0, 0, .3, 0, -.6, -1.2, -.6, -1.1, -1.5, -1.5])
    # y_s = np.array([0, .5, .9, .5, .4, 1.1, 1.4, .9, 1.3, 1.8])

    #target different path
    # x_S = np.array([0, 0, -.4, -.95, -1.5, -1.5,])
    # y_s = np.array([0, .5, 1, .9, 1.3, 2,])


    plt.plot(x_S, y_s, color='r')
    plt.show()


