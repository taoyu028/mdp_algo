# qlearningAgents.py
# ------------------
# Licensing Information:  You are free to use or extend these projects for
# educational purposes provided that (1) you do not distribute or publish
# solutions, (2) you retain this notice, and (3) you provide clear
# attribution to UC Berkeley, including a link to http://ai.berkeley.edu.
# 
# Attribution Information: The Pacman AI projects were developed at UC Berkeley.
# The core projects and autograders were primarily created by John DeNero
# (denero@cs.berkeley.edu) and Dan Klein (klein@cs.berkeley.edu).
# Student side autograding was added by Brad Miller, Nick Hay, and
# Pieter Abbeel (pabbeel@cs.berkeley.edu).


from learningAgents import ReinforcementAgent
import random
import util
from state import get_features
import copy

# from utils import print_grid

class QLearningAgent(ReinforcementAgent):
    """
      Q-Learning Agent

      Functions you should fill in:
        - computeValueFromQValues
        - computeActionFromQValues
        - getQValue
        - getAction
        - update

      Instance variables you have access to
        - self.epsilon (exploration prob)
        - self.alpha (learning rate)
        - self.discount (discount rate)

      Functions you should use
        - self.getLegalActions(state)
          which returns legal actions for a state
    """
    def __init__(self, **args):
        "You can initialize Q-values here..."
        ReinforcementAgent.__init__(self, **args)

        "*** YOUR CODE HERE ***"
        self.weights = util.Counter()
        self.weights["closest_unexplored_inverse"] = 4.152663018285844
        self.weights["to_explored"] = 18.487346254349628

    def getWeights(self):
        return self.weights

    def getQValue(self, state, action):
        """
          Should return Q(state,action) = w * featureVector
          where * is the dotProduct operator
        """

        # print_grid(state.explored_grid)
        sum = 0
        features = get_features(state, action)
        features_keys = features.keys()
        i = 0
        while i < len(features):
            sum += features[features_keys[i]] * self.weights[features_keys[i]]
            i += 1
        # print state.x, state.y, state.direction, action, features, sum
        import math
        if math.isnan(sum):
            raise "NaN value"
        return sum

    def computeValueFromQValues(self, state):
        """
          Returns max_action Q(state,action)
          where the max is over legal actions.  Note that if
          there are no legal actions, which is the case at the
          terminal state, you should return a value of 0.0.
        """

        max_Q = -10000
        actions = self.getLegalActions(state)
        if actions:
            for action in actions:
                copy = self.getQValue(state,action)
                if copy>max_Q:
                    max_Q = copy
            return max_Q
        else:
            return 0.0

    def computeActionFromQValues(self, state):
        """
          Compute the best action to take in a state.  Note that if there
          are no legal actions, which is the case at the terminal state,
          return None.
        """

        actions = self.getLegalActions(state)
        actions_q = []
        if actions:
            for action in actions:
                actions_q.append(self.getQValue(state,action))
            if 0 in actions_q:
                return random.choice(actions)
            else:
                return actions[actions_q.index(max(actions_q))]
        else:
            return None

    def getAction(self, state):
        # Pick Action
        legalActions = self.getLegalActions(state)
        legalActions_q = []
        action = None

        if legalActions:
            for legalAction in legalActions:
                legalActions_q.append(self.getQValue(state,legalAction))
            if all(v==0 for v in legalActions_q):
                return random.choice(legalActions)
            else:
                if util.flipCoin(1-self.epsilon):
                    print "******* BEST action *****"
                    # print(max(legalActions_q))
                    if legalActions_q.count(max(legalActions_q))==1:
                        return legalActions[legalActions_q.index(max(legalActions_q))]
                    else:
                        indices = [i for i, x in enumerate(legalActions_q) if x == max(legalActions_q)]
                        # for i in indices:
                        #     print(legalActions[i])

                        return legalActions[legalActions_q.index(max(legalActions_q))]
                else:
                    print "******* RANDOM action ******"
                    return random.choice(legalActions)
        return action

    def update(self, state, action, nextState, reward):
        """
          The parent class calls this to observe a
          state = action => nextState and reward transition.
          You should do your Q-Value update here

          NOTE: You should never call this function,
          it will be called on your behalf
        """

        nextState_q = []
        for actions in self.getLegalActions(nextState):
            nextState_q.append(self.getQValue(nextState, actions))
        if nextState_q:
            diff = (reward + self.discount * max(nextState_q)) - self.getQValue(state, action)
        else:
            diff = (reward + self.discount * 0) - self.getQValue(state, action)

        features = get_features(state, action)
        features_keys = features.keys()
        for feature_key in features_keys:
            self.weights[feature_key] = self.weights[feature_key] + self.alpha * diff * \
                                                                    get_features(state, action)[feature_key]
        # print self.weights


