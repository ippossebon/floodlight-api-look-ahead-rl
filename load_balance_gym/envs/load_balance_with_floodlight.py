import gym
from gym import error, spaces, utils
from gym.utils import seeding

import json
import numpy
import pandas
import requests
import time

# Based on the folllwing tutorials:
# https://towardsdatascience.com/creating-a-custom-openai-gym-environment-for-stock-trading-be532be3910e
# https://machinelearningmastery.com/tutorial-first-neural-network-python-keras/

MAX_BITS_CAPACITY = 10000000000 # TODO: update links capacity when generating network on mininet

CONTROLLER_IP = 'http://localhost'
CONTROLLER_HOST = '{host}:8080'.format(host=CONTROLLER_IP)
LLDP_PACKAGE_SIZE = 60

MAX_PRIORITY = "32768"

EPSILON = 0.001

NUM_PORTS = 16
MAX_PORTS_SWITCH = 4 # numero maximo de portas de um swithc
MULT_VALUE = 10000000

MEGABITS_CONVERSION = 1048576

class LoadBalanceEnv(gym.Env):
    metadata = {'render.modes': ['human']}

    def __init__(self, source_port_index, source_switch_index, target_port_index, target_switch_index):
        # Quero acomodar N fluxos na rede. Como?
        super(LoadBalanceEnv, self).__init__()

        self.src_switch_index = source_switch_index
        self.src_port_index = source_port_index
        self.dst_switch_index = target_switch_index
        self.dst_port_index = target_port_index

        self.flows_ids, self.flows_cookies = self.getFlows()

        # TODO: será que o if de fluxos vai ficar aqui dentro?


        self.switch_ids = []
        self.switch_links = {}
        self.switch_possible_ports = {}
        self.num_links = 0

        self.num_ports = NUM_PORTS # fixo neste primeiro momento
        self.discoverTopology()
        self.possible_paths = self.discoverPossiblePaths(src_switch=self.switch_ids[source_switch_index], dst_switch=self.switch_ids[target_switch_index])
        self.enableSwitchStatisticsEndpoit()

        # Ao descobrir a topologia, só são adicionadas as portas que conectam switches
        self.switch_possible_ports[self.switch_ids[source_switch_index]].append(str(source_port_index + 1))
        self.switch_possible_ports[self.switch_ids[target_switch_index]].append(str(target_port_index + 1))

        self.observation_space = spaces.Box(
            low=0,
            high=MAX_BITS_CAPACITY,
            shape=(self.num_ports,), # array com o RX de cada porta
            dtype=numpy.float16
        )

        # Ação = (switch_id, in_port, out_port)
        # Ação = (switch_index, in_port_index, out_port_index)
        max_path_index = len(self.possible_paths)-1
        max_switch_index = len(self.switch_ids)-1
        max_port_index = MAX_PORTS_SWITCH - 1
        self.action_space = spaces.Box(
            low=numpy.array([0, 0, 0]), # primeiro indica o valor mais baixo para o fluxo. segundo = valor mais baixo para caminho
            high=numpy.array([max_switch_index, max_port_index, max_port_index]), # primeiro: maior indice do fluxo, maior indice do caminho
            dtype=numpy.int8
        )

        self.state = numpy.zeros(shape=self.observation_space.shape)
        self.reward_range = (0, MULT_VALUE)


    def enableSwitchStatisticsEndpoit(self):
        # Enable statistics collection
        response = requests.post('{host}/wm/statistics/config/enable/json'.format(host=CONTROLLER_HOST), data={})
        response_data = response.json()


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


    def discoverPossiblePaths(self, src_switch, dst_switch):
        # GET /wm/routing/paths/<src-dpid>/<dst-dpid>/<num-paths>/json
        # Get an ordered list of paths from the shortest to the longest path

        # response = requests.post('{host}/wm/routing/paths/max-fast-paths/json'.format(
        #     host=CONTROLLER_HOST,
        #     src=src_switch,
        #     dst=dst_switch
        # ),
        # data={ 'max_fast_paths': '9' }) # pois o default é 3
        # response_data = response.json()
        # print('Resposta setando max paths ', response_data)

        response = requests.get('{host}/wm/routing/paths/{src}/{dst}/10/json'.format(
            host=CONTROLLER_HOST,
            src=src_switch,
            dst=dst_switch
        ))
        response_data = response.json()
        paths = []

        # Paths tem o formato: [
        #    [switch_index, in_port_index, out_port_index]
        # ]

        # "results":[
        #     {
        #         "src_dpid":"00:00:00:00:00:00:00:01",
        #         "dst_dpid":"00:00:00:00:00:00:00:03",
        #         "hop_count":"2",
        #         "latency":"9",
        #         "path_index":"0",
        #         "path":[
        #         {
        #             "dpid":"00:00:00:00:00:00:00:01",
        #             "port":"3"
        #         },
        #         {
        #             "dpid":"00:00:00:00:00:00:00:04",
        #             "port":"1"
        #         },
        #         {
        #             "dpid":"00:00:00:00:00:00:00:04",
        #             "port":"3"
        #         },
        #         {
        #             "dpid":"00:00:00:00:00:00:00:03",
        #             "port":"3"
        #         }]
        #     },

        # saida esperada: [
        #      [0, 0, 2]      ==       [00:00:00:00:00:00:00:01, 1, 3],  -- [self.src_switch, self.src_port_index, item[port]-1]
        #     [3, 0, 2],      ==       [00:00:00:00:00:00:00:04, 1, 3],
        #     [2, 2, 0]       ==       [00:00:00:00:00:00:00:03, 3, 1]   -- [item[dpid], item[port], self.dst_port_index]
        # ]

        paths_with_ids = []
        for item in response_data['results']:
            # path = {
            #  '00:00:01':  [1, 4],
            #  '00:00:02': [3, 2]
            # }
            path = {}

            for hop in item['path']:
                switch_id = hop['dpid']
                port_id = hop['port']
                if switch_id not in path.keys():
                    path[switch_id] = []
                path[switch_id].append(port_id)

            paths_with_ids.append(path)

        # paths_with_ids =  [
        #     {'00:00:00:00:00:00:00:01': ['3'], '00:00:00:00:00:00:00:04': ['1', '3'], '00:00:00:00:00:00:00:03': ['3']},
        #     {'00:00:00:00:00:00:00:01': ['2'], '00:00:00:00:00:00:00:02': ['1', '4'], '00:00:00:00:00:00:00:03': ['2']},
        #     {'00:00:00:00:00:00:00:01': ['3'], '00:00:00:00:00:00:00:04': ['1', '2'], '00:00:00:00:00:00:00:02': ['2', '4'], '00:00:00:00:00:00:00:03': ['2']}
        # ]

        for path_str in paths_with_ids:
            path = []
            num_hop = 0
            last_hop_index = len(path_str.keys()) -1

            for switch_id in path_str.keys():
                if num_hop == 0:
                    # É o primeiro hop, então precisa considerar infos da env
                    switch_index = self.src_switch_index
                    in_port_index = self.src_port_index
                    out_port_index = int(path_str[switch_id][0]) - 1

                    path.append(numpy.array([switch_index, in_port_index, out_port_index]))
                    num_hop += 1

                elif num_hop == last_hop_index:
                    # ultimo hop
                    switch_index = self.dst_switch_index
                    in_port_index = int(path_str[switch_id][0]) - 1
                    out_port_index = self.dst_port_index

                    path.append(numpy.array([switch_index, in_port_index, out_port_index]))
                    num_hop += 1

                else:
                    switch_index = self.switch_ids.index(switch_id)
                    in_port_index = int(path_str[switch_id][0]) - 1
                    out_port_index = int(path_str[switch_id][1]) - 1

                    path.append(numpy.array([switch_index, in_port_index, out_port_index]))
                    num_hop += 1

            paths.append(path)

        # print('Caminhos possiveis: ', paths)
        return paths


    def reset(self):
        self.state = numpy.zeros(shape=self.observation_space.shape)

        return self.state


    def getFlows(self):
        response = requests.get('{host}/wm/core/switch/all/flow/json'.format(host=CONTROLLER_HOST))
        response_data = response.json()

        flows_ids = []
        flows_cookies = {}
        for switch_address in response_data:
            for flow in response_data[switch_address]['flows']:
                contains_match = len(flow['match'].keys()) > 1

                if contains_match:
                    is_tcp_flow = False
                    tcp_src_port = None
                    try:
                        tcp_src_port = flow['match']['tcp_src']
                        tcp_dst_port = flow['match']['tcp_dst']

                        is_tcp_flow = tcp_src_port or 0
                        is_h1_to_h2_flow = tcp_dst_port == '5001'
                    except:
                        is_tcp_flow = False

                    if is_tcp_flow and is_h1_to_h2_flow:
                        flow_id = 'flow-{tcp_src_port}'.format(tcp_src_port=tcp_src_port)

                        # Se não existir na lista de fluxos ativos, adiciona
                        if flow_id not in flows_ids:
                            flow_cookie = flow['cookie']
                            flows_ids.append(flow_id)
                            flows_cookies[flow_id] = flow_cookie


        # print('-> [getFlows] Fluxos na rede: ', sorted(flows_ids))
        # print('-> [getFlows] Cookies dos fluxos na rede: ', flows_cookies)

        return sorted(flows_ids), flows_cookies


    def getState(self):
        # IMPORTANTE: o estado não pode ser guardado em bits. Será guardado em Mbits
        response = requests.post('{host}/wm/statistics/config/enable/json'.format(host=CONTROLLER_HOST), data={})
        response_data = response.json()

        response = requests.get('{host}/wm/statistics/bandwidth/all/all/json'.format(host=CONTROLLER_HOST))
        response_data = response.json()

        state = numpy.zeros(shape=self.observation_space.shape)

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

            if item['dpid'] == self.switch_ids[0] and item['port'] == '1':
                #S1.1
                state[0] = float(item['bits-per-second-rx']) / MEGABITS_CONVERSION
            elif item['dpid'] == self.switch_ids[0] and item['port'] == '2':
                #S1.2
                state[1] = float(item['bits-per-second-rx']) / MEGABITS_CONVERSION
            elif item['dpid'] == self.switch_ids[0] and item['port'] == '3':
                #S1.3
                state[2] = float(item['bits-per-second-rx']) / MEGABITS_CONVERSION
            elif item['dpid'] == self.switch_ids[1] and item['port'] == '1':
                #S2.1
                state[3] = float(item['bits-per-second-rx']) / MEGABITS_CONVERSION
            elif item['dpid'] == self.switch_ids[1] and item['port'] == '2':
                #S2.2
                state[4] = float(item['bits-per-second-rx']) / MEGABITS_CONVERSION
            elif item['dpid'] == self.switch_ids[1] and item['port'] == '3':
                #S2.3
                state[5] = float(item['bits-per-second-rx']) / MEGABITS_CONVERSION
            elif item['dpid'] == self.switch_ids[1] and item['port'] == '4':
                #S2.4
                state[6] = float(item['bits-per-second-rx']) / MEGABITS_CONVERSION
            elif item['dpid'] == self.switch_ids[2] and item['port'] == '1':
                #S3.1
                state[7] = float(item['bits-per-second-rx']) / MEGABITS_CONVERSION
            elif item['dpid'] == self.switch_ids[2] and item['port'] == '2':
                #S3.2
                state[8] = float(item['bits-per-second-rx']) / MEGABITS_CONVERSION
            elif item['dpid'] == self.switch_ids[2] and item['port'] == '3':
                #S3.3
                state[9] = float(item['bits-per-second-rx']) / MEGABITS_CONVERSION
            elif item['dpid'] == self.switch_ids[2] and item['port'] == '4':
                #S3.4
                state[10] = float(item['bits-per-second-rx']) / MEGABITS_CONVERSION
            elif item['dpid'] == self.switch_ids[3] and item['port'] == '1':
                #S4.1
                state[11] = float(item['bits-per-second-rx']) / MEGABITS_CONVERSION
            elif item['dpid'] == self.switch_ids[3] and item['port'] == '2':
                #S4.2
                state[12] = float(item['bits-per-second-rx']) / MEGABITS_CONVERSION
            elif item['dpid'] == self.switch_ids[3] and item['port'] == '3':
                #S4.3
                state[13] = float(item['bits-per-second-rx']) / MEGABITS_CONVERSION
            elif item['dpid'] == self.switch_ids[4] and item['port'] == '1':
                #S5.1
                state[14] = float(item['bits-per-second-rx']) / MEGABITS_CONVERSION
            elif item['dpid'] == self.switch_ids[4] and item['port'] == '2':
                #S5.2
                state[15] = float(item['bits-per-second-rx']) / MEGABITS_CONVERSION

        return state.flatten()

    def installRule(self, rule):
        urlPath = '{host}/wm/staticentrypusher/json'.format(host=CONTROLLER_HOST)
        headers = {
            'Content-type': 'application/json',
            'Accept': 'application/json',
        }

        return requests.post(urlPath, data=rule, headers=headers)

    def getFlowIdByCookie(self, cookie):
        flows_ids, flows_cookies = self.getFlows()

        for flow_id, flow_cookie in self.flows_cookies.items():
            if flow_cookie == cookie:
                return flow_id

        return None

    def getPossibleCookies(self):
        cookies = []
        for flow_id, flow_cookie in self.flows_cookies.items():
            cookies.append(flow_cookie)

        return cookies

    def getMostCostlyFlow(self, switch_id):
        # Retorna o fluxo que exige mais do switch, pra que esse tenha suas
        # rotas recalculadas
        # response = requests.get('{host}/wm/statistics/bandwidth/{switch_id}/all/json'.format(host=CONTROLLER_HOST, switch_id=switch_id))
        response = requests.get('{host}/wm/core/switch/all/flow/json'.format(host=CONTROLLER_HOST))
        response_data = response.json()

        possible_cookies = self.getPossibleCookies()

        max_byte_count = -1
        max_usage_flow_id = None

        for flow_obj in response_data[switch_id]['flows']:
            flow_cookie = flow_obj['cookie']
            if flow_cookie != '0' and flow_cookie in possible_cookies:
                flow_obj_keys = flow_obj.keys()
                flow_id = self.getFlowIdByCookie(flow_cookie)
                flow_byte_count = int(flow_obj['byte_count'])

                if flow_byte_count > max_byte_count:
                    max_byte_count = flow_byte_count
                    max_usage_flow_id = flow_id

        # print('[getMostCostlyFlow] max_usage_flow_id: {0} - max_byte_count: {1}'.format(max_usage_flow_id, max_byte_count))

        return max_usage_flow_id

    def actionToRule(self, switch_id, in_port, out_port, flow_id, priority=MAX_PRIORITY):
        # Só recebe ações possíveis
        # Ação = (flow_index, switch_index, in_port, out_port)
        rule = {
            "switch": switch_id,
            "name": flow_id,
            "priority": priority,
            "ingress-port": str(numpy.int8(in_port)),
            "active": "true",
            "actions": "output={0}".format(numpy.int8(out_port))
        }

        return json.dumps(rule)

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
            if str(possible_port) == str(port):
                return True

        return False

    def actionBelongsToPath(self, action):
        # Deve checar se faz parte de um caminho possível
        # Possible paths lista as regras de cada switch.
        """
        Possible paths: [
            [[0, 0, 2], [3, 0, 2], [2, 2, 0]],
            [[0, 0, 1], [1, 0, 3], [2, 1, 0]],
            [[0, 0, 1], [1, 0, 2], [4, 0, 1], [2, 3, 0]]
        ]
        """

        for path in self.possible_paths:
            for rule in path:
                if (action==rule).all():
                    return True
        return False

    def isValidAction(self, action):
        try:
            switch_index = int(action[0])
            in_port_index = action[1]
            out_port_index = action[2]
        except:
            return False

        in_port = in_port_index + 1
        out_port = out_port_index + 1

        # Deve existir um switch com o indice
        contains_switch_index = True if switch_index <= len(self.switch_ids) else False

        # Deve existir in e out port no switch
        switch_id = self.switch_ids[switch_index]
        switch_contains_in_port = self.switchContainsPort(switch_id, in_port)
        switch_contains_out_port = self.switchContainsPort(switch_id, out_port)
        switch_contains_ports = switch_contains_in_port and switch_contains_out_port

        # Checa se pertence a algum caminho possível. Para evitar loops na rede.
        belongs_to_path = self.actionBelongsToPath(action) if switch_contains_ports else False

        is_valid = contains_switch_index and belongs_to_path

        ### TODO: Debugging
        # print('...')
        # print('--> isValidAction')
        # print('contains_switch_index = ', contains_switch_index)
        # print('switch_contains_in_port = ', switch_contains_in_port)
        # print('switch_contains_out_port = ', switch_contains_out_port)
        #
        # print('portas do switch = ', self.switch_possible_ports[switch_id])

        # print('switch_index = ', switch_index)
        # print('in_port = ', in_port)
        # print('out_port = ', out_port)
        # print('belongs_to_path = ', belongs_to_path)
        # print('is_valid = ', is_valid)
        # print('...')

        return is_valid

    def step(self, action):
        # Preciso conectar com o floodlight, instalar o caminho e analisar de novo
        done = False # Aprendizado continuado
        next_state = []
        reward = 0
        info = {}

        is_valid_action = self.isValidAction(action)

        flow_id = None
        switch_id = None

        if is_valid_action:
            switch_index = int(action[0])
            switch_id = self.switch_ids[switch_index]
            flow_id = self.getMostCostlyFlow(switch_id)

        if not (is_valid_action or flow_id):
            next_state = self.getState()
            return next_state, reward, done, info


        # # Garante que só vamos executar ações válidas.
        # while not (is_valid_action and flow_id):
        #     print('-> Agente escolheu acao invalida ou flow id nao existe')
        #     print('- action = ', action)
        #     print('- flow_id = ', flow_id)
        #
        #     # Se a ação for inválida, pedimos uma nova ação.
        #     action = self.action_space.sample() # TODO: rever!!!!
        #     is_valid_action = self.isValidAction(action)
        #     switch_index = int(action[0])
        #     switch_id = self.switch_ids[switch_index]
        #     flow_id = self.getMostCostlyFlow(switch_id) if is_valid_action else None


        # switch_index = int(action[0])
        # in_port_index = action[1]
        # out_port_index = action[2]
        #
        # switch_id = self.switch_ids[switch_index]
        # in_port = in_port_index + 1
        # out_port = out_port_index + 1

        in_port_index = action[1]
        out_port_index = action[2]

        in_port = in_port_index + 1
        out_port = out_port_index + 1

        rule = self.actionToRule(
            switch_id,
            in_port,
            out_port,
            flow_id
        )

        # print('Action aplicada = ', action)
        # print('Regra instalada = ', rule)
        self.installRule(rule)

        time.sleep(5) # aguarda regras refletirem e pacotes serem enviados novamente

        next_state = self.getState()
        reward = self.calculateReward(next_state)

        self.state = next_state

        ## TODo: muito errado!!! Esta entendendo que aquela action tem uma recompensa
        return next_state, reward, done, info


    def calculateReward(self, state):

        state_var = numpy.var(state) or EPSILON
        reward = (1/state_var) * MULT_VALUE

        return reward

    def render(self, render='console'):
        self.state = self.getState()
        print('State = ', self.state)

        self.flows_ids, self.flows_cookies = self.getFlows()
        print('Flow ids = ', self.flows_ids)
