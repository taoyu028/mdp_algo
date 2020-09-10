import util
from graphicsUtils import *
from constants import CellState


class GraphicsGridworldDisplay:

    def __init__(self, gridworld, size=35, speed=1.0):
        self.gridworld = gridworld
        self.size = size
        self.speed = speed

    def start(self):
        setup(self.gridworld, size=self.size)

    def pause(self):
        wait_for_keys()

    def displayValues(self, agent, currentState = None, message = 'Agent Values'):
        # TODO: need to display current state
        values = util.Counter()
        policy = {}
        # states = self.gridworld.getStates()
        # TODO: values and policy
        # for state in states:
        #     values[state] = agent.getValue(state)
        #     policy[state] = agent.getPolicy(state)
        currentState = currentState.x, currentState.y, currentState.direction
        drawValues(self.gridworld, currentState, message)
        sleep(1.0 / self.speed)

BACKGROUND_COLOR = formatColor(0,0,0)
EDGE_COLOR = formatColor(1,1,1)
OBSTACLE_COLOR = formatColor(0.5,0.5,0.5)
TEXT_COLOR = formatColor(1,1,1)
MUTED_TEXT_COLOR = formatColor(0.7,0.7,0.7)
LOCATION_COLOR = formatColor(0,0,1)
DIRECTION_COLOR = formatColor(1, 0, 0)

WINDOW_SIZE = -1
GRID_SIZE = -1
GRID_HEIGHT = -1
GRID_WIDTH = -1
MARGIN = -1


def setup(gridworld, title = "Gridworld Display", size = 20):
    global GRID_SIZE, MARGIN, SCREEN_WIDTH, SCREEN_HEIGHT, GRID_HEIGHT, GRID_WIDTH
    grid = gridworld.grid
    WINDOW_SIZE = size
    GRID_SIZE = size
    GRID_HEIGHT = grid.height
    GRID_WIDTH = grid.width
    MARGIN = GRID_SIZE * 0.75
    screen_width = (grid.width - 1) * GRID_SIZE + MARGIN * 2
    screen_height = (grid.height - 0.5) * GRID_SIZE + MARGIN * 2

    begin_graphics(screen_width,
                   screen_height,
                   BACKGROUND_COLOR, title=title)


def drawValues(gridworld, currentState = None, message = 'State Values'):
    grid = gridworld.grid
    explored_grid = gridworld.state.explored_grid
    blank()
    # TODO: value change to number of visited
    # valueList = [values[state] for state in gridworld.getStates()] + [0.0]
    valueList = [0, 1]
    minValue = min(valueList)
    maxValue = max(valueList)
    for x in range(grid.height):
        for y in range(grid.width):
            state = (x, y)
            gridType = grid[x][y]
            # TODO: logic of isExit
            # isExit = (str(gridType) != gridType)
            isExit = False
            isCurrent = ((currentState[0], currentState[1]) == state)
            value = explored_grid[x][y]
            if value.is_same(CellState.UNKNOWN):
                value = 0
            else:
                value = 1
            valString = '%d' % value
            if gridType.is_same(CellState.OBSTACLE):
                drawSquare(x, y, 0, 0, 0, valString, True, False, isCurrent)
            else:

                # action = None
                # if policy != None and state in policy:
                #     action = policy[state]
                #     actions = gridworld.getPossibleActions(state)
                # if action not in actions and 'exit' in actions:
                #     action = 'exit'

                drawSquare(x, y, value, minValue, maxValue, valString,  False, isExit, isCurrent, currentState[2])
    # pos = to_screen(((grid.width - 1.0) / 2.0, - 0.8))
    # text( pos, TEXT_COLOR, message, "Courier", -32, "bold", "c")


def blank():
    clear_screen()


def drawSquare(x, y, val, min, max, valStr, isObstacle, isTerminal, isCurrent, direction=None):

    square_color = getColor(val, min, max)

    if isObstacle:
        square_color = OBSTACLE_COLOR

    (screen_x, screen_y) = to_screen((x, y))
    square( (screen_x, screen_y),
                   0.5* GRID_SIZE,
                   color = square_color,
                   filled = 1,
                   width = 1)
    square( (screen_x, screen_y),
                   0.5* GRID_SIZE,
                   color = EDGE_COLOR,
                   filled = 0,
                   width = 3)
    if isTerminal and not isObstacle:
        square( (screen_x, screen_y),
                     0.4* GRID_SIZE,
                     color = EDGE_COLOR,
                     filled = 0,
                     width = 2)

    #
    # if action == 'north':
    #     polygon( [(screen_x, screen_y - 0.45*GRID_SIZE), (screen_x+0.05*GRID_SIZE, screen_y-0.40*GRID_SIZE), (screen_x-0.05*GRID_SIZE, screen_y-0.40*GRID_SIZE)], EDGE_COLOR, filled = 1, smoothed = False)
    # if action == 'south':
    #     polygon( [(screen_x, screen_y + 0.45*GRID_SIZE), (screen_x+0.05*GRID_SIZE, screen_y+0.40*GRID_SIZE), (screen_x-0.05*GRID_SIZE, screen_y+0.40*GRID_SIZE)], EDGE_COLOR, filled = 1, smoothed = False)
    # if action == 'west':
    #     polygon( [(screen_x-0.45*GRID_SIZE, screen_y), (screen_x-0.4*GRID_SIZE, screen_y+0.05*GRID_SIZE), (screen_x-0.4*GRID_SIZE, screen_y-0.05*GRID_SIZE)], EDGE_COLOR, filled = 1, smoothed = False)
    # if action == 'east':
    #     polygon( [(screen_x+0.45*GRID_SIZE, screen_y), (screen_x+0.4*GRID_SIZE, screen_y+0.05*GRID_SIZE), (screen_x+0.4*GRID_SIZE, screen_y-0.05*GRID_SIZE)], EDGE_COLOR, filled = 1, smoothed = False)


    text_color = TEXT_COLOR

    if not isObstacle and isCurrent:
        circle( (screen_x, screen_y), 0.2*GRID_SIZE, outlineColor=LOCATION_COLOR, fillColor=LOCATION_COLOR )
        chord((screen_x, screen_y), 0.2*GRID_SIZE, outlineColor=DIRECTION_COLOR, fillColor=DIRECTION_COLOR, direction=direction)

    text( (screen_x, screen_y), text_color, valStr, "Courier", -20, "normal", "c")


def getColor(val, minVal, max):
    r, g = 0.0, 0.0
    if val < 0 and minVal < 0:
        r = val * 0.65 / minVal
    if val > 0 and max > 0:
        g = val * 0.65 / max
    return formatColor(r,g,0.0)


def square(pos, size, color, filled, width):
    x, y = pos
    dx, dy = size, size
    return polygon([(x - dx, y - dy), (x - dx, y + dy), (x + dx, y + dy), (x + dx, y - dy)], outlineColor=color, fillColor=color, filled=filled, width=width, smoothed=False)


def to_screen(point):
    ( gamex, gamey ) = point
    x = MARGIN + gamey*GRID_SIZE
    y = (GRID_HEIGHT - gamex - 1)*GRID_SIZE + MARGIN
    return ( x, y )


def to_grid(point):
    (x, y) = point
    x = int ((y - MARGIN + GRID_SIZE * 0.5) / GRID_SIZE)
    y = int ((x - MARGIN + GRID_SIZE * 0.5) / GRID_SIZE)
    print point, "-->", (x, y)
    return (x, y)
