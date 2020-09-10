from constants import Directions, RelativeDirections, Actions, CellState
from utils import is_within_grid, predict_unexplored_area

###########################
# SENSOR AND ROBOT
###########################


class Robot:
    """
    Robot occupies 3*3 cells
    """
    def __init__(self, x, y, direction, sensors, real=False):
        self.x = x
        self.y = y
        self.direction = direction
        self.sensors = sensors # list of sensors
        self.real = real

    def get_all_sensed_cells_state_with_sensor_value(self, x=None, y=None, direction=None):
        # used after actual action is taken, before this, sense() must update sensor_value
        if not x and not y and not direction:
            x = self.x
            y = self.y
            direction = self.direction
        cells = {}
        for sensor in self.sensors:
            cells.update(sensor.get_cells_state_with_sensor_value(x, y, direction))
        return cells

    def get_all_sensable_cell(self, x=None, y=None, direction=None):
        if not x and not y and not direction:
            x = self.x
            y = self.y
            direction = self.direction
        cells = []
        for sensor in self.sensors:
            cells.extend(sensor.get_sensable_cells(x, y, direction))
        return cells

    def move_forward_valid_with_sensor_value(self, x=None, y=None, direction=None):
        if not x and not y and not direction:
            x = self.x
            y = self.y
            direction = self.direction
        if direction == Directions.NORTH:
            front_cells = [(x + 2, y - 1), (x + 2, y), (x + 2, y + 1)]
        elif direction == Directions.EAST:
            front_cells = [(x + 1, y + 2), (x, y + 2), (x - 1, y + 2)]
        elif direction == Directions.SOUTH:
            front_cells = [(x - 2, y - 1), (x - 2, y), (x - 2, y + 1)]
        elif direction == Directions.WEST:
            front_cells = [(x + 1, y - 2), (x, y - 2), (x - 1, y - 2)]
        else:
            raise ValueError("Directions doesn't exist")
        all_sensed_cells_state = self.get_all_sensed_cells_state_with_sensor_value(x, y, direction)
        for front_cell in front_cells:
            try:
                if all_sensed_cells_state[front_cell] == CellState.OBSTACLE:
                    return False
            except KeyError:
                raise RuntimeError("Front cell is not sensed") # shouldn't happen since we place 3 SRsensor in front
        return True

    def get_valid_movements(self, x=None, y=None, direction=None):
        if not x and not y and not direction:
            x = self.x
            y = self.y
            direction = self.direction
        movements = [Actions.TURN_RIGHT]  # this make sure if Turn right and forward equals, choose turn right
        if self.move_forward_valid_with_sensor_value(x, y, direction):
            movements.append(Actions.FORWARD)
        movements.extend([Actions.U_TURN, Actions.TURN_LEFT])
        # print(movements)
        return movements

    def reset_robot(self, state):
        self.x = state.x
        self.y = state.y
        self.direction = state.direction

    def set_robot(self, x, y, direction):
        self.x = x
        self.y = y
        self.direction = direction

    def next_state(self, action, x=None, y=None, direction=None):
        if not x and not y and not direction:
            x = self.x
            y = self.y
            direction = self.direction
        if action == Actions.TURN_LEFT:
            direction = Directions((direction.value - 1) % len(Directions))
        elif action == Actions.TURN_RIGHT:
            direction = Directions((direction.value + 1) % len(Directions))
        elif action == Actions.U_TURN:
            direction = Directions((direction.value - 2) % len(Directions))
        elif action == Actions.FORWARD:
            if direction == Directions.NORTH:
                x = x + 1
            elif direction == Directions.EAST:
                y = y + 1
            elif direction == Directions.WEST:
                y = y - 1
            elif direction == Directions.SOUTH:
                x = x - 1
            else:
                raise ValueError("Directions doesn't exist")
        else:
            raise ValueError("Actions doesn't exist")
        return x, y, direction



