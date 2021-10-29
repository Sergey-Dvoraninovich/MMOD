import numpy as np
import matplotlib.pyplot as plt
import scipy.stats as st
from scipy.signal import _savitzky_golay

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

def build_diff_plot(theoretical_p, empirical_p, n, m):
    max_val = int(max(max(theoretical_p), max(empirical_p)) * 15) / 10
    states = [" "]
    for i in range(0, n + 1):
        states.append(str(i))
    for i in range(1, m + 1):
        states.append("(" + str(i) + ")")

    index = np.arange(n + m + 2)
    bw = 0.4
    plt.axis([0, n + m + 2, 0, max_val])
    plt.title('Final probability states difference', fontsize=20)
    line = [0.]
    line.extend(theoretical_p)
    plt.bar(index - 0.5 * bw, line, bw, color='b')
    line = [0.]
    line.extend(empirical_p)
    plt.bar(index + 0.5 * bw, line, bw, color='r')
    plt.xticks(index, states)
    plt.legend(['Theoretical probabilities', 'Empirical probabilities'])
    plt.show()

def build_stationarity_plot(stationarity_data, work_times, colors, n, m):
    states = [" "]
    for i in range(0, n + 1):
        states.append(str(i))
    for i in range(1, m + 1):
        states.append("(" + str(i) + ")")
    index = np.arange(n + m + 2)
    plt.xticks(index, states)

    bw = 0.4
    plt.axis([0, n + m + 2, 0, 0.3])
    plt.title('Final probability states difference', fontsize=20)

    line = [0.]
    line.extend(stationarity_data[0])
    plt.bar(index - 0.5 * bw, line, bw, color='b')
    legend = ['Theoretical probabilities']


    offset = 0
    for i in range(1, len(stationarity_data)):
        line = [0.]
        line.extend(stationarity_data[i])
        bw *= 0.5
        plt.bar(index + 0.5 * bw + offset, line, bw, color=colors[i-1])
        offset += bw
        legend.append('Empirical probabilities ' + str(work_times[i-1]) + "s")

    plt.legend(legend)
    plt.show()

def build_stationarity_diff_plot(differences, work_times, n, m):
    x = np.array(work_times[::-1])
    y = np.array(differences[::-1])
    yhat = _savitzky_golay.savgol_filter(y, 3, 2)

    plt.plot(x, y)
    plt.plot(x, yhat, color='red')

    chi_vale = st.chi2.isf(df=n + m - 5, q=0.01)
    y = []
    for _ in range(len(x)):
        y.append(chi_vale)

    plt.plot(x, y, color='blue')
    plt.show()

