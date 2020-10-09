import gym
from gym import spaces, utils
from gym.utils import seeding

from .action_rules_map import actionMap

import json
import numpy
import pandas
import requests
import time

MAX_BITS_CAPACITY = 10000000000 # TODO: update links capacity when generating network on mininet

CONTROLLER_IP = 'http://192.168.68.250'
CONTROLLER_HOST = '{host}:8080'.format(host=CONTROLLER_IP)

MAX_PRIORITY = "32768"

EPSILON = 0.001

class LoadBalanceEnvDiscAction(gym.Env):
    metadata = {'render.modes': ['human']}

    def __init__(self, source_port_index, source_switch_index, target_port_index, target_switch_index):
        super(LoadBalanceEnvDiscAction, self).__init__()

        self.src_switch_index = source_switch_index
        self.src_port_index = source_port_index
        self.dst_switch_index = target_switch_index
        self.dst_port_index = target_port_index

        self.switch_ids = []
        self.switch_links = {}
        self.switch_possible_ports = {}
        self.num_links = 0

        self.discoverTopology()

        # Ao descobrir a topologia, só são adicionadas as portas que conectam switches
        self.switch_possible_ports[self.switch_ids[source_switch_index]].append(str(source_port_index + 1))
        self.switch_possible_ports[self.switch_ids[target_switch_index]].append(str(target_port_index + 1))

        self.observation_space = spaces.Box(
            low=0,
            high=10485760, # maximo = 10Mbps = 10 * 1024 * 1024
            shape=(16,), # array com o RX de cada porta = 16 portas
            dtype=numpy.float16
        )

        self.action_space = spaces.Discrete(28)

        self.state = numpy.zeros(shape=self.observation_space.shape)
        self.prev_state = numpy.zeros(shape=self.observation_space.shape)
        self.reward_range = (0, 3200) # # TODO: rever

        self.previous_tx = numpy.zeros(shape=self.observation_space.shape)
        self.previous_timestamp = None
        self.initializeState()

    def initializeState(self):
        statistics_tx, timestamp = self.getStatisticsBandwidth()

        self.previous_tx = statistics_tx
        self.previous_timestamp = timestamp


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
        response = requests.get('{host}/wm/topology/links/json'.format(host=CONTROLLER_HOST))
        response_data = response.json()

        # Guarda mapeamento de switches e portas
        for item in response_data:
            self.saveItemLinks(item)
            self.saveItemSwitchIds(item)

        self.switch_ids = sorted(self.switch_ids)

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


    def reset(self):
        self.state = self.getState()

        return self.state


    def getStatisticsBandwidth(self):
        response = requests.get('{host}/wm/statistics/bandwidth/all/all/json'.format(host=CONTROLLER_HOST))
        response_data = response.json()

        timestamp = time.time() # seconds
        statistics_tx = numpy.zeros(shape=self.observation_space.shape)

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

            ### S1
            if item['dpid'] == "00:00:00:00:00:00:00:01" and item['port'] == '1':
                #S1.1
                statistics_tx[0] = float(item['bits-per-second-rx'])

            elif item['dpid'] == "00:00:00:00:00:00:00:01" and item['port'] == '2':
                #S1.2
                statistics_tx[1] = float(item['bits-per-second-rx'])

            elif item['dpid'] == "00:00:00:00:00:00:00:01" and item['port'] == '3':
                #S1.3
                statistics_tx[2] = float(item['bits-per-second-rx'])

            ### S2
            elif item['dpid'] == "00:00:00:00:00:00:00:02" and item['port'] == '1':
                #S2.1
                statistics_tx[3] = float(item['bits-per-second-rx'])

            elif item['dpid'] == "00:00:00:00:00:00:00:02" and item['port'] == '2':
                #S2.2
                statistics_tx[4] = float(item['bits-per-second-rx'])

            elif item['dpid'] == "00:00:00:00:00:00:00:02" and item['port'] == '3':
                #S2.3
                statistics_tx[5] = float(item['bits-per-second-rx'])
            elif item['dpid'] == "00:00:00:00:00:00:00:02" and item['port'] == '3':
                #S2.4
                statistics_tx[6] = float(item['bits-per-second-rx'])

            ### S3
            elif item['dpid'] == "00:00:00:00:00:00:00:03" and item['port'] == '1':
                #S3.1
                statistics_tx[7] = float(item['bits-per-second-rx'])

            elif item['dpid'] == "00:00:00:00:00:00:00:03" and item['port'] == '2':
                #S3.2
                statistics_tx[8] = float(item['bits-per-second-rx'])

            elif item['dpid'] == "00:00:00:00:00:00:00:03" and item['port'] == '3':
                #S3.3
                statistics_tx[9] = float(item['bits-per-second-rx'])
            elif item['dpid'] == "00:00:00:00:00:00:00:03" and item['port'] == '4':
                #S3.4
                statistics_tx[10] = float(item['bits-per-second-rx'])

            ### S4
            elif item['dpid'] == "00:00:00:00:00:00:00:04" and item['port'] == '1':
                #S4.1
                statistics_tx[11] = float(item['bits-per-second-rx'])

            elif item['dpid'] == "00:00:00:00:00:00:00:04" and item['port'] == '2':
                #S4.2
                statistics_tx[12] = float(item['bits-per-second-rx'])

            elif item['dpid'] == "00:00:00:00:00:00:00:04" and item['port'] == '3':
                #S4.3
                statistics_tx[13] = float(item['bits-per-second-rx'])

            ### S1
            elif item['dpid'] == "00:00:00:00:00:00:00:05" and item['port'] == '1':
                #S5.1
                statistics_tx[14] = float(item['bits-per-second-rx'])
            elif item['dpid'] == "00:00:00:00:00:00:00:05" and item['port'] == '2':
                #S5.2
                statistics_tx[15] = float(item['bits-per-second-rx'])


        statistics_tx.flatten()

        return statistics_tx, timestamp


    def getState(self):
        state = numpy.zeros(shape=self.observation_space.shape)

        statistics_tx, timestamp = self.getStatisticsBandwidth()


        for i in range(len(statistics_tx)):
            state[i] = statistics_tx[i]  / (1024 * 1024) # valor em Mbits

        # state = state.flatten()
        # self.prev_state = state

        return state

    def installRule(self, rule):
        urlPath = '{host}/wm/staticflowpusher/json'.format(host=CONTROLLER_HOST)
        headers = {
            'Content-type': 'application/json',
            'Accept': 'application/json',
        }
        data = json.dumps(rule)

        return requests.post(urlPath, data=data, headers=headers)

    def uninstallRule(self, rule_name):
        urlPath = '{host}/wm/staticflowpusher/json'.format(host=CONTROLLER_HOST)
        headers = {
            'Content-type': 'application/json',
            'Accept': 'application/json',
        }

        rule = json.dumps({ "name": rule_name })

        return requests.delete(urlPath, data=rule, headers=headers)

    def actionToRule(self, switch_id, in_port, out_port, flow_match, priority=MAX_PRIORITY):
        # Só recebe ações possíveis
        # Ação = (switch_index, in_port, out_port)
        tcp_src = flow_match['tcp_src']
        tcp_dst = flow_match['tcp_dst']
        ipv4_src = flow_match['ipv4_src']
        ipv4_dst = flow_match['ipv4_dst']

        rule_name = 'regra-{0}-in_{1}-out_{2}--{3}:{4}-to-{5}:{6}'.format(switch_id, in_port, out_port, ipv4_src, tcp_src, ipva4_dst, tcp_dst)
        rule = {
            "switch": switch_id,
            "name": rule_name,
            "priority": MAX_PRIORITY,
            "in_port": str(numpy.int8(in_port)),
            "active": "true",
            "eth_type": "0x0800",
            "ipv4_src": ipv4_src,
            "ipv4_dst": ipv4_dst,
            "ip_proto": "0x06",
            "actions": "output={0}".format(numpy.int8(out_port))
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

    def existsRuleWithAction(self, switch_id, in_port, out_port):
       response = requests.get('{host}/wm/staticflowpusher/list/{switch_id}/json'.format(host=CONTROLLER_HOST, switch_id=switch_id))
       response_data = response.json()

       for item in response_data[switch_id]:
           for rule_name, rule in item.items():
               try:
                   if rule['match']['in_port'] == str(in_port):
                       if str(out_port) in rule['instructions']['instruction_apply_actions']['actions']:
                           print('Regra ja existente para action {0}, in {1}, out {2}: {3}'.format(switch_id, in_port, out_port, rule_name))
                           return rule_name
               except:
                   continue

       return None

    def getMostCostlyFlow(self, switch_id):
        # Retorna o fluxo que exige mais do switch, pra que esse tenha suas
        # rotas recalculadas
        # response = requests.get('{host}/wm/statistics/bandwidth/{switch_id}/all/json'.format(host=CONTROLLER_HOST, switch_id=switch_id))
        response = requests.get('{host}/wm/core/switch/{switch_id}/flow/json'.format(host=CONTROLLER_HOST, switch_id=switch_id))
        response_data = response.json()

        max_byte_count = -1
        max_usage_flow_match = None
        flow_match = None

        for flow_obj in response_data['flows']:
            flow_cookie = flow_obj['cookie']
            try:
                flow_match = flow_obj['match']
            except:
                print('Fluxo sem match = ', flow_obj)

            if flow_match:
                flow_byte_count = int(flow_obj['byteCount'])
                if flow_byte_count > max_byte_count:
                    max_byte_count = flow_byte_count
                    max_usage_flow_match = flow_match

        print('[getMostCostlyFlow] max_usage_flow_match: {0} - max_byte_count: {1}'.format(max_usage_flow_match, max_byte_count))

        return flow_match

    def step(self, action):
        print('...........')
        done = False # Aprendizado continuado
        next_state = []
        reward = 0
        info = {}

        action_vec = actionMap(action)

        switch_index = action_vec[0]
        in_port_index = action_vec[1]
        out_port_index = action_vec[2]

        switch_id = self.switch_ids[switch_index]
        in_port = in_port_index + 1
        out_port = out_port_index + 1
        flow_match = self.getMostCostlyFlow(switch_id)

        if flow_match:
            rule = self.actionToRule(switch_id, in_port, out_port, flow_match)
            print('Regra a ser instalada: ', rule)
            response_install = self.installRule(rule)
            print('Resposta instalação: ', response_install.json())

            time.sleep(7) # aguarda regras refletirem e pacotes serem enviados novamente

            next_state = self.getState()
            reward = self.calculateReward(next_state)
            self.state = next_state

            print('State: {0} -- Reward = {1}'.format(self.state, reward))
            print('...........')
            print()

            return next_state, reward, done, info
        else:
            # Não ha fluxo onerando o switch escolhido
            # O estado não será alterado e a recompensa é zero
            print('Sem regra a ser instalada.')

            next_state = self.state
            reward = 0

            print('State: {0} -- Reward = {1}'.format(self.state, reward))
            print('...........')
            print()

            return next_state, reward, done, info


    def calculateReward(self, state):
        # Pega métricas de performance do controlador
        # response = requests.get('{host}/wm/performance/data/json'.format(host=CONTROLLER_HOST))
        # response_data = response.json()
        #
        # for item in response_data['modules']:
        #     if item['module-name'] == "net.floodlightcontroller.forwarding.Forwarding":
        #         forwarding_avg_time = item['average']
        #         break


        total_usage_links = 0
        for i in range(len(state)):
            if state[i] > 1:
                total_usage_links += state[i] * 2
            else:
                # link não está sendo usado
                total_usage_links += 1

        # Desconta o tempo de processamento para nao privilegiar caminhos enormes que podem atrasar o fluxo
        reward = total_usage_links

        return reward


    def render(self, render='console'):
        self.state = self.getState()
        print('State = ', self.state)
