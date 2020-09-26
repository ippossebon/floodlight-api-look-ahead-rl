# from load_balance_gym.envs.load_balance_with_floodlight import LoadBalanceEnv
from load_balance_gym.envs.load_balance_with_floodlight_disc_action import LoadBalanceEnvDiscAction

from stable_baselines.common.env_checker import check_env
from stable_baselines.common.policies import MlpPolicy
from stable_baselines.common import make_vec_env
from stable_baselines import PPO2, A2C
from stable_baselines.common.evaluation import evaluate_policy

from matplotlib import pyplot as plt

from flowPusher import addFlows, deleteFlows

import json
import time
import requests
import gym
import numpy

"""
Antes de iniciar o experimento, rodar:

curl -X POST 'http://localhost:8080//wm/routing/paths/max-fast-paths/json' -d '{"max_fast_paths": "10"}'


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
env = None

port_0 = []
port_1 = []
port_2 = []
port_3 = []
port_4 = []
port_5 = []
port_6 = []
port_7 = []
port_8 = []
port_9 = []
port_10 = []
port_11 = []
port_12 = []
port_13 = []
port_14 = []
port_15 = []

def updatePortStatistics(state):
    state = state.flatten()

    port_0.append(state[0])
    port_1.append(state[1])
    port_2.append(state[2])
    port_3.append(state[3])
    port_4.append(state[4])
    port_5.append(state[5])
    port_6.append(state[6])
    port_7.append(state[7])
    port_8.append(state[8])
    port_9.append(state[9])
    port_10.append(state[10])
    port_11.append(state[11])
    port_12.append(state[12])
    port_13.append(state[13])
    port_14.append(state[14])
    port_15.append(state[15])

    return port_0, port_1, port_2, port_3, port_4, port_5, port_6, port_7, port_8, port_9, port_10, port_11, port_12, port_13, port_14, port_15

def validateEnvOpenAI():
    print('************** Validacao da env: *************')
    print(check_env(env, warn=True))
    print('************************************************')

def startEnv():
    # Aguarda scripts iniciarem.
    time.sleep(10)

    # Fluxo sai de H1 e vai para H2
    env = LoadBalanceEnvDiscAction(source_port_index=0, source_switch_index=0, target_port_index=0, target_switch_index=2)
    env = make_vec_env(lambda: env, n_envs=1)

    return env


def trainAgent(env):
    # Parametros adicionais para criar o modelo: gamma (discount_factor), n_steps (numero de steps para rodar para cada env por update), learning_rate
    model = A2C(policy=MlpPolicy, env=env, verbose=1, learning_rate=0.05, gamma=0.97)
    model.learn(total_timesteps=10000)
    model.save('./A2C_10000_lr_005_gamma_097-disc-env')
    print('Modelo treinado e salvo.')


def testAgent(env):
    print('Testando o agente...')
    model = A2C.load(load_path='./A2C_10000_lr_005_gamma_097-disc-env', env=env)
    # model = A2C.load(load_path='./A2C_100_lr_005_gamma_097-disc-env-sem_acao_inv', env=env)


    state = env.reset()
    num_steps = 100

    print('State: ', state)

    for step in range(num_steps):
        print('Step: ', step)

        action, _ = model.predict(state, deterministic=True)
        print('Action: ', action)

        state, reward, done, info = env.step(action)
        print('Reward = ', reward)
        print('New state = ', state)

        p0, p1, p2, p3, p4, p5, p6, p7, p8,p9, p10, p11, p12, p13, p14, p15 = updatePortStatistics(state)
        step += 1

    plotGraphs(p0, p1, p2, p3, p4, p5, p6, p7, p8,p9, p10, p11, p12, p13, p14, p15)


def runExperiments():
    print('Rodando experimentos...')
    model = A2C.load(load_path='./A2C_10000_lr_005_gamma_097-disc-env', env=env)
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
def plotGraphs(p0, p1, p2, p3, p4, p5, p6, p7, p8,p9, p10, p11, p12, p13, p14, p15):
    print('Gerando grafico...')
    plt.plot(p0, '-', color="#ef476f", label = "port 0") # paradise pink
    plt.plot(p1, '-', color="#ffd166", label = "port 1") # orange yellow crayola
    plt.plot(p2, '-', color="#06d6a0", label = "port 2") # caribeen green
    plt.plot(p3, '-', color="#118AB2", label = "port 3") # blue NCS
    plt.plot(p4, '-', color="#073B4C", label = "port 4") # midnight green eagle green
    plt.plot(p5, '-', color="#5f0f40", label = "port 5") # tryian purple
    plt.plot(p6, '-', color="#9A031E", label = "port 6") # ruby red
    plt.plot(p7, '-', color="#FB8B24", label = "port 7") # dark orange
    plt.plot(p8, '-', color="#E36414", label = "port 8") # spanish orange
    plt.plot(p9, '-', color="#00FF00", label = "port 9") # lime
    plt.plot(p10, '-', color="#800080", label = "port 10") # purple
    plt.plot(p11, '-', color="#000000", label = "port 11") # black ?
    plt.plot(p12, '-', color="#FF00FF", label = "port 12") # fuchsia
    plt.plot(p13, '-', color="#800000", label = "port 13") # maroon
    plt.plot(p14, '-', color="#FF0000", label = "port 14") # red
    plt.plot(p15, '-', color="#FFFF00", label = "port 15") # yellow

    plt.xlabel('Step')
    plt.ylabel('In bits')

    # Set a title of the current axes.
    plt.title('Incoming bits per step')

    # show a legend on the plot
    plt.legend()

    plt.savefig('A2C_10000-100_steps-005-097-26_set.pdf')

    print('Grafico gerado')


"""
Env methods tests
"""
def testEnvMethods():
    env = LoadBalanceEnvDiscAction(source_port_index=0, source_switch_index=0, target_port_index=0, target_switch_index=2)

    max_usage_flow_id = env.getMostCostlyFlow('00:00:00:00:00:00:00:01')
    print('* max_usage_flow_id de 00:00:00:00:00:00:00:01 = ', max_usage_flow_id)

    max_usage_flow_id = env.getMostCostlyFlow('00:00:00:00:00:00:00:02')
    print('* max_usage_flow_id de 00:00:00:00:00:00:00:02 = ', max_usage_flow_id)

    max_usage_flow_id = env.getMostCostlyFlow('00:00:00:00:00:00:00:03')
    print('* max_usage_flow_id de 00:00:00:00:00:00:00:03 = ', max_usage_flow_id)

    max_usage_flow_id = env.getMostCostlyFlow('00:00:00:00:00:00:00:04')
    print('* max_usage_flow_id de 00:00:00:00:00:00:00:04 = ', max_usage_flow_id)

    max_usage_flow_id = env.getMostCostlyFlow('00:00:00:00:00:00:00:05')
    print('* max_usage_flow_id de 00:00:00:00:00:00:00:05 = ', max_usage_flow_id)

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


def run():
    # env = startEnv()

    # validateEnvOpenAI()
    testEnvMethods()
    # trainAgent(env)
    # testAgent(env)

    # runExperiments()


##################################################################################
run()
