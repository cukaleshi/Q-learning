import numpy as np


class Qlearn:

    def __init__(self, learning_rate, discount_factor, table_states, table_actions):
        self.learning_rate = learning_rate
        self.discount_factor = discount_factor
        self.states = table_states
        self.actions = table_actions
        self.reset_table()

    def train(self, old_state, new_state, reward, action):
        self.qtable[old_state, action] = self.qtable[old_state, action] + self.learning_rate * (
                reward + self.discount_factor * np.max(self.qtable[new_state, :]) - self.qtable[old_state, action])

    def predict_move(self, state):
        return np.argmax(self.qtable[state, :])

    def reset_table(self):
        self.qtable = np.zeros([self.states, self.actions])
