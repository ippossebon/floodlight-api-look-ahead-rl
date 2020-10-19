from load_balance_gym.envs.load_balance_floodlight_costly_flow import LoadBalanceEnvDiscAction

from stable_baselines.common.env_checker import check_env
from stable_baselines.deepq.policies import MlpPolicy
from stable_baselines.common import make_vec_env
from stable_baselines import PPO2, A2C, DQN
from stable_baselines.common.evaluation import evaluate_policy

from matplotlib import pyplot as plt

import json
import time
import requests
import gym
import numpy
import datetime

"""
O objetivo é fazer com que o sistema acomode os fluxos na rede de forma a usar
melhor os seus recursos.

Entrada para o sistema: source_switch, source_port, dst_switch, dst_port

source_switch: 00:00:00:00:00:00:00:01
source_port: 1
dst_switch: 00:00:00:00:00:00:00:03
dst_port: 1


Setup do experimento:
1. Executar controlador
2. Executar mininet com a topologia topologies/complete-experiment-topo.py
4. Remover todas as entradas do staticflowpusher
5. Instalar flows iniciais com Postman (arquivo initial_flows_entries.csv)
6. Para treinamento
    6.1 Iniciar 3 clients em H1 e 3 servers em H2 (iperf3)
        a. iperf3 -s -p 5201
        b. iperf3 -c 10.0.0.2 -B 10.0.0.1 5201 --cport 46110 -n 1G > client-46110-1G.txt
        c. iperf3 -s -p 5202
        d. iperf3 -c 10.0.0.2 -B 10.0.0.1 5202 --cport 46112 -n 2G > client-46112-2G.txt
        e. iperf3 -s -p 5203
        f. iperf3 -c 10.0.0.2 -B 10.0.0.1 5203 --cport 46114 -n 4G > client-46114-4G.txt
7. Para testar o agente
8. Para rodar os experimentos + coleta de estatísticas para avaliação

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


def trainAgent(env):
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
    model.learn(total_timesteps=700)
    model.save('./trained-agents/C1')
    print('Modelo treinado e salvo.')


def testAgent(env):
    # DQN_500_lr_005_gamma_095_expldecay_0995 -> na veradde era expl decay de 0.9 --> 3 fluxos
    # DQN_500_lr_001_gamma_095_expldecay_09_3_flows
    # DQN_500_lr_0005_gamma_098_expldecay_09_3_flows
    # DQN_500_lr_0005_gamma_095_expldecay_09_2_flows
    model = DQN.load(load_path='./trained-agents/B1', env=env)

    state = env.reset()
    num_steps = 700

    output_file_data = []
    output_file_data.append('Step; State; Reward')

    for step in range(num_steps):
        print('Step ', step)
        action, _ = model.predict(state, deterministic=False)
        state, reward, done, info = env.step(action)
        step += 1

        output_data_line = '{0}; {1}; {2}'.format(step, state, reward)
        output_file_data.append(output_data_line)

    output_filename = './B1-3flows.csv'

    with open(output_filename, 'w+') as output_file:
        for item in output_file_data:
            output_file.write("%s\n" % item)

    print('Arquivo {0} criado.'.format(output_filename))


def runExperiments():
    print('Rodando experimentos...')
    model = A2C.load(load_path='./A2C_100_lr_01_gamma_096-disc-env', env=env)
    env.reset()
    update_count = 0

    # Avaliar o state e identificar se existe algum elephant flow potencial
    while True:
        state = env.getState()

        if containsTraffic(state) and containsElephantFlow(state):
            print('Update: ', update_count)

            action, _ = model.predict(state, deterministic=True)
            state, reward, done, info = env.step(action)

            update_count += 1
        else:
            # Aguarda dois segundos e checa de novo.
            time.sleep(2)


"""
Elephant flow detection
"""
def containsElephantFlow(state):
    pass


def containsTraffic(state):
    pass


def run():
    env = createVectorizedEnv()
    # validateEnvOpenAI(env)
    start_time = datetime.datetime.now()
    # trainAgent(env)
    testAgent(env)
    training_time = datetime.datetime.now() - start_time
    print('Test took: ', training_time)
    # runExperiments(env)


##################################################################################
run()
