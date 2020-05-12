import gym
from gym import error, spaces, utils
from gym.utils import seeding

# from keras.models import Sequential
# from keras.layers import Dense

import pandas
import numpy

# based on tutorial from: https://towardsdatascience.com/creating-a-custom-openai-gym-environment-for-stock-trading-be532be3910e

# tutorial importante: https://machinelearningmastery.com/tutorial-first-neural-network-python-keras/

LINK_CAPACITY = 1000 # TODO: confirmar capacidade maxima do link

class LoadBalanceEnv(gym.Env):
    metadata = {'render.modes': ['human']}

    def __init__(self, usage):
        super(LoadBalanceEnv, self).__init__()

        self.initial_usage = usage

        # Estado inicial = utilização de cada link
        self.state = numpy.array(usage)

        self.switches = ['S1', 'S2', 'S3', 'S4', 'S5']
        # self.links = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I']
        self.links = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I']
        self.topology = {
            'S1': ['B', 'C'], # links entre switches,
            'S2': ['B', 'D', 'E', 'F'],
            'S3': ['F', 'G', 'H', 'I'],
            'S4': ['C', 'E', 'G'],
            'S5': ['D', 'H']
        }

        self.possible_paths = [
            ['A', 'B', 'D', 'H', 'I'],
            ['A', 'B', 'F', 'I'],
            ['A', 'B', 'E', 'G', 'I'],
            ['A', 'C', 'G', 'I'],
            ['A', 'C', 'E', 'D', 'H', 'I'],
            ['A', 'C', 'E', 'F', 'I']
        ]

        ### Conjunto de informações sobre os fluxos da rede
        self.active_flows = []
        self.flow_paths = {} # dicionario no formato self.flow_paths['flow_id'] = []
        self.flow_size = {}

        # Utilização dos links da rede
        self.observation_space = spaces.Box(
            low=0,
            high=LINK_CAPACITY, # utilização maxima do link
            shape=(1, len(self.links)), # é um array de utilização dos links
            dtype=numpy.float16
        )

        # A ação é escolher o switch sobre o qual vai agir. Isto é, o switch que
        # terá o fluxo dividido entre 2 caminhos + 1 ação void
        # self.action_space = spaces.Discrete(len(self.switches) + 1) # array com o índice do switch sobre o qual vamos agir
        # self.action_space = spaces.Box(
        #     shape=(1, 2), # é um array no formato [flow_index, switch_index], flow_index indica o fluxo que deve ser alterado
        #     # Valor mínimos são 0 pois é o primeiro índice possível
        #     low=numpy.array([0, 0]),
        #     # valor máximo de flow_index é 4, pois podemos ter até 5 flows em paralelo.
        #     # 9 ações possíveis + 1 ação void = 10 acoes possiveis, entao o maior indice é 9
        #     high=numpy.array([MAX_ACTIVE_FLOWS-1, 9]),
        #     dtype=numpy.uint8
        # )
        # 9 ações possíveis + 1 ação void = 10 acoes possiveis, entao o maior indice é 9

        self.action_space = spaces.Discrete(11)

        # Se tornou o uso da rede MAIS homogêneo, recompensa = 1
        # Se tornou o uso da rede MENOS homogêneo, recompensa = 0
        self.reward_range = (0, 1)

    def addFlow(self, flow_id, flow_size):
        if flow_id not in self.active_flows:
            self.active_flows.append(flow_id)

            # Inicializa dicionario onde será armazenado os caminhos pelo quais o fluxo está passando
            self.flow_paths[flow_id] = []

            self.flow_size[flow_id] = flow_size

    def removeFlow(self, flow_id):
        self.active_flows.remove(flow_id)
        self.flow_paths[flow_id] = []

    def addPathToFlow(self, flow_id, path_index):
        self.flow_paths[flow_id].append(path_index)

    def removePathFromFlow(self, flow_id, path_index):
        self.flow_paths[flow_id].remove(path_index)

    def reset(self):
        """
         - Reset the state of the environment to an initial state
        It  will be called to periodically reset the environment to an initial
        state. This is followed by many steps through the environment, in which
        an action will be provided by the model and must be executed, and the next
        observation returned. This is also where rewards are calculated, more on this later.

        - Called any time a new environment is created or to reset an existing environment’s state.
        """
        # Reset the state of the environment to an initial state

        return numpy.array(self.initial_usage)


    # flow_total_size corresponde ao tamanho do fluxo sobre o qual a ação será aplicada
    # flow_current_paths indica quais sao os caminhos usados pelo fluxo atualmente
    def step(self, action, flow_total_size, flow_current_paths):
        done = False # Aprendizado continuado

        # Execute one time step within the environment
        # It will take an action variable and will return a list of four things:
        # the next state, the reward for the current state, a boolean representing
        # whether the current episode of our model is done and some additional info on our problem.
        # flow_index = action[0]

        # Pega o que temos nos links que saem de S1 e divide entre output_link1 e output_link2
        total_usage = numpy.sum(self.state)
        next_state = []
        next_paths = []

        # action corresponde ao switch sobre o qual vamos agir, isto é: S1, S2, S3, S4 ou S5
        if action == 0:
            # não faz nada
            next_state = numpy.array(self.state)
            next_paths = flow_current_paths
        else:
            next_state, next_paths = self.generateNextState(
                total_usage=total_usage,
                action_to_apply=action,
                flow_total_size=flow_total_size,
                flow_current_paths=flow_current_paths
            )

        previous_state = numpy.array(self.state)
        reward = self.calculateReward(next_state)

        # Atualiza estado
        self.state = numpy.array(next_state)

        # It will take an action variable and will return a list of four things:
        # the next state, the reward for the current state, a boolean representing
        # whether the current episode of our model is done and some additional info on our problem.
        return next_state, reward, done, { 'next_paths': next_paths }


    def getPathIndex(self, path):
        return self.possible_paths.index(path)

    def getFlowIndex(self, flow_id):
        return self.active_flows.index(flow_id)

    def getLinkIndex(self, link):
        try:
            return self.links.index(link.strip())
        except ValueError:
            print('####### --> [getLinkIndex] ValueError: link = {0}, ASCII = {1} #######'.format(link, link.encode('ascii')))
            return -1


    def generateNextState(self, total_usage, action_to_apply, flow_total_size, flow_current_paths):
        # Atualiza estado com base na ação que foi escolhida
        next_state = self.state.tolist()
        next_paths = []

        # Zera utilização anterior
        next_state = self.resetPreviousPathsUsage(flow_current_paths, flow_total_size)

        if action_to_apply == 1:
            # Split do fluxo em S1
            next_paths.append(['A', 'C', 'G', 'I'])
            next_paths.append(['A', 'B', 'F', 'I'])

            # Tiramos toda a utilização dos caminhos anteriores, precisamos
            # colocar os valores do fluxo atual em todos os novos caminhos

            next_state[0] += flow_total_size # A
            next_state[1] += flow_total_size/2 # B
            next_state[2] += flow_total_size/2 # C
            next_state[5] += flow_total_size/2 # F
            next_state[6] += flow_total_size/2 # G
            next_state[8] += flow_total_size # I

        elif action_to_apply == 2:
            # Split em S2 por 2 caminhos (chegou por B, saiu por D e E)
            next_paths.append(['A', 'B', 'D', 'H', 'I'])
            next_paths.append(['A', 'B', 'E', 'G', 'I'])

            next_state[0] += flow_total_size # A
            next_state[1] += flow_total_size # B
            next_state[3] += flow_total_size/2 # D
            next_state[4] += flow_total_size/2 # E
            next_state[6] += flow_total_size/2 # G
            next_state[7] += flow_total_size/2 # H
            next_state[8] += flow_total_size # I

        elif action_to_apply == 3:
            next_paths.append(['A', 'B', 'F', 'I'])

            next_state[0] += flow_total_size # A
            next_state[1] += flow_total_size # B
            next_state[5] += flow_total_size # F
            next_state[8] += flow_total_size # I

        elif action_to_apply == 4:
            # Spit em S4 (chegou por C e saiu por dois caminhos diferentes)
            next_paths.append(['A', 'C', 'G', 'I'])
            next_paths.append(['A', 'C', 'E', 'F', 'I'])

            next_state[0] += flow_total_size # A
            next_state[2] += flow_total_size # C
            next_state[4] += flow_total_size/2 # E
            next_state[5] += flow_total_size/2 # F
            next_state[6] += flow_total_size/2 # G
            next_state[8] += flow_total_size # I

        elif action_to_apply == 5:
            next_paths.append(['A', 'C', 'G', 'I'])

            next_state[0] += flow_total_size # A
            next_state[2] += flow_total_size # C
            next_state[6] += flow_total_size # G
            next_state[8] += flow_total_size # I

        elif action_to_apply == 6:
            next_paths.append(['A', 'B', 'D', 'H', 'I'])

            next_state[0] += flow_total_size # A
            next_state[1] += flow_total_size # B
            next_state[3] += flow_total_size # D
            next_state[7] += flow_total_size # H
            next_state[8] += flow_total_size # I

        elif action_to_apply == 7:
            next_paths.append(['A', 'B', 'E', 'G', 'I'])

            next_state[0] += flow_total_size # A
            next_state[1] += flow_total_size # B
            next_state[4] += flow_total_size # E
            next_state[6] += flow_total_size # G
            next_state[8] += flow_total_size # I

        elif action_to_apply == 8:
            next_paths.append(['A', 'C', 'E', 'D', 'H', 'I'])

            next_state[0] += flow_total_size # A
            next_state[2] += flow_total_size # C
            next_state[3] += flow_total_size # D
            next_state[4] += flow_total_size # E
            next_state[7] += flow_total_size # H
            next_state[8] += flow_total_size # I

        elif action_to_apply == 9:
            next_paths.append(['A', 'C', 'E', 'F', 'I'])

            next_state[0] += flow_total_size # A
            next_state[2] += flow_total_size # C
            next_state[4] += flow_total_size # E
            next_state[5] += flow_total_size # F
            next_state[8] += flow_total_size # I

        elif action_to_apply == 10:
            # Split em S2 por 3 caminhos (chegou por B, saiu por D, E e F)
            next_paths.append(['A', 'B', 'D', 'H', 'I'])
            next_paths.append(['A', 'B', 'E', 'G', 'I'])
            next_paths.append(['A', 'B', 'F', 'I'])

            next_state[0] += flow_total_size # A
            next_state[1] += flow_total_size # B
            next_state[3] += flow_total_size/3 # D
            next_state[4] += flow_total_size/3 # E
            next_state[5] += flow_total_size/3 # F
            next_state[6] += flow_total_size/3 # G
            next_state[7] += flow_total_size/3 # H
            next_state[8] += flow_total_size # I

        else:
            print ('Error: invalid action type [generateNextState]: ', action_to_apply)
            exit(0)

        return numpy.array(next_state), next_paths


    # Remove utilização do fluxo dos caminhos anteriores
    def resetPreviousPathsUsage(self, previous_paths, flow_size):
        new_usage = self.state.tolist()
        for path in previous_paths:
            for link in path:
                link_index = self.getLinkIndex(link.strip()) # strip() necessary to remove \x1d characters
                new_usage[link_index] = self.state[link_index] - flow_size

        return new_usage


    def calculateReward(self, next_state):
        # state is usage link list
        # [ 100, 20, 0, 10, 100, 20, 0, 10, 10 ]
        np_next_usage = numpy.array(next_state)
        mean_next_usage = numpy.mean(np_next_usage)
        std_next_usage = numpy.std(np_next_usage)

        # Recompensa = 1 / desvio_padrao_soma_utilizacao_rede
        # Quanto menor for o desvio padrão da utilização da rede, maior será a recompensa
        reward = (std_next_usage and 1 / float(std_next_usage)) or 0

        return reward
