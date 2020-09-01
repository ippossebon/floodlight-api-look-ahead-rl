import gym
from gym import error, spaces, utils
from gym.utils import seeding

import numpy
import pandas
import requests
import time

# Based on the folllwing tutorials:
# https://towardsdatascience.com/creating-a-custom-openai-gym-environment-for-stock-trading-be532be3910e
# https://machinelearningmastery.com/tutorial-first-neural-network-python-keras/

LINK_CAPACITY = 1000 # TODO: update links capacity when generating network on mininet

CONTROLLER_IP = 'http://localhost'
CONTROLLER_HOST = '{host}:8080'.format(host=CONTROLLER_IP)
LLDP_PACKAGE_SIZE = 60

MAX_PRIORITY = "32768"

EPSILON = 0.001

NUM_PORTS = 16
MAX_PORTS_SWITCH = 4 # numero maximo de portas de um swithc

class LoadBalanceEnv(gym.Env):
    metadata = {'render.modes': ['human']}

    def __init__(self, source_port, source_switch, target_port, target_switch):
        # Quero acomodar N fluxos na rede. Como?
        super(LoadBalanceEnv, self).__init__()

        self.src_port = source_port
        self.dst_port = target_port

        self.flows_ids, self.flows_cookies = self.getFlows()

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
        self.switch_possible_ports = {}
        self.num_links = 0

        self.discoverTopology()
        self.possible_paths = self.discoverPossiblePaths(src_switch=self.switch_ids[source_switch], dst_switch=self.switch_ids[target_switch])
        self.enableSwitchStatisticsEndpoit()


        # Ao descobrir a topologia, só são adicionadas as portas que conectam switches
        self.switch_possible_ports[self.switch_ids[source_switch]].append(str(source_port))
        self.switch_possible_ports[self.switch_ids[target_switch]].append(str(target_port))

        # State = Links usage as [link_A_usage, link_B_usage, link_C_usage, link_D_usage, ..., link_I_usage]
        self.observation_space = spaces.Box(
            low=0,
            high=LINK_CAPACITY,
            shape=(1, self.num_ports), # array com o RX de cada porta
            dtype=numpy.float16
        )

        # Ação = (flow_id, switch_id, in_port, out_port)
        # Ação = (flow_index, switch_index, in_port, out_port)
        max_path_index = len(self.possible_paths)-1
        max_switch_index = len(self.switch_ids)-1
        max_port_index = MAX_PORTS_SWITCH - 1
        self.action_space = spaces.Box(
            low=numpy.array([0, 0, 0]), # primeiro indica o valor mais baixo para o fluxo. segundo = valor mais baixo para caminho
            high=numpy.array([max_switch_index, max_port_index, max_port_index]), # primeiro: maior indice do fluxo, maior indice do caminho
            dtype=numpy.int16
        )

        self.reward_range = (0, 1)


    def enableSwitchStatisticsEndpoit(self):
        # Enable statistics collection
        response = requests.post('{host}/wm/statistics/config/enable/json'.format(host=CONTROLLER_HOST), data={})
        response_data = response.json()

        print('[enableSwitchStatisticsEndpoit] ', response_data)


    def saveItemLinks(self, item):
        """
        Gera um dicionário no formato:
        self.switch_links = {
            '00:00:01': [{
                src_port: 1,
                dst_port: 2,
                dst_switch: '00:00:002'
            },
            {
                src_port: 1,
                dst_port: 3,
                dst_switch: '00:00:003'
            }]
        ...
        }

        """

        # Adiciona no mapeamento de links na direção 1
        switch_src = item['src-switch']
        if switch_src not in self.switch_links.keys():
            self.switch_links[switch_src] = []

        link1 = {
            'src_port': item['src-port'],
            'dst_port': item['dst-port'],
            'dst_switch': item['dst-switch']
        }
        self.switch_links[switch_src].append(link1)
        self.num_links += 1

        # Adiciona porta possível
        if switch_src not in self.switch_possible_ports.keys():
            self.switch_possible_ports[switch_src] = []
        self.switch_possible_ports[switch_src].append(item['src-port'])

        # Adiciona no mapeamento de links na direção 2
        switch_dst = item['dst-switch']
        if switch_dst not in self.switch_links.keys():
            self.switch_links[switch_dst] = []

        link2 = {
            'src_port': item['dst-port'],
            'dst_port': item['src-port'],
            'dst_switch': item['src-switch']
        }
        self.switch_links[switch_dst].append(link2)
        self.num_links += 1

        # Adiciona porta possível
        if switch_dst not in self.switch_possible_ports.keys():
            self.switch_possible_ports[switch_dst] = []
        self.switch_possible_ports[switch_dst].append(item['dst-port'])


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

        # print('-> [discoverTopology] Switch Links: ', self.switch_links)
        # print('-> [discoverTopology] Numero de portas: ', self.num_links + 2) # + 2 dos switches conectados aos hosts

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

        return paths

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
        flow_cookies = {}
        for switch_id in response_data:
            for flow_obj in response_data[switch_id]:
                flow_obj_keys = flow_obj.keys()
                for flow_id in flow_obj_keys:
                    if flow_id not in flows_ids:
                        flows_ids.append(flow_id)
                        flow_cookies[flow_id] = flow_obj[flow_id]['cookie']

        print('-> [getFlows] Fluxos na rede: ', sorted(flows_ids))
        print('-> [getFlows] Cookies dos fluxos na rede: ', flow_cookies)

        return sorted(flows_ids), flow_cookies


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

    def getFlowIdByCookie(self, cookie):
        for flow_id, flow_cookie in self.flows_cookies.items():
            if flow_cookie == cookie:
                return flow_id
        return None

    def getMostCostlyFlow(self, switch_id):
        # retorna o fluxo que exige mais do switch, pra que esse tenha suas
        # rotas recalculadas
        # response = requests.get('{host}/wm/statistics/bandwidth/{switch_id}/all/json'.format(host=CONTROLLER_HOST, switch_id=switch_id))
        response = requests.get('{host}/wm/core/switch/all/flow/json'.format(host=CONTROLLER_HOST))
        response_data = response.json()

        max_byte_count = -1
        max_usage_flow_id = None # preciso de um fallback

        print('GET MOST COSTLY FLOW DO SWITCH ', switch_id)
        print('response: ', response)
        print('response_data', response_data)
        print('')

        """

        {'00:00:00:00:00:00:00:04': {'flows': [{'version': 'OF_13', 'cookie': '0', 'table_id': '0x0', 'packet_count': '290', 'byte_count': '21846', 'duration_sec': '1371', 'duration_nsec': '438000000', 'priority': '0', 'idle_timeout_s': '0', 'hard_timeout_s': '0', 'flags': [], 'match': {}, 'instructions': {'instruction_apply_actions': {'actions': 'output=controller'}}}]}, '00:00:00:00:00:00:00:05': {'flows': [{'version': 'OF_13', 'cookie': '0', 'table_id': '0x0', 'packet_count': '187', 'byte_count': '14041', 'duration_sec': '1371', 'duration_nsec': '435000000', 'priority': '0', 'idle_timeout_s': '0', 'hard_timeout_s': '0', 'flags': [], 'match': {}, 'instructions': {'instruction_apply_actions': {'actions': 'output=controller'}}}]}, '00:00:00:00:00:00:00:02': {'flows': [{'version': 'OF_13', 'cookie': '0', 'table_id': '0x0', 'packet_count': '377', 'byte_count': '28347', 'duration_sec': '1371', 'duration_nsec': '406000000', 'priority': '0', 'idle_timeout_s': '0', 'hard_timeout_s': '0', 'flags': [], 'match': {}, 'instructions': {'instruction_apply_actions': {'actions': 'output=controller'}}}]}, '00:00:00:00:00:00:00:03': {'flows': [{'version': 'OF_13', 'cookie': '0', 'table_id': '0x0', 'packet_count': '283', 'byte_count': '21281', 'duration_sec': '1371', 'duration_nsec': '304000000', 'priority': '0', 'idle_timeout_s': '0', 'hard_timeout_s': '0', 'flags': [], 'match': {}, 'instructions': {'instruction_apply_actions': {'actions': 'output=controller'}}}]}, '00:00:00:00:00:00:00:01': {'flows': [{'version': 'OF_13', 'cookie': '49539595572507916', 'table_id': '0x0', 'packet_count': '0', 'byte_count': '0', 'duration_sec': '1330', 'duration_nsec': '532000000', 'priority': '32768', 'idle_timeout_s': '0', 'hard_timeout_s': '0', 'flags': ['SEND_FLOW_REM'], 'match': {'in_port': '1'}, 'instructions': {'instruction_apply_actions': {'actions': 'output=2'}}}, {'version': 'OF_13', 'cookie': '0', 'table_id': '0x0', 'packet_count': '192', 'byte_count': '14448', 'duration_sec': '1371', 'duration_nsec': '415000000', 'priority': '0', 'idle_timeout_s': '0', 'hard_timeout_s': '0', 'flags': [], 'match': {}, 'instructions': {'instruction_apply_actions': {'actions': 'output=controller'}}}]}}

        """

        flows_ids = []
        for switch in response_data:
            if switch == switch_id:
                for flow_obj in response_data[switch_id]['flows']:

                    print('flow_obj = ', flow_obj)
                    print('max_byte_count = ', max_byte_count)

                    flow_cookie = flow_obj['cookie']
                    flow_obj_keys = flow_obj.keys()
                    flow_id = self.getFlowIdByCookie(flow_cookie) # TODO: como conseguir o ID? deveria olhar pro cookie?
                    flow_byte_count = int(flow_obj['byte_count'])

                    print('Byte count: ', flow_byte_count)
                    print('Flow ID: {0} - cookie: {1}'.format(flow_id, self.flows_cookies[flow_id]))

                    if flow_byte_count > max_byte_count:
                        max_usage_flow_id = flow_id

        return max_usage_flow_id

    def actionToRule(self, action, priority=MAX_PRIORITY):
        # Ação = (flow_index, switch_index, in_port, out_port)
        switch_index = action[0]
        in_port = str(action[1] + 1)
        out_port = str(action[2] + 1)

        switch_id = self.switch_ids[switch_index]

        flow_id = self.getMostCostlyFlow(switch_id)
        rule = {
            "switch": switch_id,
            "name": flow_id,
            "priority": priority,
            "ingress-port": in_port,
            "active": "true",
            "actions": "output={0}".format(out_port)
        }

        return rule

    def switchContainsPort(self, switch_id, port):
        """
        Considera o dicionário:
        self.switch_possible_ports = {
            '00:00:01': ['1', '2', '3],
            '00:00:02': ['1', '2', '3', '4']
        ...
        }

        """
        for possible_port in self.switch_possible_ports[switch_id]:
            if str(possible_port) == port:
                return True

        return False

    def actionBelongsToPath(self, action):
        # Deve checar se faz parte de um caminho possível
        switch_index = action[0]
        out_port_index = action[2]

        switch_id = self.switch_ids[switch_index]
        out_port = str(out_port_index + 1)


        # Possible paths lista os links. Ex: saí de switch X na porta Y, cheguei em switch X na porta Z
        """
        Possible paths:  [
            [{'00:00:00:00:00:00:00:01': '3'}, {'00:00:00:00:00:00:00:04': '1'}, {'00:00:00:00:00:00:00:04': '3'}, {'00:00:00:00:00:00:00:03': '3'}],
            [{'00:00:00:00:00:00:00:01': '2'}, {'00:00:00:00:00:00:00:02': '1'}, {'00:00:00:00:00:00:00:02': '4'}, {'00:00:00:00:00:00:00:03': '2'}],
            [{'00:00:00:00:00:00:00:01': '3'}, {'00:00:00:00:00:00:00:04': '1'}, {'00:00:00:00:00:00:00:04': '2'}, {'00:00:00:00:00:00:00:02': '2'}, {'00:00:00:00:00:00:00:02': '4'}, {'00:00:00:00:00:00:00:03': '2'}]]
        """

        for path in self.possible_paths:
            for link in path:
                for link_switch_id in link.keys():
                    link_out_port = link[link_switch_id]
                    print('out_port = {0} - link_out_port = {1}'.format(out_port, link_out_port))

                    if link_switch_id == switch_id and out_port == link_out_port:
                        return True

        return False

    def isValidAction(self, action):
        switch_index = action[0]
        in_port_index = action[1]
        out_port_index = action[2]

        in_port = in_port_index + 1
        out_port = out_port_index + 1

        # Deve existir um fluxo com esse indice na lista
        # contains_flow_index = True if flow_index <= len(self.flows_ids) else False

        # Deve existir um switch com o indice
        contains_switch_index = True if switch_index <= len(self.switch_ids) else False

        # Deve existir in e out port no switch
        switch_id = self.switch_ids[switch_index]
        switch_contains_in_port = self.switchContainsPort(switch_id, str(in_port))
        switch_contains_out_port = self.switchContainsPort(switch_id, str(out_port))
        switch_contains_ports = switch_contains_in_port and switch_contains_out_port

        # Checa se pertence a algum caminho possível. Para evitar loops na rede.
        belongs_to_path = self.actionBelongsToPath(action) if switch_contains_ports else False

        is_valid = contains_switch_index and switch_contains_ports and belongs_to_path

        ### TODO: Debugging
        print('...')
        print('--> isValidAction')
        # print('contains_switch_index = ', contains_switch_index)
        # print('switch_contains_in_port = ', switch_contains_in_port)
        # print('switch_contains_out_port = ', switch_contains_out_port)
        #
        # print('portas do switch = ', self.switch_possible_ports[switch_id])

        print('switch_index = ', switch_index)
        print('switch_id = ', self.switch_ids[switch_index])
        print('in_port = ', in_port)
        print('out_port = ', out_port)
        print('belongs_to_path = ', belongs_to_path)
        print('is_valid = ', is_valid)
        print('...')

        return is_valid

    def step(self, action):
        # Preciso conectar com o floodlight, instalar o caminho e analisar de novo
        done = False # Aprendizado continuado
        next_state = []
        reward = 0

        if self.isValidAction(action):
            rule = self.actionToRule(action)
            print('Regra a ser instalada = ', rule)
            self.installRule(rule)

            time.sleep(2) # aguarda regras refletirem e pacotes serem enviados novamente

            next_state = self.getState()
            reward = self.calculateReward(next_state)
        else:
            # # TODO: pede outra ação!! Só devemos aplicar ações válidas
            next_state = self.getState()
            reward = 0

        return next_state, reward


    def calculateReward(self, state):
        state_values_sum = numpy.sum(1.0/state) or EPSILON
        harmonic_mean = float(len(state) / state_values_sum)

        return harmonic_mean
