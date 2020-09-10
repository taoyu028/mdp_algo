# mdp_algo
CZ3004 MDP algorithm implemented using reinforcement learning


# Setup
1. python2.7
2. if you get error messages regarding Tkinter, 
see [this](https://stackoverflow.com/questions/25905540/importerror-no-module-named-tkinter)
and [this](https://www.python.org/download/mac/tcltk/#built-in-8-6-8)


# How to use
1. change the path to grid in `gridworld.py` `get_grid_from_file(<path>)` to the
path of your grid
2. change parameters `_episodes` and `_training_episodes` in `gridworld.py` to desired value
3. (optional setup)
    1. parameter `_epsilon` in `gridworld.py` to your desired exploration rate
    2. parameter `__speed` in `gridworld.py` to your desired number of movement per second
    3. parameter `pauseCallback` in `gridworld.py`
    4. function callback `graphic_display` in  `gridworld.py` line366 to `null_display`
4. after training, remember to save weights manually in `__init__()` in `qlearningAgents.py`   
 
# Advanced
You can design your own features by modifying `get_features()` in `state.py` and change the
reward function in `getReward()` in `gridworld.py` respectively


# Reference
http://ai.berkeley.edu/reinforcement.html