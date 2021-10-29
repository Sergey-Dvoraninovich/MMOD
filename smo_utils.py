import random
import numpy as np
from enum import Enum
from plots import build_diff_plot, build_stationarity_plot, build_stationarity_diff_plot
import bisect
import math

class ActionType(Enum):
    APPEAR = 1
    FINISH_PROCESSING = 2
    WAITING_TIMEOUT = 3

class Request:
    def __init__(self, id, start_time, waiting_timeout):
        self.id = id
        self.start_time = start_time
        self.waiting_timeout = waiting_timeout
        self.is_processed = None
        self.processing_time = waiting_timeout
        self.waiting_time = waiting_timeout

    def __gt__(self, other):
        result = False
        if self.start_time > other.start_time:
            result = True
        return result

    def __eq__(self, other):
        return self.id == other.id

    def __str__(self):
        return '({}, {}, {}, {}, {}, {})'.format(self.id, self.start_time, self.waiting_timeout, self.is_processed,
                                                 self.processing_time, self.waiting_time)


class Action:
    def __init__(self, request, time, action_type):
        self.request = request
        self.time = time
        self.action_type = action_type

    def __gt__(self, other):
        result = False
        if self.time > other.time:
            result = True
        return result

    def __str__(self):
        return '({}, {}, {})'.format(self.request.id, self.time, self.action_type)

def calculate_theoretical_data(n, m, lambda_val, mu, v):
    alpha = lambda_val / mu
    beta = v / mu

    p0 = 0
    for k in range(n + 1):
        p0 += (alpha ** k) / (math.factorial(k))
    line_sum = 0
    for k in range(1, m + 1):
        local_multiplication = 1
        for j in range(1, k + 1):
            local_multiplication *= (n + j * beta)
        line_sum += (alpha ** k) / local_multiplication
    line_sum *= (alpha ** n) / math.factorial(n)
    p0 += line_sum
    p0 = 1 / p0
    theoretical_p = [p0]

    # empirical p processing
    for k in range(1, n + 1):
        pk = ((alpha ** k) * p0) / math.factorial(k)
        theoretical_p.append(pk)
    pn = theoretical_p[n]
    for s in range(1, m + 1):
        local_multiplication = 1
        for j in range(1, s + 1):
            local_multiplication *= (n + j * beta)
        pk = (pn * (alpha ** s)) / local_multiplication
        theoretical_p.append(pk)

    # decline p processing
    m_local_multiplication = 1
    for j in range(1, m + 1):
        m_local_multiplication *= (n + j * beta)
    p_decline = (pn * (alpha ** n)) / m_local_multiplication

    Q = 1 - p_decline
    A = lambda_val * Q

    L_line = 0
    for i in range(1, m + 1):
        local_multiplication = 1
        for j in range(1, i + 1):
            local_multiplication *= (n + j * beta)
        L_line += (i * alpha ** i) / local_multiplication
    L_line *= pn

    L_smo = 0
    for k in range(n + m + 1):
        L_smo += k * theoretical_p[k]

    T_line = L_line / lambda_val
    T_smo = L_smo / lambda_val

    n_processing = 0
    for k in range(n + 1):
        n_processing += k * theoretical_p[k]
    for k in range(n + 1, n + m + 1):
        n_processing += n * theoretical_p[k]

    return theoretical_p, A, p_decline, L_line, L_smo, T_line, T_smo, n_processing


def generate_requests(lambda_val, work_time, v):
    requests = []
    size = int(lambda_val * work_time)
    for i in range(size):
        start_time = random.uniform(0, work_time)
        waiting_timeout = random.expovariate(v)
        request = Request(id=i + 1, start_time=start_time, waiting_timeout=waiting_timeout)
        requests.append(request)
    requests.sort()
    for i in range(size):
        requests[i].id = i + 1
    return requests

def get_empirical_p(state_log, n, m):
    empirical_p = []
    for _ in range(n + m + 1):
        empirical_p.append(0)
    boundary = min(2 * n + 2 * m, int(len(state_log) * 0.2))
    previous_period = state_log[0]
    total_work_time = 0
    for i in range(boundary, len(state_log) - boundary):
        period = state_log[i]
        duration = period[2] - previous_period[2]
        total_work_time += duration
        empirical_p[previous_period[0] + previous_period[1]] += duration
        previous_period = period
    for i in range(n + m + 1):
        empirical_p[i] /= total_work_time
    return empirical_p

def get_decline_probability(requests, n, m):
    declines_amount = 0
    boundary = max(2*n + 2*m, int(len(requests)*0.2))
    for i in range(boundary, len(requests) - boundary):
        request = requests[i]
        if not request.is_processed:
            declines_amount += 1
    decline_probability = declines_amount / len(requests)
    return decline_probability

def get_requests_in_query(empirical_p, n, m):
    result = 0
    for k in range(n + 1, n + m + 1):
        result += empirical_p[k] * (k - n)
    return result

def get_requests_in_smo(empirical_p, n, m):
    result = 0
    for k in range(n + m + 1):
        result += empirical_p[k] * k
    return result

def get_requests_in_processing(empirical_p, n, m):
    result = 0
    for k in range(n + 1):
        result += empirical_p[k] * k
    for k in range(n + 1, n + m + 1):
        result += empirical_p[k] * n
    return result

def get_time_in_line(L_line, lambda_val):
    result = L_line / lambda_val
    return result

