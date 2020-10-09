from load_balance_gym.envs.load_balance_floodlight_costly_flow import LoadBalanceEnvDiscAction

from stable_baselines.common.env_checker import check_env
from stable_baselines.common.policies import MlpPolicy
from stable_baselines.common import make_vec_env
from stable_baselines import PPO2, A2C, DQN
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

curl -X POST 'http://192.168.68.127:8080//wm/routing/paths/max-fast-paths/json' -d '{"max_fast_paths": "10"}'


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

"""

CONTROLLER_IP = 'http://192.168.68.127'
CONTROLLER_HOST = '{host}:8080'.format(host=CONTROLLER_IP)

link_a_rx = []
link_b_rx = []
link_c_rx = []
link_d_rx = []
link_e_rx = []
link_f_rx = []
link_g_rx = []
link_h_rx = []
link_i_rx = []

rewards = []

def createVectorizedEnv():
    # Aguarda scripts iniciarem.
    # Fluxo sai de H1 e vai para H2
    env = LoadBalanceEnvDiscAction(source_port_index=0, source_switch_index=0, target_port_index=0, target_switch_index=2)
    env = make_vec_env(lambda: env, n_envs=1)

    return env


def updatePortStatistics(state):
    state = state.flatten()

    link_a_rx.append(state[0])
    link_b_rx.append(state[1])
    link_c_rx.append(state[2])
    link_d_rx.append(state[3])
    link_e_rx.append(state[4])
    link_f_rx.append(state[5])
    link_g_rx.append(state[6])
    link_h_rx.append(state[7])
    link_i_rx.append(state[8])

def validateEnvOpenAI():
    print('************** Validacao da env: *************')
    print(check_env(env, warn=True))
    print('************************************************')


def trainAgent(env):
    # Parametros adicionais para criar o modelo: gamma (discount_factor), n_steps (numero de steps para rodar para cada env por update), learning_rate
    print('Iniciando treinamento do agente.')
    model = DQN(policy=MlpPolicy, env=env, verbose=1, learning_rate=0.1, gamma=0.96)
    model.learn(total_timesteps=1000)
    model.save('./DQN_1000_lr_01_gamma_096')
    print('Modelo treinado e salvo.')


def testAgent(env):
    print('Testando o agente...')
    model = A2C.load(load_path='./A2C_100_lr_01_gamma_096-disc-env', env=env)
    # model = A2C.load(load_path='./A2C_100_lr_005_gamma_097-disc-env-sem_acao_inv', env=env)

    state = env.reset()
    num_steps = 100

    for step in range(num_steps):
        action, _ = model.predict(state, deterministic=True)
        # print('Action: ', action)

        state, reward, done, info = env.step(action)
        # print('Reward = ', reward)
        # print('New state = ', state)

        updatePortStatistics(state)
        rewards.append(reward)
        step += 1

    plotGraphs()


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



"""
Env methods tests
"""
def testEnvMethods():
    env = LoadBalanceEnvDiscAction(source_port_index=0, source_switch_index=0, target_port_index=0, target_switch_index=2)

    rule_name1 = env.existsRuleWithAction(switch_id='00:00:00:00:00:00:00:01', in_port=1, out_port=2)
    print('Regra encontrada para o switch 1:', rule_name1)

    rule_name2 = env.existsRuleWithAction(switch_id='00:00:00:00:00:00:00:02', in_port=1, out_port=4)
    print('Regra encontrada para o switch 2:', rule_name2)

    rule_name3 = env.existsRuleWithAction(switch_id='00:00:00:00:00:00:00:03', in_port=2, out_port=1)
    print('Regra encontrada para o switch 3:', rule_name3)

    if rule_name1:
        delete_rule_1_response = env.uninstallRule(rule_name1)
        print('Resposta apagando regra 1: ', delete_rule_1_response.json())

    if rule_name2:
        delete_rule_2_response = env.uninstallRule(rule_name2)
        print('Resposta apagando regra 2: ', delete_rule_2_response.json())

    if rule_name3:
        delete_rule_3_response = env.uninstallRule(rule_name3)
        print('Resposta apagando regra 3: ', delete_rule_3_response.json())


def run():
    # env = createVectorizedEnv()
    # validateEnvOpenAI(env)
    # print('Iniciando treinamento do agente.')
    # trainAgent(env)

    env = LoadBalanceEnvDiscAction(source_port_index=0, source_switch_index=0, target_port_index=0, target_switch_index=2)
    while True:
        print(env.getState())
        time.sleep(1)

    # changeMaxPaths()
    # addInitialEntries()

    # testEnvMethods()
    #
    # testAgent(env)

    # runExperiments(env)


##################################################################################
run()
