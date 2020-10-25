from load_balance_gym.envs.load_balance_floodlight_costly_flow import LoadBalanceEnvDiscAction

from stable_baselines.common.env_checker import check_env
from stable_baselines.deepq.policies import MlpPolicy
from stable_baselines.common import make_vec_env
from stable_baselines import PPO2, A2C, DQN
from stable_baselines.common.evaluation import evaluate_policy

from matplotlib import pyplot as plt
from collections import Counter

import time
import gym
import numpy
import datetime
import linecache
import os
import tracemalloc
import sys, getopt

"""
python train-agent.py -a <agent> -t <timesteps>
"""

CONTROLLER_IP = 'http://192.168.68.127'
CONTROLLER_HOST = '{host}:8080'.format(host=CONTROLLER_IP)

rewards = []

def createVectorizedEnv():
    # Aguarda scripts iniciarem.
    # Fluxo sai de H1 e vai para H2
    env = LoadBalanceEnvDiscAction(source_port_index=0, source_switch_index=0, target_port_index=0, target_switch_index=2)
    env = make_vec_env(lambda: env, n_envs=1)

    return env

def validateEnvOpenAI():
    print('************** Validacao da env: *************')
    print(check_env(env, warn=True))
    print('************************************************')


def trainAgent(env, agent, timesteps):
    model = DQN(
        env=env,
        policy=MlpPolicy,
        verbose=1,
        learning_rate=0.05, # alpha: If your learning rate is set too low, training will progress very slowly as you are making very tiny updates to the weights in your network. However, if your learning rate is set too high, it can cause undesirable divergent behavior in your loss function.
        gamma=0.95, # It controls the importance of the future rewards versus the immediate ones.
        exploration_initial_eps=1.0,
        exploration_fraction=0.9,
        exploration_final_eps=0.01,
        buffer_size=56,
        batch_size=50
    )
    model.learn(total_timesteps=timesteps)

    model_file_path = './trained-agents/' + agent
    model.save(model_file_path)

    print('Modelo {0} treinado e salvo.'.format(agent))


"""
Elephant flow detection
"""
def containsElephantFlow(state):
    pass



def main(argv):
    try:
        opts, args = getopt.getopt(argv, "ha:t:", ["agent=", "timesteps="])
    except getopt.GetoptError:
        print ('run-experiments.py -a <agent> -t <timesteps>')
        sys.exit(2)

    agent = None
    timesteps = None

    for opt, arg in opts:
        if opt == '-h':
            print ('run-experiments.py -a <agent> -n <numflows> -s <flowsize> -t <timesteps>')
            sys.exit()
        elif opt in ("-a", "--agent"):
            agent = arg
        elif opt in ("-t", "--timesteps"):
            timesteps = arg

    print('Training: agent = {0}, timesteps = {1}'.format(agent, timesteps))

    start_time = datetime.datetime.now()
    env = createVectorizedEnv()
    output_file_data = testAgent(env, agent, num_flows, flows_size, timesteps)
    time_interval = datetime.datetime.now() - start_time

    print('Training took ', time_interval)



##################################################################################
if __name__ == "__main__":
   main(sys.argv[1:])
