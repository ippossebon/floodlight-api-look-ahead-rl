import random
import pkg_resources
pkg_resources.require("tensorflow==1.15.2")

import numpy as np

from .agent import Agent

class QAgent(Agent):
    def __init__(self, env, discount_rate=0.97, learning_rate=0.01):
        super().__init__(env)
        self.state_size = env.observation_space.n
        print("State size:", self.state_size)

        self.eps = 1.0
        self.discount_rate = discount_rate
        self.learning_rate = learning_rate
        self.build_model()

    def build_model(self):
        # como criar uma Q table considerando que o estado é um array, e nao numeros inteiros?
        # CUIDADO: problema de memoria!!!
        self.q_table = 1e-4*np.random.random([self.state_size, self.action_size])

    def get_action(self, state):
        q_state = self.q_table[state]
        action_greedy = np.argmax(q_state)
        action_random = super().get_action(state)
        return action_random if random.random() < self.eps else action_greedy

    def train(self, experience):
        state, action, next_state, reward, done = experience

        q_next = self.q_table[next_state]
        q_next = np.zeros([self.action_size]) if done else q_next
        q_target = reward + self.discount_rate * np.max(q_next)

        q_update = q_target - self.q_table[state,action]
        self.q_table[state,action] += self.learning_rate * q_update

        if done:
            self.eps = self.eps * 0.99
