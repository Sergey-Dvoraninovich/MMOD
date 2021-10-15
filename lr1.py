import numpy as np
import math
import matplotlib.pyplot as plt
from plots import histogram_3d, histogram

def make_line(matrix):
    line = []
    for i in range(len(matrix)):
        line.extend(matrix[i])
    return line

def get_full_x(matrix, n, m):
    result = []
    for i in range(n):
        sum = 0
        for j in range(m):
            sum += matrix[i][j]
        result.append(sum)
    return result

def get_full_y(matrix, n, m):
    result = []
    for j in range(m):
        sum = 0
        for i in range(n):
            sum += matrix[i][j]
        result.append(sum)
    return result

def get_appearances(values, n, m):
    y_appearances = []
    for i in range(m):
        y_appearances.append(0)
    x_appearances = []
    for j in range(n):
        x_appearances.append(0)
    for value in values:
        x_appearances[value[0]-1] += 1
        y_appearances[value[1]-1] += 1
    return y_appearances, x_appearances

def normalize_appearances(appearances, values_amount):
    normalization_value = 1 / values_amount
    for i in range(len(appearances)):
        appearances[i] *= normalization_value
    return appearances

def normalize_matrix(values, values_amount, n, m):
    normalization_value = 1 / values_amount
    matrix = []
    for i in range(n):
        line = []
        for j in range(m):
            line.append(0)
        matrix.append(line)
    for value in values:
        matrix[value[0]-1][value[1]-1] += 1
    for i in range(n):
        for j in range(m):
            matrix[i][j] *= normalization_value
    return matrix

def get_data(matrix, n, m):
    x = get_full_x(matrix, n, m)
    y = get_full_y(matrix, n, m)
    mx = 0
    mx2 = 0
    for i in range(n):
        mx += i * x[i]
        mx2 += i**2 * x[i]
    my = 0
    my2 = 0
    for i in range(n):
        my += i * y[i]
        my2 += i**2 * y[i]
    dx = mx2 - mx**2
    dy = my2 - my**2
    mxy = 0
    for i in range(n):
        for j in range(m):
            mxy += i * j * matrix[i][j]
    cov = mxy - mx * my
    rxy = cov / math.sqrt(dx * dy)
    return mx, my, dx, dy, cov, rxy


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
full_y = get_full_y(matrix, n, m)
full_x = get_full_x(matrix, n, m)

values = []
values_amount = 10000
for _ in range(values_amount):
    result = generate_value(matrix, n, m)
    values.append(result)

y_appearances, x_appearances = get_appearances(values, n, m)
print("\n--- X info ---")
print(x_appearances)
print(get_full_x(matrix, n, m))

print("\n--- Y info ---")
print(y_appearances)
print(get_full_y(matrix, n, m))

histogram_3d(values, n, m)
histogram(x_appearances, n, full_x)
histogram(y_appearances, m, full_y)

mx, my, dx, dy, cov, rxy = get_data(matrix, n, m)
print("\n" + str(np.array(matrix)))
print("--- M[X] --- " + str(mx))
print("--- M[Y] --- " + str(my))
print("--- D[X] --- " + str(dx))
print("--- D[Y] --- " + str(dy))
print("--- cov ---- " + str(cov))
print("--- rxy ---- " + str(rxy))

generated_matrix = normalize_matrix(values, values_amount, n, m)
mx, my, dx, dy, cov, rxy = get_data(generated_matrix, n, m)
print("\n" + str(np.array(generated_matrix)))
print("--- M[X] --- " + str(mx))
print("--- M[Y] --- " + str(my))
print("--- D[X] --- " + str(dx))
print("--- D[Y] --- " + str(dy))
print("--- cov ---- " + str(cov))
print("--- rxy ---- " + str(rxy))