def get_time_in_smo(requests, n, m):
    boundary = max(2 * n + 2 * m, int(len(requests) * 0.2))
    total_time = 0
    total_amount = 0
    for i in range(boundary, len(requests) - boundary):
        total_time += requests[i].processing_time
        total_amount += 1
    result = total_time / total_amount
    return result

def get_time_in_smo_lr3(requests, n, m):
    boundary = int(len(requests) * 0.2)
    total_time = 0
    total_amount = 0
    for i in range(boundary, len(requests) - boundary):
        total_time += requests[i].processing_time
        total_amount += 1
    result = total_time / total_amount
    return result

def run_model(n, m, lambda_val, mu, v, work_time):
    requests = generate_requests(lambda_val, work_time, v)
    actions = []
    for request in requests:
        actions.append(Action(request, request.start_time, ActionType.APPEAR))

    processing_size = 0
    line = []
    state_log = [(0, 0, 0)]

    while len(actions) != 0:
        current_action = actions.pop(0)
        request = current_action.request
        current_time = current_action.time

        if current_action.action_type == ActionType.APPEAR:
            if processing_size < n:
                bisect.insort(actions,
                              Action(request, current_time + random.expovariate(mu), ActionType.FINISH_PROCESSING))
                processing_size += 1
                state_log.append((processing_size, len(line), current_time))
            elif len(line) < m:
                waiting_timeout = request.start_time + request.waiting_timeout
                bisect.insort(actions, Action(request, waiting_timeout, ActionType.WAITING_TIMEOUT))
                line.append(request)
                state_log.append((processing_size, len(line), current_time))
            else:
                request.is_processed = False
                request.waiting_time = 0

        if current_action.action_type == ActionType.FINISH_PROCESSING:
            request.processing_time = current_time - request.start_time
            request.is_processed = True
            if request.waiting_time is None:
                request.waiting_time = 0

            if len(line) != 0:
                waiting_request = line.pop(0)
                waiting_time = current_time - waiting_request.start_time
                waiting_request.waiting_time = waiting_time
                actions = list(filter(
                    lambda action: not (
                                action.request == waiting_request and action.action_type == ActionType.WAITING_TIMEOUT),
                    actions))
                bisect.insort(actions, Action(waiting_request, current_time + random.expovariate(mu),
                                              ActionType.FINISH_PROCESSING))
                state_log.append((processing_size, len(line), current_time))
            else:
                processing_size -= 1
                state_log.append((processing_size, len(line), current_time))

        if current_action.action_type == ActionType.WAITING_TIMEOUT:
            line.remove(request)
            request.is_processed = False
            state_log.append((processing_size, len(line), current_time))

    return state_log, requests

def get_stationarity_data(n, m, lambda_val, mu, v, work_times):
    theoretical_p, A, p_decline, L_line, L_smo, T_line, T_smo, n_processing = calculate_theoretical_data(n, m, lambda_val, mu, v)
    result = [theoretical_p]
    for time in work_times:
        state_log, requests = run_model(n, m, lambda_val, mu, v, time)
        empirical_p = get_empirical_p(state_log, n, m)
        result.append(empirical_p)
    return result

def count_xi_diffs(stationarity_data, n, m, lambda_val, work_time):
    theoretical_p = stationarity_data[0]
    differences = []
    for k in range(1, len(stationarity_data)):
        difference = 0
        empirical_p = stationarity_data[k]
        for i in range(n + m + 1):
            difference += ((theoretical_p[i] - empirical_p[i]) ** 2) / theoretical_p[i]
        difference *= lambda_val * work_time
        differences.append(difference)
    return differences

def prind_data(n, m, lambda_val, mu, v, state_log, requests):
    theoretical_p, A, p_decline, L_line, L_smo, T_line, T_smo, n_processing = calculate_theoretical_data(n, m, lambda_val, mu, v)
    print("\nTheoretical probabilities")
    print("   in processing: " + str(theoretical_p[:n + 1]))
    print("         in line: " + str(theoretical_p[n + 1:]))
    print("Theoretical decline probability")
    print(p_decline)
    print("Theoretical requests in line")
    print(L_line)
    print("Theoretical requests in SMO")
    print(L_smo)
    print("Theoretical requests in processing")
    print(n_processing)
    print("Theoretical time in line")
    print(T_line)
    print("Theoretical time in SMO")
    print(T_smo)

    empirical_p = get_empirical_p(state_log, n, m)
    print("\nTheoretical probabilities")
    print("   in processing: " + str(empirical_p[:n + 1]))
    print("         in line: " + str(empirical_p[n + 1:]))
    empirical_p_decline = get_decline_probability(requests, n, m)
    print("Empirical decline probability")
    print(empirical_p_decline)
    empirical_L_line = get_requests_in_query(empirical_p, n, m)
    print("Empirical requests in line")
    print(empirical_L_line)
    empirical_L_smo = get_requests_in_smo(empirical_p, n, m)
    print("Empirical requests in smo")
    print(empirical_L_smo)
    empirical_n_processing = get_requests_in_processing(empirical_p, n, m)
    print("Empirical requests in processing")
    print(empirical_n_processing)
    empirical_T_line = get_time_in_line(empirical_L_line, lambda_val)
    print("Empirical time in line")
    print(empirical_T_line)
    empirical_T_smo = get_time_in_smo_lr3(requests, n, m)
    print("Empirical time in SMO")
    print(empirical_T_smo)