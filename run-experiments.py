from load_balance_gym.envs.load_balance_with_floodlight import LoadBalanceEnv

from stable_baselines.common.env_checker import check_env
from stable_baselines.common.policies import MlpPolicy
from stable_baselines.common import make_vec_env
from stable_baselines import PPO2, ACKTR

from flowPusher import addFlows, deleteFlows

import json
import time
import requests
import gym
import numpy

"""
Ideia do experimento: iniciar com 5 fluxos.

sleep(30)

Mais um fluxo. Mais um fluxo, e assim por diante.

O objetivo é fazer com que o sistema acomode os fluxos na rede. Para um número N
de fluxos, em qualquer topologia (dado que utilizamos a aplicação para descobrir
os caminhos possíveis.)

Entrada para o sistema: source_switch, source_port, dst_switch, dst_port

source_switch: 00:00:00:00:00:00:00:01
source_port: 1
dst_switch: 00:00:00:00:00:00:00:03
dst_port: 1

Setup do experimento:
Todos os fluxos começam por a, b, f, i

"""

CONTROLLER_IP = 'http://localhost'
CONTROLLER_HOST = '{host}:8080'.format(host=CONTROLLER_IP)

# addFlows(num_flows=5)
time.sleep(10)

# Fluxo sai de H1 e vai para H2
env = LoadBalanceEnv(source_port_index=0, source_switch_index=0, target_port_index=0, target_switch_index=2)
print()

# max_usage_flow_id = env.getMostCostlyFlow('00:00:00:00:00:00:00:01')
# print('* max_usage_flow_id de 00:00:00:00:00:00:00:01 = ', max_usage_flow_id)
#
# max_usage_flow_id = env.getMostCostlyFlow('00:00:00:00:00:00:00:02')
# print('* max_usage_flow_id de 00:00:00:00:00:00:00:02 = ', max_usage_flow_id)
#
# max_usage_flow_id = env.getMostCostlyFlow('00:00:00:00:00:00:00:03')
# print('* max_usage_flow_id de 00:00:00:00:00:00:00:03 = ', max_usage_flow_id)
#
# max_usage_flow_id = env.getMostCostlyFlow('00:00:00:00:00:00:00:04')
# print('* max_usage_flow_id de 00:00:00:00:00:00:00:04 = ', max_usage_flow_id)
#
# max_usage_flow_id = env.getMostCostlyFlow('00:00:00:00:00:00:00:05')
# print('* max_usage_flow_id de 00:00:00:00:00:00:00:05 = ', max_usage_flow_id)

# print('Todas devem ser TRUE')
# print(env.actionBelongsToPath(action=numpy.array([0,0,2])))
# print(env.actionBelongsToPath(action=numpy.array([3,0,2])))
# print(env.actionBelongsToPath(action=numpy.array([2,2,0])))
# print(env.actionBelongsToPath(action=numpy.array([0,0,1])))
# print(env.actionBelongsToPath(action=numpy.array([1,0,3])))
# print(env.actionBelongsToPath(action=numpy.array([2,1,0])))
# print(env.actionBelongsToPath(action=numpy.array([1,0,2])))
# print(env.actionBelongsToPath(action=numpy.array([4,0,1])))
# print(env.actionBelongsToPath(action=numpy.array([2,3,0])))
# print('-----')
#
# print('Todas devem ser FALSE')
# print(env.actionBelongsToPath(action=numpy.array([0,1,2])))
# print(env.actionBelongsToPath(action=numpy.array([4,0,2])))
# print(env.actionBelongsToPath(action=numpy.array([4,2,3])))
# print(env.actionBelongsToPath(action=numpy.array([4,1,1])))
# print(env.actionBelongsToPath(action=numpy.array([1,2,2])))
# print(env.actionBelongsToPath(action=numpy.array([1,1,1])))
# print(env.actionBelongsToPath(action=numpy.array([2,2,2])))
# print(env.actionBelongsToPath(action=numpy.array([3,4,5])))
# print(env.actionBelongsToPath(action=numpy.array([1,5,5])))
# print('-----')


print('************** Validacao da env: *************')
print(check_env(env, warn=True))
# env = make_vec_env(lambda: env, n_envs=1)
print('************************************************')


# print('Treinando o agente com ACKTR...')
# model = ACKTR('MlpPolicy', env, verbose=1).learn(25)
#
# # Test the trained agent
# print('Testando o agente com gerado...')
#
# obs = env.reset()
# n_steps = 10
# for step in range(n_steps):
#   action, _ = model.predict(obs, deterministic=True)
#   print('Step {}'.format(step + 1))
#   print('Action: ', action)
#   obs, reward, done, info = env.step(action)
#   print('obs=', obs, 'reward=', reward, 'done=', done)
#   env.render()

# print('Treinando o agente com PPO2...')
# model = PPO2(MlpPolicy, env, verbose=1)
# model.learn(total_timesteps=100)
# model.save('ppo2_load_balance')
#
# del model # remove to demonstrate saving and loading
#
# model = PPO2.load('ppo2_load_balance')
#
# print('Testando o agente gerado...')
# state = env.reset()
# n_steps = 50
# print('State: ', state)
#
# for step in range(n_steps):
#   action, _ = model.predict(state, deterministic=True)
#   print('Step: ', step + 1)
#   print('Action: ', action)
#   state, reward, done, info = env.step(action)
#
#   print('state=', state, 'reward=', reward, 'done=', done)
  # env.render()


# print()
# deleteFlows(num_flows=5)
