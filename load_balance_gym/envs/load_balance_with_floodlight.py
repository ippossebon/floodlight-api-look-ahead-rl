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

CONTROLLER_IP = 'http://localhost'
CONTROLLER_HOST = '{host}:8080'.format(host=CONTROLLER_IP)
LLDP_PACKAGE_SIZE = 60

NUM_PORTS = 16
MAX_PORTS_SWITCH = 4 # numero maximo de portas de um swithc

class LoadBalanceEnv(gym.Env):
    metadata = {'render.modes': ['human']}

    def __init__(self, num_flows, source_port, source_switch, target_port, target_switch):
        # Quero acomodar N fluxos na rede. Como?
        super(LoadBalanceEnv, self).__init__()

        self.num_flows = num_flows
        self.src_port = source_port
        self.dst_port = target_port

        self.flows_ids = self.getFlows()

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
        self.switch_links = {}
        self.switch_ports = {}
        self.num_links = 0

        self.discoverTopology()
        self.discoverPossiblePaths(src_switch=self.switch_ids[source_switch], dst_switch=self.switch_ids[target_switch])

        # State = Links usage as [link_A_usage, link_B_usage, link_C_usage, link_D_usage, ..., link_I_usage]
        self.observation_space = spaces.Box(
            low=0,
            high=LINK_CAPACITY,
            shape=(1, self.num_ports), # array com o RX de cada porta
            dtype=numpy.float16
        )

        # Ação = (flow_id, switch_id, in_port, out_port)
        # Ação = (flow_index, switch_index, in_port, out_port)
        max_flow_index = self.num_flows-1
        max_path_index = len(self.possible_paths)-1
        max_switch_index = len(self.switch_ids)-1
        max_port_index = MAX_PORTS_SWITCH - 1
        self.action_space = spaces.Box(
            low=numpy.array([0, 0, 0, 0]), # primeiro indica o valor mais baixo para o fluxo. segundo = valor mais baixo para caminho
            high=numpy.array([max_flow_index, max_switch_index, max_port_index, max_port_index]), # primeiro: maior indice do fluxo, maior indice do caminho
            dtype=numpy.int16
        )

        self.reward_range = (0, 1)

    def saveItemLinks(self, item):
        """
        Gera um dicionário no formato:
        self.switch_links = {
            '00:00:01': [{
                in_port: 1,
                out_port: 2,
                dst_switch: '00:00:002'
            },
            {
                in_port: 1,
                out_port: 3,
                dst_switch: '00:00:003'
            }]
        ...
        }
        """
        switch_id = item['src-switch']

        # Adiciona no mapeamento de links na direção 1
        if switch_id not in self.switch_links.keys():
            self.switch_links[switch_id] = []
        else:
            link = {
                'in_port': item['src-port'],
                'out_port': item['dst-port'],
                'dst_switch': item['dst-switch']
            }
            self.switch_links[switch_id].append(link)
            self.num_links += 1

        switch_id = item['dst-switch']
        # Adiciona no mapeamento de links na direção 2
        if switch_id not in self.switch_links.keys():
            self.switch_links[switch_id] = []
        else:
            link = {
                'in_port': item['dst-port'],
                'out_port': item['src-port'],
                'dst_switch': item['src-switch']
            }
            self.switch_links[switch_id].append(link)
            self.num_links += 1


    def saveItemSwitchIds(self, item):
        # Guarda IDs de switches
        if item['src-switch'] not in self.switch_ids:
            self.switch_ids.append(item['src-switch'])
        if item['dst-switch'] not in self.switch_ids:
            self.switch_ids.append(item['dst-switch'])


    def discoverTopology(self):
        response = requests.get('{host}/wm/topology/links/json'.format(
            host=CONTROLLER_HOST
        ))
        response_data = response.json()

        # Guarda mapeamento de switches e portas
        for item in response_data:
            self.saveItemLinks(item)
            self.saveItemSwitchIds(item)

        self.switch_ids = sorted(self.switch_ids)
        # print('-> [discoverTopology] Switch IDs: ', self.switch_ids)

        print('-> [discoverTopology] Switch Links: ', self.switch_links)

        print('-> [discoverTopology] Numero de portas: ', self.num_links + 2) # + 2 dos switches conectados aos hosts

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

        response = requests.post('{host}/wm/routing/paths/max-fast-paths/json'.format(
            host=CONTROLLER_HOST,
            src=src_switch,
            dst=dst_switch
        ),
        data={ 'max_fast_paths': '9' }) # pois o default é 3
        response_data = response.json()
        print('Resposta setando max paths ', response_data)

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

    def getFlows(self):
        response = requests.get('{host}/wm/staticentrypusher/list/all/json'.format(host=CONTROLLER_HOST))
        response_data = response.json()

        flows_ids = []
        for switch_id in response_data:
            for flow_obj in response_data[switch_id]:
                flow_obj_keys = flow_obj.keys()
                for flow_id in flow_obj_keys:
                    if flow_id not in flows_ids:
                        flows_ids.append(flow_id)

        print('-> [getFlows] Fluxos na rede: ', sorted(flows_ids))
        return sorted(flows_ids)


    def getState(self):
        response = requests.post('{host}/wm/statistics/config/enable/json'.format(host=CONTROLLER_HOST), data={})
        response_data = response.json()

        response = requests.get('{host}/wm/statistics/bandwidth/all/all/json'.format(host=CONTROLLER_HOST))
        response_data = response.json()

        state = numpy.zeros(self.num_ports)

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

            if item['dpid'] == self.switch_ids[0] and item['port'] == '1':
                #S1.1
                state[0] = float(item['bits-per-second-rx'])
            elif item['dpid'] == self.switch_ids[0] and item['port'] == '2':
                #S1.2
                state[1] = float(item['bits-per-second-rx'])
            elif item['dpid'] == self.switch_ids[0] and item['port'] == '3':
                #S1.3
                state[2] = float(item['bits-per-second-rx'])
            elif item['dpid'] == self.switch_ids[1] and item['port'] == '1':
                #S2.1
                state[3] = float(item['bits-per-second-rx'])
            elif item['dpid'] == self.switch_ids[1] and item['port'] == '2':
                #S2.2
                state[4] = float(item['bits-per-second-rx'])
            elif item['dpid'] == self.switch_ids[1] and item['port'] == '3':
                #S2.3
                state[5] = float(item['bits-per-second-rx'])
            elif item['dpid'] == self.switch_ids[1] and item['port'] == '4':
                #S2.4
                state[6] = float(item['bits-per-second-rx'])
            elif item['dpid'] == self.switch_ids[2] and item['port'] == '1':
                #S3.1
                state[7] = float(item['bits-per-second-rx'])
            elif item['dpid'] == self.switch_ids[2] and item['port'] == '2':
                #S3.2
                state[8] = float(item['bits-per-second-rx'])
            elif item['dpid'] == self.switch_ids[2] and item['port'] == '3':
                #S3.3
                state[9] = float(item['bits-per-second-rx'])
            elif item['dpid'] == self.switch_ids[2] and item['port'] == '4':
                #S3.4
                state[10] = float(item['bits-per-second-rx'])
            elif item['dpid'] == self.switch_ids[3] and item['port'] == '1':
                #S4.1
                state[11] = float(item['bits-per-second-rx'])
            elif item['dpid'] == self.switch_ids[3] and item['port'] == '2':
                #S4.2
                state[12] = float(item['bits-per-second-rx'])
            elif item['dpid'] == self.switch_ids[3] and item['port'] == '3':
                #S4.3
                state[13] = float(item['bits-per-second-rx'])
            elif item['dpid'] == self.switch_ids[4] and item['port'] == '1':
                #S5.1
                state[14] = float(item['bits-per-second-rx'])
            elif item['dpid'] == self.switch_ids[4] and item['port'] == '2':
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

    def actionToRule(self, action):
        # Ação = (flow_index, switch_index, in_port, out_port)
        flow_index = action[0]
        switch_index = action[1]
        in_port = action[2]
        out_port = action[3]

        pass

    def isValidAction(self, action):
        flow_index = action[0]
        switch_index = action[1]
        in_port = action[2]
        out_port = action[3]

        # Deve existir um fluxo com esse indice na lista
        contains_flow_index = True if flow_index <= len(self.flows_ids) else False

        # Deve existir um switch com o indice
        contains_switch_index = True if switch_index <= len(self.switch_ids) else False

        # Deve existir in e out port no switch
        switch_contains_in_port
        switch_contains_out_port

        # Não vou checar se pertence a um caminho possível.

        is_valid = contains_flow_index and contains_switch_index and switch_contains_in_port and switch_contains_out_port

        return is_valid

    def step(self, action):
        # Preciso conectar com o floodlight, instalar o caminho e analisar de novo
        done = False # Aprendizado continuado
        next_state = []
        reward = 0

        if self.isValidAction(action):
            rule = self.actionToRule(flow_index, path_index)
            self.installRule(rule)

            slep(2) # aguarda regras refletirem e pacotes serem enviados novamente

            next_state = self.getState()
            reward = self.calculateReward(next_state)
        else:
            next_state = self.getState()
            reward = 0

        return next_state, reward, done


    def calculateReward(self, state):
        harmonic_mean = float(len(state) / numpy.sum(1.0/state))

        return harmonic_mean
