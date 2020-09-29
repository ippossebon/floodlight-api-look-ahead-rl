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

"""

CONTROLLER_IP = 'http://localhost'
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
    time.sleep(1)

    # Fluxo sai de H1 e vai para H2
    env = LoadBalanceEnvDiscAction(source_port_index=0, source_switch_index=0, target_port_index=0, target_switch_index=2)
    env = make_vec_env(lambda: env, n_envs=1)

    return env


def changeMaxPaths():
    data = json.dumps({"max_fast_paths": "10"})
    headers = {
        'Content-type': 'application/json',
        'Accept': 'application/json',
    }
    response = requests.post(
        '{host}/wm/statistics/config/enable/json'.format(host=CONTROLLER_HOST),
        data=data,
        headers=headers
    )
    response_data = response.json()

    print('Changing max paths value: ', response_data)


def installRule(rule):
    urlPath = '{host}/wm/staticentrypusher/json'.format(host=CONTROLLER_HOST)
    headers = {
        'Content-type': 'application/json',
        'Accept': 'application/json',
    }

    return requests.post(urlPath, data=rule, headers=headers)

def addInitialEntries():
    # Inicialmente, todos os fluxos serguirão o caminho S1 -> S2 -> S3.
    # O trabalho do agente é identificar que isso é um problema e encontrar as melhores regras
    entry1 = {
        "switch": "00:00:00:00:00:00:00:01",
        "name": "switch-1-initial-entry",
        "priority": "32760",
        "in_port": "1",
        "active": "true",
        "actions": "output=2"
    }
    rule1 = json.dumps(entry1)

    entry2 = {
        "switch": "00:00:00:00:00:00:00:02",
        "name": "switch-2-initial-entry",
        "priority": "32760",
        "in_port": "1",
        "active": "true",
        "actions": "output=4"
    }
    rule2 = json.dumps(entry2)


    entry3 = {
        "switch": "00:00:00:00:00:00:00:03",
        "name": "switch-3-initial-entry",
        "priority": "32760",
        "in_port": "2",
        "active": "true",
        "actions": "output=1"
    }
    rule3 = json.dumps(entry3)

    group_test = {
        "switch" : "00:00:00:00:00:00:00:01",
        "entry_type" : "group",
        "name" : "group-mod-1",
        "active" : "true",
        "group_type" : "select",
        "group_id" : "1",
        "group_buckets" : [
            {
                "bucket_id" : "1",
                "bucket_watch_port" : "1",
                "bucket_watch_group" : "any",
                "bucket_weight" : "50",
                "bucket_actions":"output=2"
            },
            {
                "bucket_id" : "2",
                "bucket_watch_port" : "2",
                "bucket_watch_group" : "any",
                "bucket_weight" : "50",
                "bucket_actions":"output=3"
            }
        ]
    }
    group_rule = json.dumps(group_test)

    response_rule1 = installRule(rule1)
    response_rule2 = installRule(rule2)
    response_rule3 = installRule(rule3)
    response_group = installRule(group_rule)

    print('Adding initial rule 1: ', response_rule1.json())
    print('Adding initial rule 2: ', response_rule2.json())
    print('Adding initial rule 3: ', response_rule3.json())
    print('Adding GROUP: ', response_group.json())

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
    model = A2C(policy=MlpPolicy, env=env, verbose=1, learning_rate=0.05, gamma=0.97)
    model.learn(total_timesteps=500)
    model.save('./A2C_500_lr_005_gamma_097-disc-env')
    print('Modelo treinado e salvo.')


def testAgent(env):
    print('Testando o agente...')
    model = A2C.load(load_path='./A2C_500_lr_005_gamma_097-disc-env', env=env)
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
    model = A2C.load(load_path='./A2C_500_lr_005_gamma_097-disc-env', env=env)
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
    plt.ylabel('Link RX')

    # Set a title of the current axes.
    plt.title('Links RX per step')

    # show a legend on the plot
    plt.legend()

    # plt.subplot(2)
    # plt.plot(rewards)
    # plt.plot(rewards)
    # plt.xlabel('Step')
    # plt.ylabel('Reward')
    # plt.title('Reward per step')

    plt.savefig('A2C_500-100_steps-005-097-27_set-links_usage.pdf')

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
    env = createVectorizedEnv()
    # validateEnvOpenAI(env)

    changeMaxPaths()
    addInitialEntries()

    # testEnvMethods()

    trainAgent(env)
    testAgent(env)

    # runExperiments(env)


##################################################################################
run()
