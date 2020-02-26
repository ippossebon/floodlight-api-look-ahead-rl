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

class LoadBalanceEnv(gym.Env):
    metadata = {'render.modes': ['human']}

    def __init__(self, usage):
        super(LoadBalanceEnv, self).__init__()

        self.initial_usage = usage

        self.switches = ['S1', 'S2', 'S3', 'S4', 'S5']
        self.links = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I']
        self.topology = {
            'S1': ['B', 'C'], # links entre switches,
            'S2': ['B', 'D', 'E', 'F'],
            'S3': ['F', 'G', 'H', 'I'],
            'S4': ['C', 'E', 'G'],
            'S5': ['D', 'H']
        }

        # Estado inicial = utilização de cada link
        self.usage = usage

        self.possible_routes = [
            ['B', 'D', 'H', 'I'],
            ['B', 'F', 'I'],
            ['B', 'E', 'G', 'I'],
            ['C', 'G', 'I'],
            ['C', 'E', 'D', 'H', 'I'],
            ['C', 'E', 'F', 'I']
        ]

        # Utilização dos links da rede
        self.observation_space = spaces.Box(
            low=0,
            high=LINK_CAPACITY, # utilização maxima do link
            shape=(1, len(self.links)), # é um array de utilização dos links
            dtype=numpy.float16
        )

        # A ação é escolher o switch sobre o qual vai agir. Isto é, o switch que
        # terá o fluxo dividido entre 2 caminhos + 1 ação void
        self.action_space = spaces.Discrete(len(self.switches) + 1) # array com o índice do switch sobre o qual vamos agir

        # Considenrando que action seria um array de coisas
        # self.action_space = spaces.Box(
        #     low=np.array([-1, -1, -1]), # -1 indica que nada deve ser feito
        #     high=np.array([max_switch_id, -1, -1]), # # TODO: rever
        #     shape=(3, 1), # [switch_id, link_saida1, link_saida2] shape=(3,1) = 1 linha, 3 colunas
        #     dtype=numpy.uint8
        # )

        # Se tornou o uso da rede MAIS homogêneo, recompensa = 1
        # Se tornou o uso da rede MENOS homogêneo, recompensa = 0
        self.reward_range = (0, 1)

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
        self.usage = self.initial_usage

        # Set the current step to a random point within the data frame
        # We set the current step to a random point within the data frame, because
        # it essentially gives our agent’s more unique experiences from the same data set.
        # The _next_observation method compiles the stock data for the last five time steps,
        # appends the agent’s account information, and scales all the values to between 0 and 1

        # self.current_step = random.randint(0, len(self.df.loc[:, 'Open'].values) - 6)
        # self.current_step = random.randint(0, len(self.dataframe))

        # self.createNeuralNetworkModel()
        return self.usage

    def createNeuralNetworkModel(self):
        # Cria rede neural
        """
        The model expects rows of data with 6 variables (the input_dim=6 argument)
        The first hidden layer has 12 nodes and uses the relu activation function.
        The second hidden layer has 8 nodes and uses the relu activation function.
        The output layer has 6 nodes and uses the sigmoid activation function.
        """
        self.nn_model = Sequential()
        # Vamos usar fully conected layers, por isso estamos usando Dense.
        # We can specify the number of neurons or nodes in the layer as the first argument, and specify the activation function using the activation argument.
        self.nn_model.add(Dense(12, input_dim=6, activation='relu')) # input_dim=6 pois temos 6 inputs
        self.nn_model.add(Dense(8, activation='relu'))
        self.nn_model.add(Dense(6, activation='sigmoid')) # precisamos de 6 saídas; usamos Sigmoid como função de ativação para que a saída esteja entre 0 e 1.

        # compile the keras model
        #  metrics=['accuracy']
        model.compile(loss='binary_crossentropy', optimizer='adam')

        # Training occurs over epochs and each epoch is split into batches.
        # Epoch: One pass through all of the rows in the training dataset.
        # Batch: One or more samples considered by the model within an epoch before weights are updated.

        # treinamento nao supervisionado
        history = model.fit(
            self.training_set, # será o meu dataframe
            self.training_set, # será o meu dataframe
            epochs=EPOCHS,
            validation_data=[self.validation_set, self.validation_set]
        )


    def step(self, action):
        done = False # Aprendizado continuado

        # Execute one time step within the environment
        # It will take an action variable and will return a list of four things:
        # the next state, the reward for the current state, a boolean representing
        # whether the current episode of our model is done and some additional info on our problem.
        switch_id = action

        # Pega o que temos nos links que saem de S1 e divide entre output_link1 e output_link2
        total_usage = sum(self.usage)
        next_state = []

        # action corresponde ao switch sobre o qual vamos agir, isto é: S1, S2, S3, S4 ou S5
        if switch_id == 0:
            # não faz nada
            next_state = list(self.usage)

        elif switch_id == 1:
            # Atua sobre S1
            # Atualmente, estamos ignorando output_link1 e output_link2, e dividindo entre 2 os fluxos
            next_state = self.generateNextState(total_usage, 0)

        elif switch_id == 2:
            # Atua sobre S2
            next_state = self.generateNextState(total_usage, 1)

        elif switch_id == 3:
            # Atua sobre S3
            next_state = self.generateNextState(total_usage, 2)

        elif switch_id == 4:
            # Atua sobre S4
            next_state = self.generateNextState(total_usage, 3)

        elif switch_id == 5:
            # Atua sobre S5
            next_state = self.generateNextState(total_usage, 4)

        else:
            print('Erro: switch_id = ', switch_id)
            exit(0)


        previous_state = list(self.usage)
        reward = self.calculateReward(next_state)

        # Atualiza estado
        self.usage = list(next_state)

        # It will take an action variable and will return a list of four things:
        # the next state, the reward for the current state, a boolean representing
        # whether the current episode of our model is done and some additional info on our problem.
        return next_state, reward, done, {}


    def generateNextState(self, total_usage, switch_array_index): # switch_array_index
        # Atualiza estado
        next_state = list(self.usage)
        switch_id = self.switches[switch_array_index]
        available_links_count = len(self.topology[switch_id])

        total_switch_links_usage = 0

        for link_index in range(len(self.links)):
            if self.links[link_index] in self.topology[switch_id]:
                # Se o link está associado ao switch em questao, contabiliza sua utilização
                total_switch_links_usage += self.usage[link_index]

                # deve atualizar o valor utilizado
                # divide a carga entre todos os links do switch
                next_state[link_index] = (total_usage and float(total_usage/available_links_count)) or 0

        # print('next_state = ', next_state)
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
