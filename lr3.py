import random
import bisect
import scipy.stats as st
from smo_utils import Action, ActionType, generate_requests, Request, prind_data

def run_model(n, m, lambda_val, mu, v, work_time):
    prev_time = 0
    s_waiting_time = 0
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

        if (len(line) > 3):
            s_waiting_time += (len(line) - 3) * (current_time - prev_time)
        prev_time = current_time

    return state_log, requests, s_waiting_time

days_amount = 100
n = 2
m = 10
lambda_val = 1 / (2 * 60)
mu = 1 / (6 * 60)
v = 1 / (9 * 60)
work_time = (24 * 60) * days_amount
s_fine = 100

state_log, requests, s_waiting_time = run_model(n, m, lambda_val, mu, v, work_time)

prind_data(n, m, lambda_val, mu, v, state_log, requests)

total_time_minutes = int(s_waiting_time / days_amount)
total_fine = s_fine * total_time_minutes / 60
total_fine = round(total_fine, 2)
print("\nTotal fine")
print(total_fine)
print("Total waiting hours")
print(str(total_time_minutes // 60) + "h " + str(total_time_minutes % 50) + "m")



