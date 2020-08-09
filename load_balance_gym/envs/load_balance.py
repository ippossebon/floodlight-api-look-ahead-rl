import gym
from gym import error, spaces, utils
from gym.utils import seeding

import pandas
import numpy

# Based on the folllwing tutorials:
# https://towardsdatascience.com/creating-a-custom-openai-gym-environment-for-stock-trading-be532be3910e
# https://machinelearningmastery.com/tutorial-first-neural-network-python-keras/

LINK_CAPACITY = 1000 # TODO: update links capacity when generating network on mininet

class LoadBalanceEnv(gym.Env):
    metadata = {'render.modes': ['human']}

    def __init__(self, usage):
        super(LoadBalanceEnv, self).__init__()

        self.initial_usage = usage

        # Initial state = initial links usage
        self.state = numpy.array(usage)

        self.switches = ['S1', 'S2', 'S3', 'S4', 'S5']
        self.links = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i']
        self.topology = {
            'S1': ['b', 'c'], # links between switches,
            'S2': ['b', 'd', 'e', 'f'],
            'S3': ['f', 'g', 'h', 'i'],
            'S4': ['c', 'e', 'g'],
            'S5': ['d', 'h']
        }

        self.possible_paths = [
            ['a', 'b', 'd', 'h', 'i'],
            ['a', 'b', 'f', 'i'],
            ['a', 'b', 'e', 'g', 'i'],
            ['a', 'c', 'g', 'i'],
            ['a', 'c', 'e', 'd', 'h', 'i'],
            ['a', 'c', 'e', 'f', 'i']
        ]

        ### Information about network flows
        self.active_flows = []
        self.flow_paths = {} # dict on format self.flow_paths['flow_id'] = []
        self.flow_size = {}

        # State = Links usage as [link_A_usage, link_B_usage, link_C_usage, link_D_usage, ..., link_I_usage]
        self.observation_space = spaces.Box(
            low=0,
            high=LINK_CAPACITY, # max link usage: # TODO: check if it's ok!
            shape=(1, len(self.links)), # array of link usage: [link_A_usage, link_B_usage, link_C_usage, link_D_usage, ..., link_I_usage]
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

        # Possible actions: 11 possible paths combinatios - check step function
        self.action_space = spaces.Discrete(11)

        # TODO: still testing reward results
        # If network usage became MORE homogeneous, recompensa = 1
        # If network usage became LESS homogeneous, recompensa = 0
        self.reward_range = (0, 1)

    def addFlow(self, flow_id, flow_size):
        if flow_id not in self.active_flows:
            self.active_flows.append(flow_id)

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

        return numpy.array(self.initial_usage)


    # flow_total_size is the flow total size over which the action will be applied
    # flow_current_paths indicates which are the paths used by the flow currently
    def step(self, action, flow_total_size, flow_current_paths):
        done = False # Aprendizado continuado

        # Execute one time step within the environment
        # It will take an action variable and will return a list of four things:
        # the next state, the reward for the current state, a boolean representing
        # whether the current episode of our model is done and some additional info on our problem.
        # flow_index = action[0]

        total_usage = numpy.sum(self.state)
        next_state = []
        next_paths = []

        # action corresponde ao switch sobre o qual vamos agir, isto é: S1, S2, S3, S4 ou S5
        if action == 0:
            # do nothing: void action - Important so the agent could choose to simply keep going.
            # This is used because we work with "continued learning" = there's no "done" state.
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

        # Update state
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
            print('####### --> [getLinkIndex] ValueError: link = {0}, ASCII = {1}, self.links = {2}'.format(link, link.encode('ascii'), self.links))
            return -1


    def generateNextState(self, total_usage, action_to_apply, flow_total_size, flow_current_paths):
        # Updates status based on the chosen action
        next_state = self.state.tolist()
        next_paths = []

        # Reset previous usage
        next_state = self.resetPreviousPathsUsage(flow_current_paths, flow_total_size)

        if action_to_apply == 1:
            # "Splits" flow on S1
            next_paths.append(['a', 'c', 'g', 'i'])
            next_paths.append(['a', 'b', 'f', 'i'])

            # Because we removed all the usage from previous paths, we need to
            # put the values of the current flow in all the new paths
            next_state[0] += flow_total_size # A
            next_state[1] += flow_total_size/2 # B
            next_state[2] += flow_total_size/2 # C
            next_state[5] += flow_total_size/2 # F
            next_state[6] += flow_total_size/2 # G
            next_state[8] += flow_total_size # I

        elif action_to_apply == 2:
            # "Split" on S2 using two paths (flow came in through B, came out through D and E)
            next_paths.append(['a', 'b', 'd', 'h', 'i'])
            next_paths.append(['a', 'b', 'e', 'g', 'i'])

            next_state[0] += flow_total_size # A
            next_state[1] += flow_total_size # B
            next_state[3] += flow_total_size/2 # D
            next_state[4] += flow_total_size/2 # E
            next_state[6] += flow_total_size/2 # G
            next_state[7] += flow_total_size/2 # H
            next_state[8] += flow_total_size # I

        elif action_to_apply == 3:
            next_paths.append(['a', 'b', 'f', 'i'])

            next_state[0] += flow_total_size # A
            next_state[1] += flow_total_size # B
            next_state[5] += flow_total_size # F
            next_state[8] += flow_total_size # I

        elif action_to_apply == 4:
            # "Split" on S4 using two paths (flow came in through C)
            next_paths.append(['a', 'c', 'g', 'i'])
            next_paths.append(['a', 'c', 'e', 'f', 'i'])

            next_state[0] += flow_total_size # A
            next_state[2] += flow_total_size # C
            next_state[4] += flow_total_size/2 # E
            next_state[5] += flow_total_size/2 # F
            next_state[6] += flow_total_size/2 # G
            next_state[8] += flow_total_size # I

        elif action_to_apply == 5:
            next_paths.append(['a', 'c', 'g', 'i'])

            next_state[0] += flow_total_size # A
            next_state[2] += flow_total_size # C
            next_state[6] += flow_total_size # G
            next_state[8] += flow_total_size # I

        elif action_to_apply == 6:
            next_paths.append(['a', 'b', 'd', 'h', 'i'])

            next_state[0] += flow_total_size # A
            next_state[1] += flow_total_size # B
            next_state[3] += flow_total_size # D
            next_state[7] += flow_total_size # H
            next_state[8] += flow_total_size # I

        elif action_to_apply == 7:
            next_paths.append(['a', 'b', 'e', 'g', 'i'])

            next_state[0] += flow_total_size # A
            next_state[1] += flow_total_size # B
            next_state[4] += flow_total_size # E
            next_state[6] += flow_total_size # G
            next_state[8] += flow_total_size # I

        elif action_to_apply == 8:
            next_paths.append(['a', 'c', 'e', 'd', 'h', 'i'])

            next_state[0] += flow_total_size # A
            next_state[2] += flow_total_size # C
            next_state[3] += flow_total_size # D
            next_state[4] += flow_total_size # E
            next_state[7] += flow_total_size # H
            next_state[8] += flow_total_size # I

        elif action_to_apply == 9:
            next_paths.append(['a', 'c', 'e', 'f', 'i'])

            next_state[0] += flow_total_size # A
            next_state[2] += flow_total_size # C
            next_state[4] += flow_total_size # E
            next_state[5] += flow_total_size # F
            next_state[8] += flow_total_size # I

        elif action_to_apply == 10:
            # "Split" on S3 using three paths (flow came in through B, came out through D, E and F)
            next_paths.append(['a', 'b', 'd', 'h', 'i'])
            next_paths.append(['a', 'b', 'e', 'g', 'i'])
            next_paths.append(['a', 'b', 'f', 'i'])

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


    # Reset previous paths usage
    def resetPreviousPathsUsage(self, previous_paths, flow_size):
        new_usage = self.state.tolist()
        for path in previous_paths:
            for link in path:
                link_index = self.getLinkIndex(link.strip()) # strip() necessary to remove \x1d characters
                new_usage[link_index] = self.state[link_index] - flow_size

        return new_usage


    def calculateReward(self, next_state):
        # # TODO: still testing if this is the right reward function. The agent is now chosing minimum rewards

        # state is usage link list
        # [ 100, 20, 0, 10, 100, 20, 0, 10, 10 ]
        # print('next_state = ', next_state)

        np_next_usage = numpy.array(next_state)
        # print('np_next_usage = ', np_next_usage)
        mean_next_usage = numpy.mean(np_next_usage)
        # print('mean_next_usage = ', mean_next_usage)

        std_next_usage = numpy.std(np_next_usage)
        # print('std_next_usage = ', std_next_usage)

        # Recompensa = 1 / desvio_padrao_soma_utilizacao_rede
        # Quanto menor for o desvio padrão da utilização da rede, maior será a recompensa
        reward = (std_next_usage and 1 / float(std_next_usage)) * 1000 or 0
        # print('reward = ', rewa111rd)

        return reward
