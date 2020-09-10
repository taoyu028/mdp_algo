from constants import CellState


###########################
# GRID AND CELL
###########################


GRID_HEIGHT = 20
GRID_WIDTH = 15


class Cell:
    def __init__(self, enum_type, default_enum_state=CellState.UNKNOWN):
        self.enum_type = enum_type
        self.num_state = len(enum_type)
        self.default_enum_state = default_enum_state
        self.data = []
        self.set_state(default_enum_state)
        self.current_state = default_enum_state

    def __eq__(self, other):
        raise "Don't use equal directly"

    def clear_state(self):
        self.data = [0 for i in range(self.num_state)]
        self.current_state = None

    def reset_state(self):
        self.clear_state()
        self.data[self.default_enum_state.value] = 1
        self.current_state = self.default_enum_state

    def set_state(self, enum_state):
        if enum_state is None:
            self.clear_state()
            return
        if not isinstance(enum_state, self.enum_type):
            raise ValueError("Enum_state doesn't exist")
        if enum_state.value >= len(self.enum_type):
            raise IndexError("Index out of bound")
        self.clear_state()
        self.data[enum_state.value] = 1
        self.current_state = enum_state

    def get_state(self):
        return self.current_state

    def is_same(self, enum_type):
        return self.current_state == enum_type

    def __str__(self):
        if not self.current_state:
            return "-1"
        return str(self.current_state.value)


class Grid:
    """
    A 2-dimensional array of Cell.  Data is accessed via grid[x][y] where (x,y)
    are cartesian coordinates with x horizontal, y vertical and the origin (0,0)
    in the bottom left corner.

    The __str__ method constructs an MDF string.
    """
    def __init__(self, width, height, data=None):
        self.width = width
        self.height = height
        self.data = data

    def __getitem__(self, i):
        return self.data[i]

    def __eq__(self, other):
        if other == None: return False
        return self.data == other.data

    def __hash__(self):
        return hash(self.data)

    def is_allowed(self, x, y):
        if x < 0 or x >= self.height: return False
        if y < 0 or y >= self.width: return False
        return True

    def is_surround_wall_virtual_wall(self, x, y):
        # including virtual wall of wall
        if x == 0 or x == self.height-1: return True
        if y == 0 or y == self.width-1: return True
        return False

    def _getMapDescriptor(self):
        string_a = ""  # isExplored string
        string_a_bin = "11"
        string_b = ""  # isObstacle
        string_b_bin = ""
        for x in range(self.height):
            for y in range(self.width):
                if self.data[x][y] == CellState.UNKNOWN:
                    string_a_bin += "0"
                elif self.data[x][y] == CellState.FREE:
                    string_b_bin += "0"
                    string_a_bin += "1"
                elif self.data[x][y] == CellState.OBSTACLE:
                    string_b_bin += "1"
                    string_a_bin += "1"
                else:
                    raise TypeError("Cannot perform _getMapDescriptor")
                if len(string_a_bin) == 4:
                    string_a += format(int(string_a_bin, 2), 'x')
                    string_a_bin = ""
                if len(string_b_bin) == 4:
                    string_b += format(int(string_b_bin, 2), 'x')
                    string_b_bin = ""
        string_a_bin += "11"
        string_a += format(int(string_a_bin, 2), 'x')
        string_b += format(int('{:0<04}'.format(string_b_bin), 2), 'x')
        return string_a + " " + string_b

    def __str__(self):
        try:
            return str(self._getMapDescriptor())
        except TypeError:
            return str(self.data)

    def is_virtual_wall(self, x, y):
        if x==0 or x == self.height-1: return True
        if y==0 or y == self.width-1: return True
        x_move = [1,1,1,0,-1,-1,-1,0]
        y_move = [-1,0,1,1,1,0,-1,-1]
        for i in range(8):
            _x = x+x_move[i]
            _y = y+y_move[i]
            if not self.is_allowed(_x, _y):
                continue
            else:
                if self.data[_x][_y].is_same(CellState.OBSTACLE):
                    return True
                elif self.data[_x][_y].is_same(CellState.FREE):
                    continue
                elif self.data[_x][_y].is_same(CellState.UNKNOWN):
                    return False
        return False


def get_grid_from_file(file_path):
    # following Map Descriptor Format
    import os
    if os.path.exists(file_path):
        with open(file_path, "r") as f:
            lines = f.read().splitlines()
            height = len(lines)
            width = len(lines[0])
            grid = [[Cell(CellState) for y in range(width)] for x in range(height)]
            for x in range(height):
                for y in range(width):
                    if lines[x][y] == "0":
                        grid[height-x-1][y].set_state(CellState.FREE)
                    else:
                        grid[height-x-1][y].set_state(CellState.OBSTACLE)
        return Grid(width, height, grid)
    else:
        raise ValueError("File path doesn't exist")


def get_initial_explored_grid():
    grid = [[Cell(CellState, CellState.UNKNOWN) for y in range(GRID_WIDTH)] for x in range(GRID_HEIGHT)]
    # set start zone
    for row in range(3):
        for col in range(3):
            grid[row][col].set_state(CellState.FREE)
    # # set goal zone
    # for row in range(17, 20):
    #     for col in range(12, 15):
    #         grid[row][col].set_state(CellState.FREE)
    return Grid(GRID_WIDTH, GRID_HEIGHT, grid)


if __name__ == '__main__':

    # deep copy works!
    grid = get_grid_from_file("/Users/chentaoyu/Desktop/year4sem1/CZ3004/project/mine/mdp_algo/grids/exp1.txt")
    print (type(grid))
    import copy
    grid_copy = copy.deepcopy(grid)
    print(grid_copy[0][11])
    print(grid[0][11])
    grid.data[0][11].set_state(CellState.FREE)
    print(grid_copy[0][11])
    print(grid[0][11])