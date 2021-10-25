import random
from enum import Enum
import bisect
import math


class ActionType(Enum):
    APPEAR = 1
    FINISH_PROCESSING = 2
    WAITING_TIMEOUT = 3
    DECLINE = 4


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
    a = alpha / n
    p0 = 0
    for k in range(n + 1):
        p0 += (alpha ** k) / math.factorial(k)
    line_sum = a * (1 - (a**m))
    line_sum /= (1 - a)
    line_sum *= (alpha ** n) / math.factorial(n)
    p0 += line_sum
    p0 = 1 / p0

    theoretical_p = [p0]
    for i in range(n):
        k = i + 1
        pk = ((alpha ** k) / math.factorial(k)) * p0
        theoretical_p.append(pk)
    for i in range(m):
        s = i + 1
        pk = ((alpha ** (n + s)) / (math.factorial(n) * (n ** s))) * p0
        theoretical_p.append(pk)

    decline_probability = ((alpha ** (n + m)) / ((n ** m) * math.factorial(n))) * p0
    Q = 1 - decline_probability
    A = lambda_val * Q
    l_line = (alpha ** (n+1)) / (n * math.factorial(n)) * p0
    l_line *= 1 - ((alpha/n)**m)*(m + 1 - m*alpha/n)
    l_line /= ((1 - alpha/n) ** 2)
    return decline_probability, l_line, theoretical_p


def generate_requests(lambda_val, work_time, v):
    requests = []
    for i in range(lambda_val * work_time):
        start_time = random.uniform(0, work_time)
        waiting_timeout = random.expovariate(v)
        request = Request(id=i + 1, start_time=start_time, waiting_timeout=waiting_timeout)
        requests.append(request)
    requests.sort()
    for i in range(lambda_val * work_time):
        requests[i].id = i + 1
    return requests

def get_empirical_p(state_log, print_result=False):
    empirical_p = []
    for _ in range(n + m + 1):
        empirical_p.append(0)
    previous_period = state_log[0]
    total_work_time = 0
    for i in range(1, len(state_log)):
        period = state_log[i]
        duration = period[2] - previous_period[2]
        total_work_time += duration
        empirical_p[previous_period[0] + previous_period[1]] += duration
        previous_period = period
    for i in range(n + m + 1):
        empirical_p[i] /= total_work_time
    return empirical_p

def get_decline_probability(requests):
    declines_amount = 0
    for request in requests:
         if not request.is_processed: # and request.waiting_time == 0:
             declines_amount += 1
    decline_probability = declines_amount / len(requests)
    return decline_probability

def get_requests_in_query(empirical_p):
    result = 0
    for i in range(n + 1, n + m + 1):
        result += empirical_p[i] * (i - n)
    return result


def add_to_processing(request, actions, time=None):
    if time is None:
        time = request.start_time
    processing_end_time = time
    processing_end_time += random.expovariate(mu)
    bisect.insort(actions, Action(request, processing_end_time, ActionType.FINISH_PROCESSING))


n = 5
m = 5
lambda_val = 2
mu = 0.5
v = 0.5
work_time = 9000

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
            add_to_processing(request, actions)
            processing_size += 1
            state_log.append((processing_size, len(line), current_time))
        elif len(line) < m:
            waiting_timeout = request.waiting_timeout
            waiting_timeout += request.start_time
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
                lambda action: action.request != waiting_request and action.action_type != ActionType.WAITING_TIMEOUT,
                actions))
            add_to_processing(waiting_request, actions, current_time)
            state_log.append((processing_size, len(line), current_time))
        else:
            processing_size -= 1
            state_log.append((processing_size, len(line), current_time))

    if current_action.action_type == ActionType.WAITING_TIMEOUT:
        request.is_processed = False
        line.remove(request)
        state_log.append((processing_size, len(line), current_time))

# for event in state_log:
#     print ("[" + str(event[0]) + " processing][" + str(event[1]) + " in line]["+str(event[2]) + "s]")
#
# for request in requests:
#     line = ""
#     if request.is_processed != True:
#         line = "-DECLINED- "
#     if request.is_processed is None:
#         line = "-ERROR- "
#     line += "[" + str(request.id) + "]"
#     line += "[" + str(request.processing_time) + "s processed]"
#     line += "[" + str(request.waiting_time) + "s in line]"
#     print (line)


decline_probability, line_requests_theoretical, theoretical_p = calculate_theoretical_data(n, m, lambda_val, mu, v)
print("Theoretical probabilities")
print("   in processing: " + str(theoretical_p[:n + 1]))
print("         in line: " + str(theoretical_p[n + 1:]))
print("Theoretical decline probability")
print(decline_probability)
print("Theoretical requests in query")
print(line_requests_theoretical)

empirical_p = get_empirical_p(state_log)
print("Theoretical probabilities")
print("   in processing: " + str(empirical_p[:n + 1]))
print("         in line: " + str(empirical_p[n + 1:]))

decline_probability = get_decline_probability(requests)
print("Empirical decline probability")
print(decline_probability)
line_requests_theoretical = get_requests_in_query(empirical_p)
print("Empirical requests in query")
print(line_requests_theoretical)

