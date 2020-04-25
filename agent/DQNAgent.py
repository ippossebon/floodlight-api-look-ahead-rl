import random
import numpy as np

import pkg_resources
pkg_resources.require("tensorflow==1.15.2")
import tensorflow as tf

from collections import deque
from .q_network import QNetwork

## Agente que vai usar a rede neural
class DQNAgent():
    def __init__(self, env):
        # state_dim = state dimension
        self.state_dim = env.observation_space.shape
        self.action_size = env.action_space.n # n só existe se as ações forem discretas

        self.q_network = QNetwork(self.state_dim, self.action_size)

        # É necessário para termos acesso aos valores de q_state da rede
        self.sess = tf.Session()
        self.sess.run(tf.global_variables_initializer()) # precisa rodar depois de QNetwork(self.state_dimension, self.action_size), senão não terá nenhuma

        self.replay_buffer = ReplayBuffer(maxlen=10000)
        self.gamma = 0.97 # discount rate
        self.eps = 1.0 # probabilidade de selecionar uma ação randomica em detrimento de uma ação greedy -> 1.0 sempre

    def getAction(self, state):
        # Ação aleatória
        # action = random.choice(range(self.action_size))

        # Ação com base nas infos do env
        #action = np.random.uniform(self.action_low, self.action_high, self.action_shape)

        # Ação usando a rede neural
        # O agente precisa escolher a ação com o valor Q máximo previsto pela rede neural
        q_state = self.q_network.getQState(self.sess, [state])
        action_greedy = np.argmax(q_state)
        action_random = np.random.randint(self.action_size)
        action = action_random if random.random() < self.eps else action_greedy

        return action

    def train(self, state, action, next_state, reward, done):
        self.replay_buffer.add((state, action, next_state, reward, done))

        states, actions, next_states, rewards, dones = self.replay_buffer.sample(50)
        print('### next states = ', next_states)
        ## # TODO: deveria enviar next-states???
        q_next_states = self.q_network.getQState(self.sess, next_states)
        q_next_states[dones] = np.zeros([self.action_size])
        q_targets = rewards + self.gamma * np.max(q_next_states, axis=1)

        self.q_network.updateModel(self.sess, states, actions, q_targets)

        if done: self.eps = max(0.1, 0.99*self.eps)

    def __del__(self):
        self.sess.close()


# Usado para otimizar o treinamento

class ReplayBuffer():
    def __init__(self, maxlen):
        self.buffer = deque(maxlen=maxlen)

    def add(self, experience):
        self.buffer.append(experience)

    def sample(self, batch_size):
        sample_size = min(len(self.buffer), batch_size)
        samples = random.choices(self.buffer, k=sample_size)
        return map(list, zip(*samples))
