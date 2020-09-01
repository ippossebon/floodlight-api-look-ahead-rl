from load_balance_gym.envs.load_balance_with_floodlight import LoadBalanceEnv

from stable_baselines.common.env_checker import check_env
from stable_baselines.common.policies import MlpPolicy
from stable_baselines.common import make_vec_env
from stable_baselines import PPO2

import json
import time
import requests
import gym

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
NUM_FLOWS = 5

for flow_index in range(0, NUM_FLOWS):
    # Adiciona fluxo na rede.
    flow_name = 'flow-{0}'.format(flow_index)
    flow = {
        'switch':'00:00:00:00:00:00:00:01',
        'name': flow_name,
        'cookie':'0',
        'priority':'32767',
        'in_port':'1',
        'active':'true',
        'actions':'output=2'
    }

    response = requests.post(
        'http://localhost:8080/wm/staticentrypusher/json',
        data=json.dumps(flow)
    )
    # print('Resposta ao adicionar novo fluxo na rede: ', response)


# Fluxo sai de H1 e vai para H2
# env = LoadBalanceEnv(source_port=1, source_switch=0, target_port=1, target_switch=2)

time.sleep(20)

# multiprocess environment
# env = make_vec_env('CartPole-v1', n_envs=4)
env = LoadBalanceEnv(source_port=1, source_switch=0, target_port=1, target_switch=2)
print(check_env(env, warn=True))


# model = PPO2(MlpPolicy, env, verbose=1)
# model.learn(total_timesteps=25000)
# model.save('ppo2_load_balance')
#
# del model # remove to demonstrate saving and loading
#
# model = PPO2.load('ppo2_load_balance')
#
# obs = env.reset()
# while True:
#     action, _states = model.predict(obs)
#     obs, rewards, dones, info = env.step(action)
#     env.render()
