from constants import CellState, Actions
from shortest_path import dijkstra
from shortest_path import virtual_sense
from utils import print_grid


###########################
# STATE
###########################
import util
import copy


class State:
    def __init__(self, x=None, y=None, direction=None, robot=None, explored_grid=None, num_explored=None, is_terminal=False, grid=None):
        self.x = x
        self.y = y
        self.direction = direction
        self.is_terminal = is_terminal
        self.num_explored = num_explored
        self.grid = grid
        self.explored_grid = explored_grid
        self.history = []
        self.robot = robot

    def get_num_explored(self):
        if self.num_explored is None:
            raise "None initialized number of explored cell"
        return self.num_explored

    def closest_unexplored(self, state, k):
        distance = [0.0]
        x = state.x
        y = state.y
        explored_grid = state.explored_grid
        for _x in range(self.grid.height):
            for _y in range(self.grid.width):
                if explored_grid[_x][_y].is_same(CellState.UNKNOWN):
                    distance.append(abs(_x-x)+abs(_y-y))
        distance.sort()
        return sum(distance[:k+1])


def get_features(state, action):
    state_copy = copy.deepcopy(state)

    features = util.Counter()

    # features["bias"] = 0.1
    # features["num_steps"] = 1.0 / (len(self.history)+1.0)
    # features["action_type"] = 1.0

    # next_state is after predict
    next_state = virtual_sense(state_copy, action)
    features["to_explored"] = (next_state.num_explored - state_copy.num_explored) / 20.0
    # features["num_unexplored_inverse"] = 1.0 / (301.0 - next_state.num_explored)  # 301 is set to avoid devide by zero
    # features["num_unexplored_normalized"] = next_state.num_explored/300.0
    # features["closest_unexplored"] = 1.0 / self.closest_unexplored(next_state, 10)  # trap
    if features["to_explored"] > 0:
        features["closest_unexplored_inverse"] = 1.0
    else:
        closest_unexplored = dijkstra(next_state)
        features["closest_unexplored_inverse"] = 1.0 / (closest_unexplored)
    # features["closest_unexplored"] = closest_unexplored / 5.0 # don't use this
    # features["x"] = state.x / 20.0
    # features["y"] = state.y / 15.0

    # encourage right hugging
    # features["right_hugging"] = 0
    # if action == Actions.FORWARD:
    #     features["right_hugging"] = int(state.history[-1:] == [Actions.TURN_RIGHT])
    # features["u_turn"] = 0
    # features["back"] = 0
    # if action == Actions.U_TURN:
    #     features["u_turn"] = 1
    # if action == Actions.TURN_LEFT:
    #     if state.history[-1:] == [Actions.TURN_LEFT]:
    #         features["u_turn"] = 1
    #     if state.history[-1:] == [Actions.TURN_RIGHT]:
    #         features["back"] = 1
    # if action == Actions.TURN_RIGHT:
    #     if state.history[-1:] == [Actions.TURN_RIGHT]:
    #         features["u_turn"] = 1
    #     if state.history[-1:] == [Actions.TURN_LEFT]:
    #         features["back"] = 1
    print(state.x, state.y, state.direction, action, features)
    return features