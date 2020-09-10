from enum import Enum
import mdp
import util
from constants import Directions, CellState, Actions
from state import State
from grid import get_initial_explored_grid, get_grid_from_file
from robot import get_initial_robot
import copy
from utils import print_grid


class Gridworld(mdp.MarkovDecisionProcess):
    """
      Gridworld
    """

    def __init__(self, real_grid):
        self.grid = real_grid
        self.initial_state = State(x=1, y=1, direction=Directions.EAST, grid=self.grid)
        self.robot = get_initial_robot(self.initial_state.x, self.initial_state.y, self.initial_state.direction)
        self.state = None
        self.reset()

        # parameters
        self.livingReward = -1.0

    def reset(self):
        self.state = copy.deepcopy(self.initial_state)
        self.state.explored_grid = get_initial_explored_grid()
        self.robot.reset_robot(self.initial_state)
        self.state.robot = self.robot

        self.initial_sense(self.state)
        self.check_num_explored(self.state)

    def check_num_explored(self, state):
        num = 0
        for x in range(state.explored_grid.height):
            for y in range(state.explored_grid.width):
                if state.explored_grid[x][y].is_same(CellState.UNKNOWN):
                    continue
                elif state.explored_grid[x][y].is_same(CellState.FREE) \
                        or state.explored_grid[x][y].is_same(CellState.OBSTACLE):
                    num += 1
        if state.num_explored is None:
            state.num_explored = num
        else:
            if state.num_explored != num:
                raise "Inconsistent number of explored cell"

    def initial_sense(self, state):
        x = state.x
        y = state.y
        direction = state.direction
        # update robot and sensors
        self.robot.set_robot(x, y, direction)
        for sensor in self.robot.sensors:
            all_area = sensor.get_all_cells(self.robot.x, self.robot.y, self.robot.direction)
            sensor_value = 1
            for cell in all_area:
                _x, _y = cell
                if not self.__isAllowed(_x, _y):
                    break
                if self.grid[_x][_y].is_same(CellState.FREE):
                    sensor_value += 1
                elif self.grid[_x][_y].is_same(CellState.OBSTACLE):
                    break
            sensor.set_sensor_value(sensor_value)
        # update explored_grid
        sensed_cells_state = self.robot.get_all_sensed_cells_state_with_sensor_value()
        for sensed_cell in sensed_cells_state.keys():
            x, y = sensed_cell
            if self.__isAllowed(x, y):
                if state.explored_grid[x][y].is_same(CellState.UNKNOWN):
                    state.explored_grid[x][y].set_state(sensed_cells_state[sensed_cell])
                elif not state.explored_grid[x][y].is_same(sensed_cells_state[sensed_cell]):
                    print(x, y, state.explored_grid[x][y].get_state())
                    print(sensed_cells_state[sensed_cell])
                    raise "Serious error!!!!"

    def sense(self, action):
        # change self.state
        self.state.history.append(action)
        x, y, direction = self.robot.next_state(action, self.state.x, self.state.y, self.state.direction)
        self.state.x = x
        self.state.y = y
        self.state.direction = direction
        # update robot and sensors
        self.robot.set_robot(x, y, direction)
        for sensor in self.robot.sensors:
            all_area = sensor.get_all_cells(self.robot.x, self.robot.y, self.robot.direction)
            sensor_value = 1
            for cell in all_area:
                _x, _y = cell
                if not self.__isAllowed(_x, _y):
                    break
                if self.grid[_x][_y].is_same(CellState.FREE):
                    sensor_value += 1
                elif self.grid[_x][_y].is_same(CellState.OBSTACLE):
                    break
            sensor.set_sensor_value(sensor_value)
        # update explored_grid
        sensed_cells_state = self.robot.get_all_sensed_cells_state_with_sensor_value()
        for sensed_cell in sensed_cells_state.keys():
            x, y = sensed_cell
            if self.__isAllowed(x, y):
                if self.state.explored_grid[x][y].is_same(CellState.UNKNOWN):
                    self.state.explored_grid[x][y].set_state(sensed_cells_state[sensed_cell])
                    self.state.num_explored += 1
                elif not self.state.explored_grid[x][y].is_same(sensed_cells_state[sensed_cell]):
                    print(x, y, self.state.explored_grid[x][y].get_state())
                    print(sensed_cells_state[sensed_cell])
                    raise "Serious error!!!!"
        if self.state.num_explored == 300:
            self.state.is_terminal = True
        # print(self.state.num_explored)

    def setLivingReward(self, reward):
        """
        The (negative) reward for exiting "normal" states.

        Note that in the R+N text, this reward is on entering
        a state and therefore is not clearly part of the state's
        future rewards.
        """
        self.livingReward = reward

    def getPossibleActions(self, state):
        """
        Returns list of valid actions for 'state'.

        Note that you can request moves into walls and
        that "exit" states transition to the terminal
        state under the special action "done".
        """
        if state.is_terminal:
            return ()
        x = state.x
        y = state.y
        direction = state.direction
        return self.robot.get_valid_movements(x, y, direction)

    def getStates(self):
        """
        Return list of all states.
        """
        # The true terminal state.
        states = []
        for x in range(self.grid.height):
            for y in range(self.grid.width):
                if self.grid[x][y].is_same(CellState.OBSTACLE):
                    state = State(x, y, None)
                    states.append(state)
        return states

    def getReward(self, state, action, next_state):
        """
        Get reward for state, action, nextState transition.

        Note that the reward depends only on the state being
        departed (as in the R+N book examples, which more or
        less use this convention).
        """
        # TODO:
        if state.is_terminal:
            return 0.0

        reward = 0
        # for i in range(state.num_explored+1, next_state.num_explored+1):
        #     reward += 2.0 * pow(0.99, i)

        reward += (next_state.num_explored - state.num_explored)
        if action == Actions.U_TURN:
            reward -= 10
        # reward -= pow(1.005, len(state.history))
        # encourage right hugging
        # if reward != 1 and action == Actions.U_TURN:
        #     reward -= 5
        # if action == Actions.FORWARD:
        #     reward += 1
        #     if state.history[-1:] == [Actions.TURN_RIGHT]:
        #         reward += 200
        # if action == Actions.TURN_RIGHT:
        #     if state.history[-1:] == [Actions.TURN_RIGHT]:
        #         reward -= 5
        #     if state.history[-1:] == [Actions.TURN_LEFT]:
        #         reward -= 50
        # if action == Actions.TURN_LEFT:
        #     if state.history[-1:] == [Actions.TURN_LEFT]:
        #         reward -= 5
        #     if state.history[-1:] == [Actions.TURN_RIGHT]:
        #         reward -= 50
        # time
        return reward

    def getStartState(self):
        """
        Start state is at the bottom left corner of grid, the center
        of start zone
        :return:
        """
        return self.initial_state

    def isTerminal(self, state):
        """
        Only the TERMINAL_STATE state is *actually* a terminal state.
        The other "exit" states are technically non-terminals with
        a single action "exit" which leads to the true terminal state.
        This convention is to make the grids line up with the examples
        in the R+N textbook.
        """
        return state.is_terminal

    def __isAllowed(self, x, y):
        if x < 0 or x >= self.grid.height: return False
        if y < 0 or y >= self.grid.width: return False
        return True

