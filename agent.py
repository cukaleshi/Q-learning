from qlearn import Qlearn

import random

import gym
import numpy as np


class Agent:
    def __init__(self, epsilon_gredy, max_lifes=20000):

        self.epsilon_gredy = epsilon_gredy
        self.init_epsilon()
        self.init_self()

    def init_self(self):
        self.env = gym.make('FrozenLake-v0')
        self.state = self.env.reset()
        self.old_state = 0
        # self.env.render()
        self.brain = Qlearn(0.1, 0.99, self.env.observation_space.n, self.env.action_space.n)
        self.action = 0
        self.dead = False
        self.reward = 0
        self.lifes_spent = 0
        self.epoch = 1
        self.gambled = False
        self.steps = 0
        self.exploration_rate_history = [self.epsilon]
        self.gamble_history = [0, 0]

    def init_epsilon(self):
        self.epsilon = self.epsilon_gredy
        self.max_epsilon = self.epsilon_gredy
        self.decay_rate = self.epsilon_gredy / 1000

    def reset(self):
        # if self.lifes_spent >= 100:
        #     self.lifes_spent = 0
        #     self.epoch += 1
        self.steps = 0
        self.lifes_spent += 1
        self.dead = False
        self.state = self.env.reset()
        # self.env.render()
        # 100 lifes = epoch
        self.epsilon = self.decay_rate + (self.max_epsilon - self.decay_rate) * np.exp(
            -self.decay_rate * self.lifes_spent * self.epoch)
        self.exploration_rate_history.append(self.epsilon)

    def restart(self):
        self.brain.reset_table()
        self.init_epsilon()
        self.init_self()

    def train_once(self):
        self.steps += 1
        if self.dead:
            self.reset()
        else:
            self.gamble()
            new_state, self.reward, self.dead, info = self.env.step(self.action)

            self.brain.train(self.state, new_state, self.reward, self.action)
            self.old_state = self.state
            self.state = new_state
            # self.env.render()
            # print("self agent steps = " + str(self.steps))

    def getGame_repr(self):
        desc = self.env.unwrapped.desc.tolist()
        game_grid = [[c.decode('utf-8') for c in line] for line in desc]
        return game_grid

    def gamble(self):
        if random.uniform(0, 1) > self.epsilon:
            self.action = self.brain.predict_move(self.state)
            self.gamble_history[1] = self.gamble_history[1] + 1
            self.gambled = False
        else:  # gamble
            self.action = random.randint(0, 3)
            self.gamble_history[0] = self.gamble_history[0] + 1
            self.gambled = True

    def play(self):
        if self.gambled == True:
            self.gambled = False

        if self.dead:
            self.dead = False
            self.state = self.env.reset()
        else:
            self.old_state = self.state
            self.state, self.reward, self.dead, info = self.env.step(self.brain.predict_move(self.state))
            self.steps += 1
            # self.env.render()
