from load_balance_gym.envs.load_balance_floodlight_costly_flow import LoadBalanceEnvDiscAction

from stable_baselines.common.env_checker import check_env
# from stable_baselines.common.policies import MlpPolicy
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
    print('Iniciando treinamento do agente.')
    model = DQN(
        env=env,
        policy=MlpPolicy,
        verbose=1,
        learning_rate=0.005, # alpha
        gamma=0.98,
        exploration_initial_eps=1.0,
        exploration_fraction=0.9,
        exploration_final_eps=0.05,
        buffer_size=56,
        batch_size=50
    )
    model.learn(total_timesteps=500)
    model.save('./DQN_500_lr_0005_gamma_098_expldecay_09_3_flows')
    print('Modelo treinado e salvo.')


def testAgent(env):
    # DQN_500_lr_005_gamma_095_expldecay_0995 -> na veradde era expl decay de 0.9 --> 3 fluxos
    # DQN_500_lr_001_gamma_095_expldecay_09_3_flows
    #
    model = DQN.load(load_path='./DQN_500_lr_005_gamma_095_expldecay_0995', env=env)

    state = env.reset()
    num_steps = 100

    for step in range(num_steps):
        action, _ = model.predict(state, deterministic=True)
        # print('Action: ', action)

        state, reward, done, info = env.step(action)
        # print('Step {0}. Reward = {1}'.format(step, reward))
        print('State = ', state)

        # updatePortStatistics(state)
        print('Reward = ', reward)
        step += 1

    # plotGraphs()


def runExperiments():
    print('Rodando experimentos...')
    model = A2C.load(load_path='./A2C_100_lr_01_gamma_096-disc-env', env=env)
    env.reset()
    update_count = 0

    # Avaliar o state e identificar se existe algum elephant flow potencial
    while True:
        state = env.getState()

        if containsTraffic(state) and containsElephantFlow(state):
            print('---------------------------------------------')
            print('Update: ', update_count)

            action, _ = model.predict(state, deterministic=True)
            state, reward, done, info = env.step(action)
            print('State: ', state)
            print('Action: ', action)
            print('Reward: ', reward)

            p0, p1, p2, p3, p4, p5, p6, p7, p8,p9, p10, p11, p12, p13, p14, p15 = updatePortStatistics(state)

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

"""
Graficos
"""
def plotGraphs():
    print('Gerando graficos...')

    plt.figure()
    # plt.subplot(1)
    plt.plot(link_a_rx, '-', color="#ef476f", label = "Link a") # paradise pink
    plt.plot(link_b_rx, '-', color="#ffd166", label = "Link b") # orange yellow crayola
    plt.plot(link_c_rx, '-', color="#06d6a0", label = "Link c") # caribeen green
    plt.plot(link_d_rx, '-', color="#118AB2", label = "Link d") # blue NCS
    plt.plot(link_e_rx, '-', color="#073B4C", label = "Link e") # midnight green eagle green
    plt.plot(link_f_rx, '-', color="#5f0f40", label = "Link f") # tryian purple
    plt.plot(link_g_rx, '-', color="#9A031E", label = "Link g") # ruby red
    plt.plot(link_h_rx, '-', color="#FB8B24", label = "Link h") # dark orange
    plt.plot(link_i_rx, '-', color="#E36414", label = "Link i") # spanish orange

    plt.xlabel('Step')
    plt.ylabel('Mbits/seg')

    # Set a title of the current axes.
    plt.title('Mbits/seg RX per step')

    # show a legend on the plot
    plt.legend()

    # plt.subplot(2)
    # plt.plot(rewards)
    # plt.plot(rewards)
    # plt.xlabel('Step')
    # plt.ylabel('Reward')
    # plt.title('Reward per step')

    plt.savefig('A2C_100_lr_01_gamma_096-30-set-links_usage.pdf')

    print('Grafico gerado.')



def run():
    env = createVectorizedEnv()
    # validateEnvOpenAI(env)
    trainAgent(env)


    # env = LoadBalanceEnvDiscAction(source_port_index=0, source_switch_index=0, target_port_index=0, target_switch_index=2)
    # while True:
    #     print(env.getState())
    #     time.sleep(1)

    # changeMaxPaths()
    # addInitialEntries()

    # testEnvMethods()
    #
    # testAgent(env)

    # runExperiments(env)


##################################################################################
run()
