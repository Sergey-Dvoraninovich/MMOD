import random
from enum import Enum
import bisect

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
        return '({}, {}, {}, {}, {}, {})'.format(self.id, self.start_time, self.waiting_timeout, self.is_processed, self.processing_time, self.waiting_time)

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

def generate_requests(lambda_val, work_time, v):
    requests = []
    for i in range(lambda_val * work_time):
        start_time = random.uniform(0, work_time)
        waiting_timeout = random.expovariate(1/v)
        request = Request(id=i+1, start_time=start_time, waiting_timeout=waiting_timeout)
        requests.append(request)
    requests.sort()
    return requests

def add_to_processing(request, actions, time=None):
    if time is None:
        time = request.start_time
    processing_end_time = time
    processing_end_time += random.expovariate(1/mu)
    bisect.insort(actions, Action(request, processing_end_time, ActionType.FINISH_PROCESSING))

m = 9
lambda_val = 2
mu = 10
v = 10
work_time = 20

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
        if processing_size < m:
            add_to_processing(request, actions)
            processing_size += 1
            state_log.append((processing_size, len(line), current_time))
        else:
            waiting_timeout = request.waiting_timeout
            waiting_timeout += request.start_time
            bisect.insort(actions, Action(request, waiting_timeout, ActionType.WAITING_TIMEOUT))
            line.append(request)
            state_log.append((processing_size, len(line), current_time))

    if current_action.action_type == ActionType.FINISH_PROCESSING:
        request.processing_time = current_time - request.start_time
        request.is_processed = True
        if request.waiting_time is None:
            request.waiting_time = 0

        if len(line) != 0:
            waiting_request = line.pop(0)
            waiting_time = current_time - waiting_request.start_time
            waiting_request.waiting_time = waiting_time
            actions = list(filter(lambda action: action.request != waiting_request and action.action_type != ActionType.WAITING_TIMEOUT, actions))
            add_to_processing(waiting_request, actions, current_time)
            state_log.append((processing_size, len(line), current_time))
        else:
            processing_size -= 1
            state_log.append((processing_size, len(line), current_time))

    if current_action.action_type == ActionType.WAITING_TIMEOUT:
        request.is_processed = False
        line.remove(request)
        state_log.append((processing_size, len(line), current_time))




for event in state_log:
    print ("[" + str(event[0]) + " processing][" + str(event[1]) + " in line]["+str(event[2]) + "s]")

for request in requests:
    line = ""
    if request.is_processed != True:
        line = "-DECLINED- "
    if request.is_processed is None:
        line = "-ERROR- "
    line += "[" + str(request.id) + "]"
    line += "[" + str(request.processing_time) + "s processed]"
    line += "[" + str(request.waiting_time) + "s in line]"
    print (line)