import environment
import random


class GridworldEnvironment(environment.Environment):

    def __init__(self, gridWorld):
        self.gridWorld = gridWorld
        self.reset()

    def getCurrentState(self):
        return self.gridWorld.state

    def getPossibleActions(self, state):
        return self.gridWorld.getPossibleActions(state)

    def doAction(self, action):
        self.previous_state = copy.deepcopy(self.getCurrentState())
        self.gridWorld.sense(action)
        reward = self.gridWorld.getReward(self.previous_state, action, self.getCurrentState())
        return (self.getCurrentState(), reward)

    def reset(self):
        """
        reset start state and explored grid
        """
        self.gridWorld.reset()


def print_string(x): print (x)


def runEpisode(agent, environment, discount, decision, display, message, pause, episode, train=False):
    returns = 0
    totalDiscount = 1.0
    environment.reset()
    if 'startEpisode' in dir(agent): agent.startEpisode()
    message("BEGINNING EPISODE: "+str(episode)+"\n")
    while True:

        # DISPLAY CURRENT STATE
        state = environment.getCurrentState()
        state_copy = copy.deepcopy(state)
        display(state)
        pause()

        # END IF IN A TERMINAL STATE
        actions = environment.getPossibleActions(state)
        if len(actions) == 0:
            message("EPISODE "+str(episode)+" COMPLETE: TOOK "+str(len(state.history))+"STEPS; RETURN WAS "+str(returns)+"\n")
            message(str(state.history))
            message(str(len(state.history)))
            return returns

        # GET ACTION (USUALLY FROM AGENT)
        action = decision(state)
        if action == None:
            raise 'Error: Agent returned None action'

        # EXECUTE ACTION
        nextState, reward = environment.doAction(action)
        message("Started in state: "+str(state_copy.x)+str(state_copy.y)+str(state_copy.direction)+str(state_copy.num_explored)+" "+str(len(state_copy.history))+
                "\nTook action: "+str(action)+
                "\nEnded in state: "+str(nextState.x)+str(nextState.y)+str(nextState.direction)+str(nextState.num_explored)+" "+str(len(nextState.history))+
                "\nGot reward: "+str(reward)+"\n")
        # UPDATE LEARNER
        # print_grid(state_copy.explored_grid)
        # print_grid(nextState.explored_grid)

        if 'observeTransition' in dir(agent) and not nextState.is_terminal and train:
            agent.observeTransition(state_copy, action, nextState, reward)
        print(agent.weights)
        print ("############################################")
        print ("############################################\n")

        returns += reward * totalDiscount
        totalDiscount *= discount