class Sensor:
    def __init__(self, lrange, urange, relative_x, relative_y, relative_direction):
        self.lrange = lrange
        self.urange = urange  # inclusive
        self.relative_x = relative_x
        self.relative_y = relative_y
        self.relative_direction = relative_direction
        self.sensor_value = -1

    def get_relative_position(self):
        return self.relative_x, self.relative_y

    def get_relative_direction(self):
        return self.relative_direction

    def get_direction(self, robot_direction):
        # Directions class's order cannot be changed
        if self.relative_direction == RelativeDirections.FRONT:
            return robot_direction
        elif self.relative_direction == RelativeDirections.LEFT:
            return Directions((robot_direction.value - 1) % len(Directions))
        elif self.relative_direction == RelativeDirections.RIGHT:
            return Directions((robot_direction.value + 1) % len(Directions))
        elif self.relative_direction == RelativeDirections.BACK:
            return Directions((robot_direction.value - 2) % len(Directions))
        else:
            raise ValueError("RelativeDirections doesn't exist")

    def get_position(self, robot_x, robot_y, robot_direction):
        if robot_direction == Directions.NORTH:
            return robot_x+self.relative_x, robot_y+self.relative_y
        elif robot_direction == Directions.EAST:
            return robot_x-self.relative_y, robot_y+self.relative_x
        elif robot_direction == Directions.WEST:
            return robot_x+self.relative_y, robot_y-self.relative_x
        elif robot_direction == Directions.SOUTH:
            return robot_x-self.relative_x, robot_y-self.relative_y
        else:
            raise ValueError("Directions doesn't exist")

    def get_sensable_cells(self, robot_x, robot_y, robot_direction):
        # might produce non-existing position
        x,y = self.get_position(robot_x,robot_y, robot_direction)
        direction = self.get_direction(robot_direction)
        area = []
        for i in range(self.lrange, self.urange+1):
            if direction == Directions.NORTH:
                area.append((x+i,y))
            elif direction == Directions.EAST:
                area.append((x,y+i))
            elif direction == Directions.SOUTH:
                area.append((x-i,y))
            elif direction == Directions.WEST:
                area.append((x, y - i))
            else:
                raise ValueError("Directions doesn't exist")
        return area

    def get_all_cells(self, robot_x, robot_y, robot_direction):
        # from robot to upper range
        # might produce non-existing position
        x, y = self.get_position(robot_x, robot_y, robot_direction)
        direction = self.get_direction(robot_direction)
        area = []
        for i in range(1, self.urange + 1):
            if direction == Directions.NORTH:
                area.append((x + i, y))
            elif direction == Directions.EAST:
                area.append((x, y + i))
            elif direction == Directions.SOUTH:
                area.append((x - i, y))
            elif direction == Directions.WEST:
                area.append((x, y - i))
            else:
                raise ValueError("Directions doesn't exist")
        return area

    def set_sensor_value(self, sensor_value):
        self.sensor_value = sensor_value

    def get_cells_state_with_sensor_value(self, robot_x=None, robot_y=None, robot_direction=None):
        # if sensor_value = 1, meaning the block next to robot is a obstacle
        if self.sensor_value < self.lrange:
            return {}
        else:
            cells = self.get_sensable_cells(robot_x, robot_y, robot_direction)
            cell_states = {}
            if self.sensor_value <= self.urange:
                cell_states[cells[self.sensor_value-self.lrange]] = CellState.OBSTACLE
                for i in range(self.lrange, self.sensor_value):
                    cell_states[cells[i-self.lrange]] = CellState.FREE
            else:
                for i in range(self.lrange, self.urange+1):
                    cell_states[cells[i-self.lrange]] = CellState.FREE
            return cell_states

    def get_cells_state_with_explored_grid(self, robot_x, robot_y, robot_direction, state):
        # if encounter obstacle, the further cells cannot be sensed
        all_cells = self.get_all_cells(robot_x, robot_y, robot_direction)
        sensable_cells = self.get_sensable_cells(robot_x, robot_y, robot_direction)
        cell_states = {}
        for cell in all_cells:
            x, y = cell
            if is_within_grid(state.explored_grid, x, y):
                if state.explored_grid[x][y].is_same(CellState.UNKNOWN):
                    if (x,y) not in sensable_cells:
                        break
                    # predict UNKNOWN
                    predict_unexplored_area(state.explored_grid, x, y)
                if state.explored_grid[x][y].is_same(CellState.OBSTACLE):
                    cell_states[(x,y)] = CellState.OBSTACLE
                    break
                elif state.explored_grid[x][y].is_same(CellState.FREE):
                    cell_states[(x, y)] = CellState.FREE
                else:
                    raise "Invalid CellState"
        return cell_states




def get_initial_robot(x, y, direction):
    """

               ^   ^   ^
               ^   ^   ^
          < < [X] [X] [X] > >
              [X] [X] [X]
      < <     [X] [X] [X]


    #           ^   ^   ^
    #          SR  SR  SR
    #     < SR [X] [X] [X] SR >
    #          [X] [X] [X]
    #< LR      [X] [X] [X]

    """
    sr_front_left = Sensor(1, 2, 1, -1, RelativeDirections.FRONT)
    sr_front_right = Sensor(1, 2, 1, 1, RelativeDirections.FRONT)
    sr_front_center = Sensor(1, 2, 1, 0, RelativeDirections.FRONT)
    sr_left = Sensor(1, 2, 1, -1, RelativeDirections.LEFT)
    sr_right = Sensor(1, 2, 1, 1, RelativeDirections.RIGHT)
    lr_left = Sensor(1, 4, -1, -1, RelativeDirections.LEFT)
    sensors = [sr_front_left, sr_front_center, sr_front_right, sr_left, sr_right, lr_left]
    # sensors = [sr_front_left, sr_front_center, sr_front_right, sr_left, sr_right]
    robot = Robot(x, y, direction, sensors)
    return robot


#
#
# def test_get_cells_state_with_explored_grid()
#
