import numpy as np
import math
import scipy
from scipy import stats
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
        mx += (i+1) * x[i]
        mx2 += (i+1)**2 * x[i]
    my = 0
    my2 = 0
    for i in range(m):
        my += (i+1) * y[i]
        my2 += (i+1)**2 * y[i]
    dx = mx2 - mx**2
    dy = my2 - my**2
    mxy = 0
    for i in range(n):
        for j in range(m):
            mxy += (i+1) * (j+1) * matrix[i][j]
    cov = mxy - mx * my
    rxy = cov / math.sqrt(dx * dy)
    return mx, my, dx, dy, cov, rxy

def get_interval_data(values):
    values_amount = len(values)
    y_values = []
    x_values = []
    for value in values:
        y_values.append(value[1])
        x_values.append(value[0])
    x, y, sx, sy = 0, 0, 0, 0
    for i in range(values_amount):
        x += x_values[i]
        y += y_values[i]
    x /= values_amount
    y /= values_amount
    for i in range(values_amount):
        sx += (x_values[i] - x) ** 2
        sy += (y_values[i] - y) ** 2
    sx /= values_amount - 1
    sy /= values_amount - 1
    return x, y, sx, sy


def get_m_intervals(values):
    a = 0.05
    values_amount = len(values)
    x, y, sx, sy = get_interval_data(values)
    x_delta = sx * stats.t.ppf((2 - a) / 2, 10)
    x_delta /= math.sqrt(values_amount - 1)
    min_x = x - x_delta
    max_x = x + x_delta
    y_delta = sy * stats.t.ppf((2 - a) / 2, 10)
    y_delta /= math.sqrt(values_amount - 1)
    min_y = y - y_delta
    max_y = y + y_delta
    return min_x, max_x, min_y, max_y

def get_d_intervals(values):
    a = 0.05
    values_amount = len(values)
    x, y, sx, sy = get_interval_data(values)
    
    min_x = values_amount * sx
    min_x /= stats.chi2.isf(df=values_amount, q=a/2)
    max_x = values_amount * sx
    max_x /=stats.chi2.isf(df=values_amount, q=1 - a/2)

    min_y = values_amount * sy
    min_y /= stats.chi2.isf(df=values_amount, q=a/2)
    max_y = values_amount * sy
    max_y /= stats.chi2.isf(df=values_amount, q=1 - a/2)
    return min_x, max_x, min_y, max_y

def check_mizes(matrix, generated_matrix, n, m):
    a = 0.05
    critical_value = 0.461
    result = 0
    for i in range(n):
        for j in range(m):
            delta = matrix[i][j]
            delta -= generated_matrix[i][j]
            delta **= 2
            result += delta
    result = 1 / (12 * n * m) + result
    return a, critical_value, result

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
min_x, max_x, min_y, max_y = get_m_intervals(values)
print("\n" + str(np.array(generated_matrix)))
print("--- M[X] --- " + str(mx))
print(str(min_x) + " - " + str(max_x))
print("--- M[Y] --- " + str(my))
print(str(min_y) + " - " + str(max_y))
min_x, max_x, min_y, max_y = get_d_intervals(values)
print("--- D[X] --- " + str(dx))
print(str(min_x) + " - " + str(max_x))
print("--- D[Y] --- " + str(dy))
print(str(min_y) + " - " + str(max_y))
print("--- cov ---- " + str(cov))
print("--- rxy ---- " + str(rxy))


print("\n------- Mizes criteria -------")
a, critical_value, result = check_mizes(matrix, generated_matrix, n, m)
print("Critical value - " + str(critical_value))
print("        Result - " + str(result))
#print(stats.chi2.isf(df=2, q=0.025))
#print(stats.t.ppf((1 + 0.95)/2, 9))

