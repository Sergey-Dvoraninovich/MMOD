import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.axes3d import Axes3D
from matplotlib import cm

def make_line(matrix):
    line = []
    for i in range(len(matrix)):
        line.extend(matrix[i])
    return line

def get_full_y(matrix, n, m):
    result = []
    for i in range(n):
        sum = 0
        for j in range(m):
            sum += matrix[i][j]
        result.append(sum)
    return result

def get_appearances(values, n, m):
    y_appearances = []
    for i in range(n):
        y_appearances.append(0)
    x_appearances = []
    for j in range(m):
        x_appearances.append(0)
    for value in values:
        y_appearances[value[0]-1] += 1
        x_appearances[value[1]-1] += 1
    return x_appearances, y_appearances

def normalize_appearances(appearances, values_amount):
    normalization_value = 1 / values_amount
    for i in range(len(appearances)):
        appearances[i] *= normalization_value
    return appearances


def get_full_x(matrix, n, m):
    result = []
    for j in range(m):
        sum = 0
        for i in range(n):
            sum += matrix[i][j]
        result.append(sum)
    return result

def make_probabilities_line(matrix):
    p_line = []
    for i in range(len(matrix)):
        p_line.extend(matrix[i])
    sum = 0
    result = []
    for i in range(len(p_line)):
        sum += p_line[i]
        result.append(sum)
    return result

def generate_value(matrix, n, m):
    x = np.random.uniform()
    l_line = make_probabilities_line(matrix)
    pos = 0
    if x <= l_line[0]:
        result = pos
    pos += 1
    while pos < len(l_line):
        if x > l_line[pos-1] and x <= l_line[pos]:
            result = pos
            break
        pos += 1
    n = result // m
    m = result - n * m
    n += 1
    m += 1
    return n, m

n = 3
m = 5
matrix = [[0.09, 0.045, 0.035, 0.05, 0.08],
          [0.1,  0.11,  0.07,  0.1,  0.07],
          [0.05, 0.035, 0.045, 0.07, 0.05]]
print(get_full_y(matrix, n, m))
print(get_full_x(matrix, n, m))

values = []
values_amount = 10000
for _ in range(values_amount):
    result = generate_value(matrix, n, m)
    values.append(result)

x_appearances, y_appearances = get_appearances(values, n, m)
#x_appearances = normalize_appearances(x_appearances, values_amount)
print("\n--- X info ---")
print(x_appearances)
print(get_full_x(matrix, n, m))

#y_appearances = normalize_appearances(y_appearances, values_amount)
print("\n--- Y info ---")
print(y_appearances)
print(get_full_y(matrix, n, m))


x_val = []
y_val = []
for i in range(values_amount):
    x_val.append(values[i][1])
    y_val.append(values[i][0])
print(x_val)
print(y_val)

fig = plt.figure()
ax = fig.add_subplot(projection='3d')
x, y = x_val, y_val
hist, xedges, yedges = np.histogram2d(x, y, bins=[m, n], range=[[1, m+1], [1, n+1]])

# Construct arrays for the anchor positions of the 16 bars.
xpos, ypos = np.meshgrid(xedges[:-1] + 0.25, yedges[:-1] + 0.25, indexing="ij")
xpos = xpos.ravel()
ypos = ypos.ravel()
zpos = 0

# Construct arrays with the dimensions for the 16 bars.
dx = dy = 0.5 * np.ones_like(zpos)
dz = hist.ravel()

ax.bar3d(xpos, ypos, zpos, dx, dy, dz, zsort='average')

plt.show()


