from graphModel.graph import Graph
from graphModel.link import Link
from graphModel.node import Node

import numpy as np
import gym

DEFAULT_EPSILON = 0.9
DEFAULT_ALPHA = 0.85
DEFAULT_GAMMA = 0.95

MAX_STEPS = 100
TOTAL_EPISODES = 10000

"""
Testar tutoriais: https://medium.com/swlh/introduction-to-reinforcement-learning-coding-sarsa-part-4-2d64d6e37617
"""

class RLLoadBalancer(object):
    def __init__(self, epsilon=DEFAULT_EPSILON, alpha=DEFAULT_ALPHA, gamma=DEFAULT_GAMMA,
        max_steps=MAX_STEPS, total_episodes=TOTAL_EPISODES):
        self.epsiolon = epsilon
        self.alpha = alpha
        self.gamma = gamma
        self.max_steps = max_steps
        self.total_episodes = total_episodes

    def chooseAction(self, state):
    # Function to choose the next action
        action=0
        if np.random.uniform(0, 1) < epsilon:
            action = env.action_space.sample()
        else:
            action = np.argmax(Q[state, :])
        return action

    def update(self, state, state2, reward, action, action2):
        #Function to learn the Q-value
        predict = self.Q_matrix[state, action]
        target = reward + self.gamma * self.Q_matrix[state2, action2]
        self.Q_matrix[state, action] = self.Q_matrix[state, action] + self.alpha * (target - predict)

    def trainModel(self):
        #Initializing the reward
        reward = 0

        # Starting the SARSA learning
        for episode in range(self.total_episodes):
            t = 0
            state1 = env.reset()
            action1 = self.chooseAction(state1)

            while t < self.max_steps:
                #Visualizing the training
                env.render()

                #Getting the next state
                state2, reward, done, info = env.step(action1)

                #Choosing the next action
                action2 = self.chooseAction(state2)

                #Learning the Q-value
                self.update(state1, state2, reward, action1, action2)

                state1 = state2
                action1 = action2

                #Updating the respective vaLues
                t += 1
                reward += 1

                #If at the end of learning process
                if done:
                    break


    def runModel(self):
        # Tutorial: https://www.geeksforgeeks.org/sarsa-reinforcement-learning/
        # Here, we will be using the ‘FrozenLake-v0’ environment which is preloaded into gym.
        # You can read about the environment description here.
        # Building the environment
        env = gym.make('FrozenLake-v0')

        #Defining the different parameters


        #Initializing the Q_matrix
        self.Q_matrix = np.zeros((env.observation_space.n, env.action_space.n))


    def evaluatePerformance(self):
        print ("Performace : ", reward/total_episodes)
