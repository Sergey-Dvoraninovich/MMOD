import random

def get_matrix(n, m):
    matrix = []
    sum = 0
    for _ in range(n):
        matrix_line = []
        for _ in range(m):
            value = random.random()
            matrix_line.append(value)
            sum += value
        matrix.append(matrix_line)
    normalization_value = 1 / sum
    sum = 0
    for i in range(n):
        for j in range(m):
            matrix[i][j] = matrix[i][j] * normalization_value
            sum += matrix[i][j]
    return matrix

def get_q_line(p, n, m):
    q_line = []
    for i in range(n):
        sum = 0
        for j in range(m):
            sum += p[i][j]
        q_line.append(sum)
    return q_line

def get_l_line(q_line, n):
    l_line = []
    current_sum = 0
    for i in range(n):
        current_sum += q_line[i]
        l_line.append(current_sum)
    l_line[len(l_line)-1] = 1
    return l_line

def get_x():
    return random.random()




