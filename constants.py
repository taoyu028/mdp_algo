from enum import Enum


###########################
# SENSOR AND ROBOT
###########################
class Directions(Enum):
    NORTH = 0
    EAST = 1
    SOUTH = 2
    WEST = 3


class RelativeDirections(Enum):
    FRONT = 0
    LEFT = 1
    RIGHT = 2
    BACK = 3  # no benefit for putting sensor at the back


class Actions(Enum):
    FORWARD = 0
    TURN_LEFT = 1
    TURN_RIGHT = 2
    U_TURN = 3


###########################
# GRID AND CELL
###########################
class CellState(Enum):
    FREE = 0
    OBSTACLE = 1
    UNKNOWN = 2




