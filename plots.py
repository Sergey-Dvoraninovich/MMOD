import numpy as np
import matplotlib.pyplot as plt

def histogram_3d(values, n, m):
    x_val = []
    y_val = []
    for i in range(len(values)):
        x_val.append(values[i][1])
        y_val.append(values[i][0])

    fig = plt.figure()
    ax = fig.add_subplot(projection='3d')
    x, y = x_val, y_val
    hist, xedges, yedges = np.histogram2d(x, y, bins=[m, n], range=[[1, m + 1], [1, n + 1]])

    xpos, ypos = np.meshgrid(xedges[:-1] + 0.25, yedges[:-1] + 0.25, indexing="ij")
    xpos = xpos.ravel()
    ypos = ypos.ravel()
    zpos = 0

    dx = dy = 0.5 * np.ones_like(zpos)
    dz = hist.ravel()

    ax.bar3d(xpos, ypos, zpos, dx, dy, dz, zsort='average')

    plt.show()

def histogram(appearances, n, expected_probabilities):
    indexes = []
    for i in range(n):
        indexes.append(i+1)
    plt.bar(indexes, appearances)
    plt.title(expected_probabilities)
    plt.show()