# grid = get_grid_from_file("/Users/chentaoyu/Desktop/year4sem1/CZ3004/project/mine/mdp_algo/grids/exp1.txt")
# mdp = Gridworld(grid)
# env = GridworldEnvironment(mdp)
# from display import GraphicsGridworldDisplay
# display = GraphicsGridworldDisplay(mdp)
# display.start()
# mdp.sense(mdp.initial_state)
# display.displayValues(None, env.getCurrentState())
# env.doAction(Actions.FOWARD)
# display.displayValues(None, env.getCurrentState())
# print()


if __name__ == '__main__':

    _discount = 0.9
    _grid_size = 35
    _alpha = 0.5  # learning rate

    _epsilon = 0.3  # exploration rate
    _episodes = 1
    _training_episodes = 0
    _speed = 4

    ###########################
    # GET THE GRIDWORLD
    ###########################

    grid = get_grid_from_file("/Users/chentaoyu/Desktop/year4sem1/CZ3004/project/mdp_algo/grids/not_reachable.txt")
    mdp = Gridworld(grid)
    env = GridworldEnvironment(mdp)

    ###########################
    # GET THE DISPLAY ADAPTER
    ###########################
    from display import GraphicsGridworldDisplay
    display = GraphicsGridworldDisplay(mdp, size=_grid_size, speed=_speed)
    display.start()

    ###########################
    # GET THE AGENT
    ###########################
    import qlearningAgents
    actionFn = lambda state: mdp.getPossibleActions(state)
    qLearnOpts = {'gamma': _discount,
                  'alpha': _alpha,
                  'epsilon': _epsilon,
                  'actionFn': actionFn}
    a = qlearningAgents.QLearningAgent(**qLearnOpts)

    ###########################
    # RUN EPISODES
    ###########################
    graphic_display = lambda state: display.displayValues(a, state)
    null_display = lambda state: None
    messageCallback = lambda x: print_string(x)
    decisionCallback = a.getAction
    # pauseCallback = lambda: display.pause()
    pauseCallback = lambda: None
    # RUN EPISODES
    if _episodes > 0:
        print
        print "RUNNING", _episodes, "EPISODES"
        print
    returns = 0
    for episode in range(1, _episodes + 1):
        if episode <= _training_episodes:
            returns += runEpisode(a, env, _discount, decisionCallback, graphic_display, messageCallback, pauseCallback,
                                  episode, train=True)
        else:
            print "TESTING EPISODE"
            print
            a.epsilon = 0.0
            returns += runEpisode(a, env, _discount, decisionCallback, graphic_display, messageCallback, pauseCallback,
                                  episode)
        print
        print "FINISHED", str(episode), "th", "EPISODE"
        print a.getWeights()
        print
    if _episodes > 0:
        print
        print "AVERAGE RETURNS FROM START STATE: " + str((returns + 0.0) / _episodes)
        print
        print

