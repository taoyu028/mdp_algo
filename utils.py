from constants import CellState
import random
from grid import Cell, Grid


def flip_coin(p):
    r = random.random()
    return r < p


def is_within_grid(grid, x, y):
    if x < 0 or x >= grid.height: return False
    if y < 0 or y >= grid.width: return False
    return True


def print_grid(grid):
    for x in range(grid.height-1, -1, -1):
        for y in range(grid.width):
            if grid[x][y].is_same(CellState.UNKNOWN):
                print "?",
            elif grid[x][y].is_same(CellState.OBSTACLE):
                print "#",
            elif grid[x][y].is_same(CellState.FREE):
                print ".",
        print
    print

###########################
# GRID PREDICTION
###########################
PREDICT_DISTANCE_TO_WALL = 4


def is_next_to_obstacle(explored_grid, x, y):
    """
    Notice that the difference between explored_grid and grid is that
    explored_grid can have CellState.UNKNOWN
    """
    dx = [1, 0, -1, 0]
    dy = [0, 1, 0, -1]
    for _dx in dx:
        for _dy in dy:
            _x = x + _dx
            _y = y + _dy
            if is_within_grid(explored_grid, _x, _y):
                if explored_grid[_x][_y].is_same(CellState.OBSTACLE):
                    return True
    return False


def is_next_to_wall(explored_grid, x, y, distance=PREDICT_DISTANCE_TO_WALL):
    if not is_within_grid(explored_grid, x, y):
        return None
    if explored_grid.width - y <= distance:
        return True
    if y < distance:
        return True
    if explored_grid.height - x <= distance:
        return True
    if x < distance:
        return True


def predict_unexplored_area(explored_grid, x, y, distance=PREDICT_DISTANCE_TO_WALL):
    """
    This function is really important, the accuracy of prediction decides the
    accuracy of qvalue

    Explored_grid will be modified directly and should be save for later use
    by other sensors
    """
    if not is_within_grid(explored_grid, x, y):
        return
    prob = 0.1 # default rate of OBSTACLE
    if is_next_to_obstacle(explored_grid, x, y):
        prob += 0.25
    if is_next_to_wall(explored_grid, x, y, distance):
        prob += 0.25
    if flip_coin(prob):
        explored_grid[x][y].set_state(CellState.OBSTACLE)
    else:
        explored_grid[x][y].set_state(CellState.FREE)



###########################
# TEST
###########################
# def test_print_grid():
#     """
#     PASS
#     """
#     data = [[Cell(CellState, CellState.UNKNOWN) for i in range(4)] for i in range(5)]
#     data[0][1].set_state(CellState.OBSTACLE)
#     data[0][2].set_state(CellState.FREE)
#     data[1][1].set_state(CellState.FREE)
#     grid = Grid(4, 5, data)
#     print_grid(grid)
#
#
# def test_predict_unexplored_area():
#     """
#     PASS
#     """
#     data = [[Cell(CellState, CellState.UNKNOWN) for i in range(4)] for i in range(5)]
#     data[0][1].set_state(CellState.OBSTACLE)
#     data[0][2].set_state(CellState.FREE)
#     data[1][1].set_state(CellState.FREE)
#     grid = Grid(4, 5, data)
#     print_grid(grid)
#     print
#     predict_unexplored_area(grid,0,0)
#     print_grid(grid)
#     print
#     predict_unexplored_area(grid, 3, 2, 1)
#     print_grid(grid)
#     print
