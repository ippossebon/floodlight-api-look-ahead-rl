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
python3 run-experiments.py -a <agent> -n <numflows> -s <flowsize> -t <timesteps>

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

csv_output_filename = None

def createVectorizedEnv():
    # Aguarda scripts iniciarem.
    # Fluxo sai de H1 e vai para H2
    original_env = LoadBalanceEnvDiscAction(source_port_index=0, source_switch_index=0, target_port_index=0, target_switch_index=2)
    env = make_vec_env(lambda: original_env, n_envs=1)

    return env, original_env

def validateEnvOpenAI():
    print('************** Validacao da env: *************')
    print(check_env(env, warn=True))
    print('************************************************')


def trainAgent(env, agent):
    model = DQN(
        env=env,
        policy=MlpPolicy,
        verbose=1,
        learning_rate=0.1, # alpha: If your learning rate is set too low, training will progress very slowly as you are making very tiny updates to the weights in your network. However, if your learning rate is set too high, it can cause undesirable divergent behavior in your loss function.
        gamma=0.95, # It controls the importance of the future rewards versus the immediate ones.
        exploration_initial_eps=1.0,
        exploration_fraction=0.8,
        exploration_final_eps=0.1,
        buffer_size=56,
        batch_size=50
    )

    # treinamento com 5 fluxos de 300M
    model.learn(total_timesteps=700)
    model.save('./trained-agents/' + agent)
    print('Modelo treinado e salvo: ', agent)


def testLookAheadAgent(env, original_env, agent):
    agent_path = 'trained-agents/{0}'.format(agent)
    model = DQN.load(load_path=agent_path, env=env)

    state = env.reset()

    writeLineToFile('Step; State; Reward', csv_output_filename)

    time.sleep(5) # pra dar tempo de iniciar os fluxos e não ficar com active_flows vazio

    while True:
        active_flows = original_env.getActiveFlows()

        for flow in active_flows:
            if original_env.isElephantFlow(flow):
                state = original_env.getState()
                action, _ = model.predict(state, deterministic=False)
                state, reward, done, info = env.step(action, flow)

                output_data_line = '{0}; {1}; {2}'.format(step, state, reward)
                writeLineToFile(output_data_line, csv_output_filename)

        print()
        time.sleep(1)


def main(argv):
    global csv_output_filename
    # start1 = datetime.datetime.now()
    #
    # try:
    #     opts, args = getopt.getopt(argv, "ha:n:s:t:i:", ["agent=", "numflows=", "flowsize=", "timesteps=", "iter="])
    # except getopt.GetoptError:
    #     print ('test-env.py -a <agent> -n <numflows> -s <flowsize> -t <timesteps> -i <iter>')
    #     sys.exit(2)
    #
    agent = 'B'
    # num_flows = None
    # flows_size = None
    # timesteps = None
    # iter = None
    #
    # for opt, arg in opts:
    #     if opt == '-h':
    #         print ('run-experiments.py -a <agent> -n <numflows> -s <flowsize> -t <timesteps> -i <iter>')
    #         sys.exit()
    #     elif opt in ("-a", "--agent"):
    #         agent = arg
    #     elif opt in ("-n", "--numflows"):
    #         num_flows = arg
    #     elif opt in ("-s", "--flowsize"):
    #         flows_size = arg
    #     elif opt in ("-t", "--timesteps"):
    #         timesteps = arg
    #     elif opt in ("-i", "--iter"):
    #         iter = arg
    #
    #
    print('Running: agent = {0}, number of flows = {1}, flows size = {2}, timesteps = {3}, iter = {4}'.format(
        agent, num_flows=2, flows_size='ALL', timesteps='LA', iter=12
    ))

    # if agent == 'F' or agent == 'F2':
    #     flow_size_bits = int(flows_size.strip('M')) * 8
    #     wait_time = (int(num_flows) * flow_size_bits/10 ) * 4
    #     print('wait_time = ', wait_time)
    #     time.sleep(wait_time)
    # else:
    env, original_env = createVectorizedEnv()
    testLookAheadAgent(env, original_env, agent)



##################################################################################
if __name__ == "__main__":
    main(sys.argv[1:])
