from load_balance_gym.envs.load_balance_floodlight_costly_flow_s10 import LoadBalanceEnvDiscAction

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
    model.learn(total_timesteps=10000)
    model.save('./trained-agents/' + agent)
    print('Modelo treinado e salvo.')


def testAgent(env, original_env, agent, num_flows, flows_size, timesteps):
    # if agent == 'A-LA':
    #     # Na verdade, o agente C1 é o A1 com o if. Não é necessário treinar outro
    #     agent = 'A'

    agent_path = 'trained-agents/{0}'.format(agent)
    model = DQN.load(load_path=agent_path, env=env)

    state = env.reset()
    num_steps = int(timesteps)

    writeLineToFile('Step; State; Reward', csv_output_filename)

    for step in range(num_steps):
        print('Step ', step)
        action, _ = model.predict(state, deterministic=False)
        state, reward, done, info = env.step(action)

        output_data_line = '{0}; {1}; {2}'.format(step, state, reward)
        writeLineToFile(output_data_line, csv_output_filename)
        step += 1

    # Com o IF, acho que preciso rodar com mais steps
    # for step in range(num_steps * 2):
    #     print('Step ', step)
    #     action, _ = model.predict(state, deterministic=False)
    #     contains_elephant_flow = containsElephantFlow(original_env)
    #     print('contains_elephant_flow: ', contains_elephant_flow)
    #     print('state = ', state)
    #
    #     if contains_elephant_flow:
    #         state, reward, done, info = env.step(action)
    #
    #         output_data_line = '{0}; {1}; {2}'.format(step, state, reward)
    #         writeLineToFile(output_data_line, csv_output_filename)
    #     step += 1



def writeLineToFile(line, filename):
    print(csv_output_filename)
    with open(filename, 'a') as file:
        file.write("%s\n" % line)

"""
Elephant flow detection
"""
def containsElephantFlow(env):
    return env.existsElephantFlow()


def getTopMemoryUsage(snapshot, key_type='lineno', limit=3):
    snapshot = snapshot.filter_traces((
        tracemalloc.Filter(False, "<frozen importlib._bootstrap>"),
        tracemalloc.Filter(False, "<unknown>"),
    ))
    top_stats = snapshot.statistics(key_type)

    # print("Top %s lines" % limit)
    for index, stat in enumerate(top_stats[:limit], 1):
        frame = stat.traceback[0]
        # replace "/path/to/module/file.py" with "module/file.py"
        filename = os.sep.join(frame.filename.split(os.sep)[-2:])
        # print("#%s: %s:%s: %.1f KiB"
        #       % (index, filename, frame.lineno, stat.size / 1024))
        line = linecache.getline(frame.filename, frame.lineno).strip()
        # if line:
            # print('    %s' % line)

    other = top_stats[limit:]
    if other:
        size = sum(stat.size for stat in other)
        print("%s other: %.1f KiB" % (len(other), size / 1024))
    total = sum(stat.size for stat in top_stats)
    total_allocated_size_kb = total / 1024
    # print("Total allocated size: %.1f KiB" % total_allocated_size_kb)

    return total_allocated_size_kb



def main(argv):
    global csv_output_filename
    start1 = datetime.datetime.now()

    try:
        opts, args = getopt.getopt(argv, "ha:n:s:t:i:", ["agent=", "numflows=", "flowsize=", "timesteps=", "iter="])
    except getopt.GetoptError:
        print ('run-experiments.py -a <agent> -n <numflows> -s <flowsize> -t <timesteps> -i <iter>')
        sys.exit(2)

    agent = None
    num_flows = None
    flows_size = None
    timesteps = None
    iter = None

    for opt, arg in opts:
        if opt == '-h':
            print ('run-experiments.py -a <agent> -n <numflows> -s <flowsize> -t <timesteps> -i <iter>')
            sys.exit()
        elif opt in ("-a", "--agent"):
            agent = arg
        elif opt in ("-n", "--numflows"):
            num_flows = arg
        elif opt in ("-s", "--flowsize"):
            flows_size = arg
        elif opt in ("-t", "--timesteps"):
            timesteps = arg
        elif opt in ("-i", "--iter"):
            iter = arg

    csv_output_filename = './output-experiments-app/{0}-{1}_flows-{2}-{3}_steps-v_{4}.csv'.format(
        agent, num_flows, flows_size, timesteps, iter
    )

    print('Running: agent = {0}, number of flows = {1}, flows size = {2}, timesteps = {3}, iter = {4}'.format(
        agent, num_flows, flows_size, timesteps, iter
    ))

    tracemalloc.start()
    start_time = datetime.datetime.now()

    env, original_env = createVectorizedEnv()

    # print('Inicia treinamento do agente.')
    # trainAgent(env, agent)

    print('Inicia execução do agente.')
    testAgent(env, original_env, agent, num_flows, flows_size, timesteps)


    time_interval = datetime.datetime.now() - start_time
    snapshot = tracemalloc.take_snapshot()
    memory_usage = getTopMemoryUsage(snapshot)

    output_filename_compcosts = './output-experiments-app/{0}-{1}_flows-{2}-{3}_steps-v_{4}-compcosts.txt'.format(
        agent, num_flows, flows_size, timesteps, iter
    )

    with open(output_filename_compcosts, 'w+') as output_file:
        output_file.write("%s\n" % time_interval)
        output_file.write("%s\n" % memory_usage)

    print('Arquivo {0} criado.'.format(output_filename_compcosts))



##################################################################################
if __name__ == "__main__":
    main(sys.argv[1:])
