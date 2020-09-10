from heapq import heappop, heappush
import itertools
import copy

from constants import CellState, Actions
dist = {
    "FORWARD": 1,
    "U_TURN": 1,
    "TURN_LEFT": 1,
    "TURN_RIGHT": 1
}


def __isAllowed(state, x, y):
    if x < 0 or x >= state.grid.height: return False
    if y < 0 or y >= state.grid.width: return False
    return True


def explore_new(state, x, y, direction):
    state.robot.set_robot(x, y, direction)


def virtual_explore(state, x, y, direction):
    state.robot.set_robot(x, y, direction)
    for sensor in state.robot.sensors:
        all_sensable_cells = sensor.get_all_cells(x, y, direction)
        for cell in all_sensable_cells:
            _x, _y = cell
            if not __isAllowed(state, _x, _y):
                break
            if state.explored_grid[_x][_y].is_same(CellState.FREE):
                continue
            elif state.explored_grid[_x][_y].is_same(CellState.OBSTACLE):
                break
            elif state.explored_grid[_x][_y].is_same(CellState.UNKNOWN):
                return True
    return False


def virtual_sense(state, action):
    # used to get a approximate next_state
    # virtual_sense won't change state
    x, y, direction = state.robot.next_state(action, state.x, state.y, state.direction)
    state_copy = copy.deepcopy(state)
    state_copy.robot.set_robot(x, y, direction)
    state_copy.x = x
    state_copy.y = y
    state_copy.direction = direction
    explored_grid_before_predict = copy.deepcopy(state.explored_grid)
    sensed_cells_state = {}
    for sensor in state_copy.robot.sensors:
        # predict and update state_copy.explored_map and num_explored
        sensed_cells_state.update(sensor.get_cells_state_with_explored_grid(x, y, direction, state_copy))
    for sensed_cell in sensed_cells_state.keys():
        x, y = sensed_cell
        if explored_grid_before_predict[x][y].is_same(CellState.UNKNOWN):
            state_copy.num_explored += 1
    if state_copy.num_explored == 300:
        state_copy.is_terminal = True
        # print("virtual sense:", next_state.num_explored)
    return state_copy


# def dijkstra(state):
#     # virtual wall can walk, but will stuck at corner, see case1.jpg
#     if state.num_explored == 300:
#         return 1
#     pq = []  # list of entries arranged in a heap
#     entry_finder = {}  # mapping of tasks to entries
#     REMOVED = '<removed-task>'  # placeholder for a removed task
#     counter = itertools.count()  # unique sequence count
#
#     def add_task(task, priority=0):
#         'Add a new task or update the priority of an existing task'
#         if task in entry_finder:
#             remove_task(task)
#         count = next(counter)
#         entry = [priority, count, task]
#         entry_finder[task] = entry
#         heappush(pq, entry)
#
#     def remove_task(task):
#         'Mark an existing task as REMOVED.  Raise KeyError if not found.'
#         entry = entry_finder.pop(task)
#         entry[-1] = REMOVED
#
#     def pop_task():
#         'Remove and return the lowest priority task. Raise KeyError if empty.'
#         while pq:
#             priority, count, task = heappop(pq)
#             if task is not REMOVED:
#                 del entry_finder[task]
#                 return task
#         raise KeyError('pop from an empty priority queue')
#
#     distance = {}
#     task = (state.x, state.y, state.direction)
#     distance[task] = 0
#     visited = set()
#     add_task(task, distance[task])
#     while pq:
#         task = pop_task()
#         visited.add(task)
#         x, y, direction = task
#         #
#         # temp_state = copy.deepcopy(state)
#         # virtual_explore(temp_state, x, y, direction)
#         # if temp_state.num_explored != state.num_explored:
#         #     return distance[task]
#
#         for action in Actions:
#             next_x, next_y, next_direction = state.robot.next_state(action, x, y, direction)
#             next_task = (next_x, next_y, next_direction)
#
#             # check is allowed
#             if not state.grid.is_allowed(next_x, next_y):
#                 continue
#
#             # find the shortest distance to the first unexplored cell
#             if state.explored_grid[next_x][next_y].is_same(CellState.UNKNOWN):
#                 return distance[task]+dist[action.name]
#
#             if state.grid[next_x][next_y].is_same(CellState.OBSTACLE):
#                 continue
#
#             # if state.grid.is_virtual_wall(next_x, next_y):
#             #     continue
#             distance[next_task] = distance[task]+dist[action.name]
#             if next_task not in visited:
#                 add_task(next_task, distance[next_task])


def dijkstra(state):
    # shortest distance to sense unexplored area
    if state.num_explored == 300:
        return 1.0
    pq = []  # list of entries arranged in a heap
    entry_finder = {}  # mapping of tasks to entries
    REMOVED = '<removed-task>'  # placeholder for a removed task
    counter = itertools.count()  # unique sequence count

    def add_task(task, priority=0):
        'Add a new task or update the priority of an existing task'
        if task in entry_finder:
            remove_task(task)
        count = next(counter)
        entry = [priority, count, task]
        entry_finder[task] = entry
        heappush(pq, entry)

    def remove_task(task):
        'Mark an existing task as REMOVED.  Raise KeyError if not found.'
        entry = entry_finder.pop(task)
        entry[-1] = REMOVED

    def pop_task():
        'Remove and return the lowest priority task. Raise KeyError if empty.'
        while pq:
            priority, count, task = heappop(pq)
            if task is not REMOVED:
                del entry_finder[task]
                return task
        raise KeyError('pop from an empty priority queue')

    distance = {}
    x, y, direction = state.x, state.y, state.direction
    task = (x, y, direction)
    distance[task] = 1.0
    visited = set()
    add_task(task, distance[task])
    # print("initial append to pq:", task, distance[task])
    while pq:
        task = pop_task()
        visited.add(task)
        x, y, direction = task

        if virtual_explore(state, x, y, direction):
            # print(x, y, direction, distance[task])
            return distance[task]

        for _action in Actions:
            _x, _y, _direction = state.robot.next_state(_action, x, y, direction)
            _task = (_x, _y, _direction)
            if (_x, _y, _direction) in visited:
                continue

            # check is allowed
            if not __isAllowed(state, _x, _y):
                continue

            if state.explored_grid.is_virtual_wall(_x, _y):
                visited.add((_x, _y, _direction))
                continue

            if state.explored_grid[_x][_y].is_same(CellState.OBSTACLE):
                visited.add((_x, _y, _direction))
                continue

            if _task not in visited:
                distance[_task] = distance[task] + dist[_action.name]
                # print("append to pq:", _task, distance[_task])
                add_task(_task, distance[_task])

    raise("There exist cells that are unable to reach")


def total_number_newly_explore_given_steps(state, action, num_step):
    pass


def discontinuous_unexplored_cells(state):
    pass