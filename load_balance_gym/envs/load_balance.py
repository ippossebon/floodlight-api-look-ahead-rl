import gym
from gym import error, spaces, utils
from gym.utils import seeding

from keras.models import Sequential
from keras.layers import Dense

import pandas
import numpy

# based on tutorial from: https://towardsdatascience.com/creating-a-custom-openai-gym-environment-for-stock-trading-be532be3910e

# tutorial importante: https://machinelearningmastery.com/tutorial-first-neural-network-python-keras/

DATAFRAME_FILE = './dataframe/dataframe-h1-client-h2-server-usage-rate.csv'

LINK_CAPACITY = 1000 # TODO: confirmar capacidade maxima do link
MAX_ACTIVE_FLOWS = 5

class LoadBalanceEnv(gym.Env):
    metadata = {'render.modes': ['human']}

    def __init__(self, usage):
        super(LoadBalanceEnv, self).__init__()

        self.initial_usage = usage
        # Estado inicial = utilização de cada link
        self.usage = usage

        self.switches = ['S1', 'S2', 'S3', 'S4', 'S5']
        self.links = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I']
        self.topology = {
            'S1': ['B', 'C'], # links entre switches,
            'S2': ['B', 'D', 'E', 'F'],
            'S3': ['F', 'G', 'H', 'I'],
            'S4': ['C', 'E', 'G'],
            'S5': ['D', 'H']
        }

        self.possible_paths = [
            ['A', 'B', 'D', 'H', 'I'],
            ['A', 'B', 'F', 'I'],
            ['A', 'B', 'E', 'G', 'I'],
            ['A', 'C', 'G', 'I'],
            ['A', 'C', 'E', 'D', 'H', 'I'],
            ['A', 'C', 'E', 'F', 'I']
        ]

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
        self.action_space = spaces.Box(
            shape=(1, 2), # é um array no formato [flow_index, switch_index], flow_index indica o fluxo que deve ser alterado
            # Valor mínimos são 0 pois é o primeiro índice possível
            low=np.array([0, 0]),
            # valor máximo de flow_index é 4, pois podemos ter até 5 flows em paralelo.
            # Valor máximo de switch_index é 5, pois temos 5 switches na topologia + 1 ação void
            high=np.array([MAX_ACTIVE_FLOWS-1, len(self.switches)),
            dtype=numpy.uint8
        )

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
        self.usage = list(self.initial_usage)

        return self.usage


    def step(self, action):
        done = False # Aprendizado continuado

        # Execute one time step within the environment
        # It will take an action variable and will return a list of four things:
        # the next state, the reward for the current state, a boolean representing
        # whether the current episode of our model is done and some additional info on our problem.
        flow_index = action[0]
        switch_action_id = action[1]

        # Pega o que temos nos links que saem de S1 e divide entre output_link1 e output_link2
        total_usage = sum(self.usage)
        next_state = []

        # action corresponde ao switch sobre o qual vamos agir, isto é: S1, S2, S3, S4 ou S5
        if switch_action_id == 0:
            # não faz nada
            next_state = list(self.usage)

        elif switch_action_id == 1:
            # Atua sobre S1
            next_state = self.generateNextState(
                total_usage=total_usage,
                switch_array_index=0,
                flow_index=flow_index
            )

        elif switch_action_id == 2:
            # Atua sobre S2
            next_state = self.generateNextState(
                total_usage=total_usage,
                switch_array_index=1,
                flow_index=flow_index
            )

        elif switch_action_id == 3:
            # Atua sobre S3
            next_state = self.generateNextState(
                total_usage=total_usage,
                switch_array_index=2,
                flow_index=flow_index
            )

        elif switch_action_id == 4:
            # Atua sobre S4
            next_state = self.generateNextState(
                total_usage=total_usage,
                switch_array_index=3,
                flow_index=flow_index
            )

        elif switch_action_id == 5:
            # Atua sobre S5
            next_state = self.generateNextState(
                total_usage=total_usage,
                switch_array_index=4,
                flow_index=flow_index
            )

        else:
            print('Error: invalid switch_id = ', switch_id)
            exit(0)

        previous_state = list(self.usage)
        reward = self.calculateReward(next_state)

        # Atualiza estado
        self.usage = list(next_state)

        # It will take an action variable and will return a list of four things:
        # the next state, the reward for the current state, a boolean representing
        # whether the current episode of our model is done and some additional info on our problem.
        return next_state, reward, done, {}


    def getPathIndex(self, path):
        return self.possible_paths.index(path)

    def getFlowIndex(self, flow_id):
        return self.active_flows.index(flow_id)

    def getLinkIndex(self, link):
        return self.links.index(link) or -1

    def generateNextState(self, total_usage, switch_array_index, flow_index): # switch_array_index
        # Atualiza estado com base na ação que foi escolhida (switch_array_index
        # corresponde ao switch sobre o qual vamos atuar)
        next_state = list(self.usage)
        switch_id = self.switches[switch_array_index]
        path1 = []
        path2 = []

        if switch_id == 'S1':
            # split de fluxo em S1
            path1 = ['A', 'C', 'G', 'I']
            path2 = ['A', 'B', 'F', 'I']

        elif switch_id == 'S2':
            # split de fluxo em S2
            path1 = ['A', 'B', 'D', 'H', 'I']
            path2 = ['A', 'B', 'E', 'G', 'I']

        elif switch_id == 'S3':
            # mantem no mesmo caminho (não existe caminho alternativo que mexa apenas em S3)
            return next_state

        elif switch_id == 'S4':
            # split de fluxo em S4
            path1 = ['A', 'C', 'G', 'I']
            path2 = ['A', 'C', 'E', 'F', 'I']

        elif switch_id == 'S5':
            # mantem no mesmo caminho (não existe caminho alternativo que mexa apenas em S5)
            return next_state
        else:
            print ('Error: invalid switch id [generateNextState]: ', switch_id)
            exit(0)

        path1_index = self.getPathIndex(path1)
        path2_index = self.getPathIndex(path2)

        # Pega os caminhos anteriores utilizados, para atulizar o estado
        previous_paths = self.flow_paths[flow_id]

        # Altera caminhos utilizados pelo fluxo
        flow_id = self.active_flows[flow_index]
        self.flow_paths[flow_id] = [path1_index, path2_index]


        # Para cada caminho utilizado anteriormente, remove utilização dos links anteriores
        for p in previous_paths:
            previous_path_index = p
            previous_path = self.possible_paths[previous_path_index]

            # Remove utilização do link dos caminhos anteriores:
            flow_size = self.flow_size[flow_id]
            for link in previous_path:
                link_index = self.getLinkIndex(link)
                next_state[link_index] = self.usage[link_index] - flow_size

        # Seleciona links da diferença dos caminhos
        # [A, B, D, H, I] - [A, C, G, I] = [B, C, D, G, H]
        links_to_split = path1 - path2 # links que precisam ter sua utilização dividida em 2
        links_to_keep = list(set(path1).intersection(path2)) # links que usam a quantidade total de fluxo
        for link in links_to_keep:
            link_index = self.getLinkIndex(link)
            next_state[link_index] = self.usage[link_index] + flow_size

        for link in links_to_split:
            link_index = self.getLinkIndex(link)
            next_state[link_index] = self.usage[link_index] + (flow_size/2)

        return next_state


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
