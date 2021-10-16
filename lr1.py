import numpy as np
import math
import scipy
from scipy import optimize
from scipy import stats
from scipy import special
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

def get_r_interval(gen_cov, dx, dy, n):
    a = 0.05
    z = optimize.fsolve(lambda x: special.erf(x) - a, 0)[0]
    rxy = gen_cov / math.sqrt(dx * dy)
    a = 0.5 * math.log((1 + rxy) / (1 - rxy)) - z / math.sqrt(n-3)
    b = 0.5 * math.log((1 + rxy) / (1 - rxy)) + z / math.sqrt(n-3)
    min = (math.e ** (2*a) - 1)/(math.e ** (2*a) + 1)
    max = (math.e ** (2*b) - 1)/(math.e ** (2*b) + 1)
    return min, max

def check_mizes(matrix, generated_matrix, n, m):
    a = 0.05
    critical_value = 0.461
    result = 0
    m_line = make_line(matrix)
    gen_line = make_line(generated_matrix)
    m_sum = 0
    gen_sum = 0
    for i in range(n*m):
        m_sum += m_line[i]
        gen_sum += gen_line[i]
        delta = m_sum
        delta -= gen_sum
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

success = True

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
print("--- rxy ---- " + str(rxy))

generated_matrix = normalize_matrix(values, values_amount, n, m)
base_dx, base_dy = dx, dy
mx, my, dx, dy, cov, rxy = get_data(generated_matrix, n, m)
min_x, max_x, min_y, max_y = get_m_intervals(values)
print("\n" + str(np.array(generated_matrix)))
print("--- M[X] --- " + str(mx))
print(str(min_x) + " - " + str(max_x))
if min_x < mx and mx < max_x:
    print("OK")
else:
    print("Invalid M interval for x")
    success = False

print("--- M[Y] --- " + str(my))
print(str(min_y) + " - " + str(max_y))
if min_y < my and my < max_y:
    print("OK")
else:
    print("Invalid M interval for y")
    success = False

min_x, max_x, min_y, max_y = get_d_intervals(values)
print("--- D[X] --- " + str(dx))
print(str(min_x) + " - " + str(max_x))
if min_x < dx and dx < max_x:
    print("OK")
else:
    print("Invalid D interval for x")
    success = False

print("--- D[Y] --- " + str(dy))
print(str(min_y) + " - " + str(max_y))
if min_y < dy and dy < max_y:
    print("OK")
else:
    print("Invalid D interval for y")
    success = False

print("--- rxy ---- " + str(rxy))


print("\n------- Mizes criteria -------")
a, critical_value, result = check_mizes(matrix, generated_matrix, n, m)
print("Critical value - " + str(critical_value))
print("        Result - " + str(result))
if result < critical_value:
    print("                 OK")
else:
    print("Invalid Mizes criteria")
    success = False

if success:
    print("Valid result")
else:
    print("Inalid result")
