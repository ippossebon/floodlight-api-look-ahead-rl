import gym
from gym import error, spaces, utils
from gym.utils import seeding

import numpy
import pandas
import requests

# Based on the folllwing tutorials:
# https://towardsdatascience.com/creating-a-custom-openai-gym-environment-for-stock-trading-be532be3910e
# https://machinelearningmastery.com/tutorial-first-neural-network-python-keras/

LINK_CAPACITY = 1000 # TODO: update links capacity when generating network on mininet

CONTROLLER_IP = 'http://0.0.0.0'
CONTROLLER_HOST = '{host}:8080'.format(host=CONTROLLER_IP)
LLDP_PACKAGE_SIZE = 60
NUM_PORTS = 16

class LoadBalanceEnv(gym.Env):
    metadata = {'render.modes': ['human']}

    def __init__(self, num_flows, source_port, source_switch, target_port, target_switch):
        # Quero acomodar N fluxos na rede. Como?
        super(LoadBalanceEnv, self).__init__()

        self.num_flows = num_flows # exemplo = 5
        self.src_port = source_port
        self.dst_port = target_port
        # TODO: vou precisar dos ids dos fluxos
        # TODO: será que o if de fluxos vai ficar aqui dentro?

        # For debugging!
        self.links_map = {
            'b': {'00:00:00:00:00:00:00:01' : '2'},
            'c': {'00:00:00:00:00:00:00:01' : '3'},
            'd': {'00:00:00:00:00:00:00:02' : '2'},
            'e': {'00:00:00:00:00:00:00:04' : '2'},
            'f': {'00:00:00:00:00:00:00:02' : '3'},
            'g': {'00:00:00:00:00:00:00:04' : '3'},
            'h': {'00:00:00:00:00:00:00:05' : '3'},
            'i': {'00:00:00:00:00:00:00:03' : '1'}
        }

        self.switch_ids = []
        self.discoverTopology()
        self.discoverPossiblePaths(src_switch=self.switch_ids[source_switch], dst_switch=self.switch_ids[target_switch]) # posso assumir que sempre saio de H1 para H2


        # State = Links usage as [link_A_usage, link_B_usage, link_C_usage, link_D_usage, ..., link_I_usage]
        self.observation_space = spaces.Box(
            low=0,
            high=LINK_CAPACITY,
            shape=(1, self.num_ports), # array com o RX de cada porta
            dtype=numpy.float16
        )

        # Ação = (flow, caminho)
        self.action_space = spaces.Box(
            low=numpy.array([0, 0]), # primeiro indica o valor mais baixo para o fluxo. segundo = valor mais baixo para caminho
            high=numpy.array([self.num_flows-1, len(self.possible_paths)-1]), # primeiro: maior indice do fluxo, maior indice do caminho
            shape=(1, 2), # array com o RX de cada porta -> 1 linha e duas colunas = tupla
            dtype=numpy.int16 # cada caminho possivel
        )

        self.reward_range = (0, 1)

    def discoverTopology(self):
        response = requests.get('{host}/wm/topology/links/json'.format(
            host=CONTROLLER_HOST
        ))
        response_data = response.json()
        switch_ports = {}

        # Guarda mapeamento de switches e portas
        for item in response_data:
            switch_id = item['src-switch']
            if switch_id not in switch_ports.keys():
                switch_ports[switch_id] = []
            else:
                port = item['src-port']
                if port not in switch_ports[switch_id]:
                    switch_ports[switch_id].append(port)

            switch_id = item['dst-switch']
            if switch_id not in switch_ports.keys():
                switch_ports[switch_id] = []
            else:
                port = item['dst-port']
                if port not in switch_ports[switch_id]:
                    switch_ports[switch_id].append(port)

            # Guarda IDs de switches
            if item['src-switch'] not in self.switch_ids:
                self.switch_ids.append(item['src-switch'])
            if item['dst-switch'] not in self.switch_ids:
                self.switch_ids.append(item['dst-switch'])

        # print('Switch IDs: ', self.switch_ids)
        self.switch_ids = sorted(self.switch_ids)

        num_ports_aux = 0
        for switch_id in switch_ports:
            num_ports_aux += len(switch_ports[switch_id])

        num_ports_aux += 2 # portas dos hosts
        # print('Numero de portas calculadas: ', num_ports_aux)

        self.num_ports = NUM_PORTS # fixo neste primeiro momento
        self.ports: {
            'S1.1': 0,
            'S1.2': 1,
            'S1.3': 2,
            'S2.1': 3,
            'S2.2': 4,
            'S2.3': 5,
            'S2.4': 6,
            'S3.1': 7,
            'S3.2': 8,
            'S3.3': 9,
            'S3.4': 10,
            'S4.1': 11,
            'S4.2': 12,
            'S4.3': 13,
            'S5.1': 14,
            'S5.2': 15,
        }

    def getKeyDict(self, dict, val):
        for key, value in dict.items():
             if val == value:
                 return key

        print('[getKeyDict] Key does not exist: ', val)
        return None


    def discoverPossiblePaths(self, src_switch, dst_switch):
        # GET /wm/routing/paths/<src-dpid>/<dst-dpid>/<num-paths>/json
        # Get an ordered list of paths from the shortest to the longest path
        print('[discoverPossiblePaths]')

        response = requests.post('{host}/wm/routing/paths/max-fast-paths/json'.format(
            host=CONTROLLER_HOST,
            src=src_switch,
            dst=dst_switch
        ),
        data={ 'max_fast_paths': '10' }) # pois o default é 3
        response_data = response.json()
        print('Resposta setando max paths ', response_data)

        print('SRC = ', src_switch)
        print('DST = ', dst_switch)

        response = requests.get('{host}/wm/routing/paths/{src}/{dst}/10/json'.format(
            host=CONTROLLER_HOST,
            src=src_switch,
            dst=dst_switch
        ))
        response_data = response.json()
        paths = []

        # Paths tem o formato: [
        #     [{'switch_id': 'port' }, {'switch_id': 'port' }]
        # ]
        for item in response_data['results']:
            path = []
            for hop in item['path']:
                switch_id = hop['dpid']
                port = hop['port']
                path.append({ switch_id: port })
            paths.append(path)

        self.possible_paths = paths

        # print('Caminhos possiveis')
        # paths_with_links = []
        # for path in paths:
        #     links = []
        #     for hop in path:
        #         link = self.getKeyDict(self.links_map, hop)
        #         links.append(link)
        #     paths_with_links.append(links)
        #
        # print('Caminhos com formato de links: ', paths_with_links)


    def reset(self):
        numpy.zeros(NUM_PORTS)

    def getState(self):
        response = requests.get('{host}/wm/statistics/bandwidth/all/all/json'.format(host=CONTROLLER_HOST))
        response_data = response.json()

        state = []

        for item in response_data:
            switch_dpid = item['dpid']
            # item é um objeto com o formato:
            #    {
            #       "bits-per-second-rx" : "0",
            #       "dpid" : "00:00:00:00:00:00:00:02",
            #       "updated" : "Mon Sep 02 15:54:17 EDT 2019",
            #       "link-speed-bits-per-second" : "10000000",
            #       "port" : "1",
            #       "bits-per-second-tx" : "6059"
            #    }
            # print('Usage data - item: ', item)

            if item['dpid'] == self.switch_ids['S1'] and item['port'] == '1':
                #S1.1
                state[0] = float(item['bits-per-second-rx'])
            elif item['dpid'] == self.switch_ids['S1'] and item['port'] == '2':
                #S1.2
                state[1] = float(item['bits-per-second-rx'])
            elif item['dpid'] == self.switch_ids['S1'] and item['port'] == '3':
                #S1.3
                state[2] = float(item['bits-per-second-rx'])
            elif item['dpid'] == self.switch_ids['S2'] and item['port'] == '1':
                #S2.1
                state[3] = float(item['bits-per-second-rx'])
            elif item['dpid'] == self.switch_ids['S2'] and item['port'] == '2':
                #S2.2
                state[4] = float(item['bits-per-second-rx'])
            elif item['dpid'] == self.switch_ids['S2'] and item['port'] == '3':
                #S2.3
                state[5] = float(item['bits-per-second-rx'])
            elif item['dpid'] == self.switch_ids['S2'] and item['port'] == '4':
                #S2.4
                state[6] = float(item['bits-per-second-rx'])
            elif item['dpid'] == self.switch_ids['S3'] and item['port'] == '1':
                #S3.1
                state[7] = float(item['bits-per-second-rx'])
            elif item['dpid'] == self.switch_ids['S3'] and item['port'] == '2':
                #S3.2
                state[8] = float(item['bits-per-second-rx'])
            elif item['dpid'] == self.switch_ids['S3'] and item['port'] == '3':
                #S3.3
                state[9] = float(item['bits-per-second-rx'])
            elif item['dpid'] == self.switch_ids['S3'] and item['port'] == '4':
                #S3.4
                state[10] = float(item['bits-per-second-rx'])
            elif item['dpid'] == self.switch_ids['S4'] and item['port'] == '1':
                #S4.1
                state[11] = float(item['bits-per-second-rx'])
            elif item['dpid'] == self.switch_ids['S4'] and item['port'] == '2':
                #S4.2
                state[12] = float(item['bits-per-second-rx'])
            elif item['dpid'] == self.switch_ids['S4'] and item['port'] == '3':
                #S4.3
                state[13] = float(item['bits-per-second-rx'])
            elif item['dpid'] == self.switch_ids['S5'] and item['port'] == '1':
                #S5.1
                state[14] = float(item['bits-per-second-rx'])
            elif item['dpid'] == self.switch_ids['S5'] and item['port'] == '2':
                #S5.2
                state[15] = float(item['bits-per-second-rx'])

        return state

    def installRule(self, rule):
        urlPath = '{host}/wm/staticentrypusher/json'.format(host=CONTROLLER_HOST)
        headers = {
            'Content-type': 'application/json',
            'Accept': 'application/json',
        }

        return requests.post(urlPath, data=rule, headers=headers)
        # return self.flow_pusher.set(rule)

    def step(self, action):
        # Preciso conectar com o floodlight, instalar o caminho e analisar de novo
        done = False # Aprendizado continuado

        # action = [flow, path]
        flow_index = action[0]
        path_index = action[1]

        # flow_mbps = self.flows_mbps[flow_index]]
        # path = self.possible_paths[path_index]

        # # TODO:  como saber o id dos fluxos?

        rules = self.pathToRules(flow_index, path_index)
        for rule in rules:
            self.installRule(rule)

        slep(2) # aguarda regras refletirem e pacotes serem enviados novamente

        next_state = self.getState()
        reward = self.calculateReward(next_state)

        return next_state, reward, done


    def calculateReward(self, state):
        harmonic_mean = float(len(state) / numpy.sum(1.0/state))

        return harmonic_mean
