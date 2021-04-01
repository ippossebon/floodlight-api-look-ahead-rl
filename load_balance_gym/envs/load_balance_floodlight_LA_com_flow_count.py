import gym
from gym import spaces, utils
from gym.utils import seeding

from .action_with_flow_rules_map import actionWithFlowMap
from .flow_match_map import flowMap


import json
import numpy
import pandas
import requests
import time

MAX_BITS_CAPACITY = 10000000000 # TODO: update links capacity when generating network on mininet

CONTROLLER_IP = 'http://192.168.68.250'
CONTROLLER_HOST = '{host}:8080'.format(host=CONTROLLER_IP)

MAX_PRIORITY = 32760

EPSILON = 0.001

MEGA_BYTE_COUNT = 1 * 1024 * 1024
GIGA_BYTE_COUNT = MEGA_BYTE_COUNT * 1024

ELEPHANT_FLOW_THRESHOLD = 100 * 1024 * 1024 # 5MBytes
ELEPHANT_FLOW_REWARD_FACTOR = 100

MAX_HMEAN_REWARD = 5.29
MIN_HMEAN_REWARD = EPSILON

MAX_LA_REWARD = ELEPHANT_FLOW_REWARD_FACTOR + MAX_HMEAN_REWARD
MIN_LA_REWARD = -1 * MAX_LA_REWARD

# 213574015

class LoadBalanceEnvLA(gym.Env):
    metadata = {'render.modes': ['human']}

    def __init__(self, source_port_index, source_switch_index, target_port_index, target_switch_index):
        super(LoadBalanceEnvLA, self).__init__()

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
            high=(50*MEGA_BYTE_COUNT),
            shape=(16,), # array com o RX de cada porta = 16 portas
            dtype=numpy.uint32
        )

        self.action_space = spaces.Discrete(529)

        self.state = numpy.zeros(shape=self.observation_space.shape)
        self.prev_state = numpy.zeros(shape=self.observation_space.shape)
        self.reward_range = (0, MAX_HMEAN_REWARD) # max = 3200 * (50 + 50) (50 é capacidade do link S3.1)

        self.state = numpy.zeros(shape=self.observation_space.shape)


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

    def getActiveFlows(self):
        # response = requests.get('{host}/wm/core/switch/all/flow/json'.format(host=CONTROLLER_HOST))
        response = requests.get('{host}/wm/core/switch/00:00:00:00:00:00:00:01/flow/json'.format(host=CONTROLLER_HOST))
        response_data = response.json()

        active_flows = []

        try:
            for flow_obj in response_data['flows']:
                flow_match = None

                try:
                    flow_match = flow_obj['match']['tcp_src']
                except:
                    flow_match = None

                if flow_match != None:
                    flow_byte_count = int(flow_obj['byteCount'])
                    # print('flow_byte_count = ', flow_byte_count)
                    active_flows.append(flow_obj)

            return active_flows
        except:
            return []


    def isElephantFlow(self, flow_obj):
        try:
            flow_byte_count_arr = numpy.fromstring(flow_obj['byteCount'], dtype=numpy.uint32)
            flow_byte_count = flow_byte_count_arr[0]
            # print('flow_byte_count = {0}; threshold = {1}; EF = {2}'.format(flow_byte_count, ELEPHANT_FLOW_THRESHOLD, flow_byte_count >= ELEPHANT_FLOW_THRESHOLD))

            if flow_byte_count >= ELEPHANT_FLOW_THRESHOLD:
                return True

            return False
        except:
            return False

    def getFlowInfo(self, flow_to_get):
        active_flows = self.getActiveFlows()

        if flow_to_get:
            for flow in active_flows:
                flow_match_tcp_src = flow['match']['tcp_src']
                flow_match_tcp_dst = flow['match']['tcp_dst']

                flow_to_get_tcp_src = flow_to_get['tcp_src']
                flow_to_get_tcp_dst = flow_to_get['tcp_dst']

                if flow_match_tcp_src == flow_to_get_tcp_src and flow_match_tcp_dst == flow_to_get_tcp_dst:
                    return flow

        return None



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

            # 0       1     2       3             4      5        6     7      8    9      10
            #[0.1781 7.96   0.     0.1758 0.     0.     8.19   8.17   0.1793 4.035 4.035  0.     0.     0.     0.     0.    ]]

            ### S1
            if item['dpid'] == "00:00:00:00:00:00:00:01" and item['port'] == '1':
                #S1.1
                statistics_tx[0] = float(item['bits-per-second-tx'])

            elif item['dpid'] == "00:00:00:00:00:00:00:01" and item['port'] == '2':
                #S1.2
                statistics_tx[1] = float(item['bits-per-second-tx'])

            elif item['dpid'] == "00:00:00:00:00:00:00:01" and item['port'] == '3':
                #S1.3
                statistics_tx[2] = float(item['bits-per-second-tx'])

            ### S2
            elif item['dpid'] == "00:00:00:00:00:00:00:02" and item['port'] == '1':
                #S2.1
                statistics_tx[3] = float(item['bits-per-second-tx'])

            elif item['dpid'] == "00:00:00:00:00:00:00:02" and item['port'] == '2':
                #S2.2
                statistics_tx[4] = float(item['bits-per-second-tx'])

            elif item['dpid'] == "00:00:00:00:00:00:00:02" and item['port'] == '3':
                #S2.3
                statistics_tx[5] = float(item['bits-per-second-tx'])

            elif item['dpid'] == "00:00:00:00:00:00:00:02" and item['port'] == '4':
                #S2.4
                statistics_tx[6] = float(item['bits-per-second-tx'])

            ### S3
            elif item['dpid'] == "00:00:00:00:00:00:00:03" and item['port'] == '1':
                #S3.1
                statistics_tx[7] = float(item['bits-per-second-tx'])

            elif item['dpid'] == "00:00:00:00:00:00:00:03" and item['port'] == '2':
                #S3.2
                statistics_tx[8] = float(item['bits-per-second-tx'])

            elif item['dpid'] == "00:00:00:00:00:00:00:03" and item['port'] == '3':
                #S3.3
                statistics_tx[9] = float(item['bits-per-second-tx'])
            elif item['dpid'] == "00:00:00:00:00:00:00:03" and item['port'] == '4':
                #S3.4
                statistics_tx[10] = float(item['bits-per-second-tx'])

            ### S4
            elif item['dpid'] == "00:00:00:00:00:00:00:04" and item['port'] == '1':
                #S4.1
                statistics_tx[11] = float(item['bits-per-second-tx'])

            elif item['dpid'] == "00:00:00:00:00:00:00:04" and item['port'] == '2':
                #S4.2
                statistics_tx[12] = float(item['bits-per-second-tx'])

            elif item['dpid'] == "00:00:00:00:00:00:00:04" and item['port'] == '3':
                #S4.3
                statistics_tx[13] = float(item['bits-per-second-tx'])

            ### S1
            elif item['dpid'] == "00:00:00:00:00:00:00:05" and item['port'] == '1':
                #S5.1
                statistics_tx[14] = float(item['bits-per-second-tx'])
            elif item['dpid'] == "00:00:00:00:00:00:00:05" and item['port'] == '2':
                #S5.2
                statistics_tx[15] = float(item['bits-per-second-tx'])


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

    def getState2(self):
        state = []
        net_usage = numpy.zeros(shape=self.observation_space.shape)

        statistics_tx, timestamp = self.getStatisticsBandwidth()

        # Coleta utilização da rede
        for i in range(len(statistics_tx)):
            net_usage[i] = statistics_tx[i]  / (1024 * 1024) # valor em Mbits

        # Coleta fluxos e seus byte counts
        flows_byte_count = []
        active_flows_objs = self.getActiveFlows()

        """
        Fluxos que podemos considerar ativos (máximo de 8 simultaneos)
        state[1][0] = 46110 -> 5201
        state[1][1] = 46112 -> 5202
        state[1][2] = 46114 -> 5203
        state[1][3] = 46116 -> 5204
        state[1][4] = 46118 -> 5205
        state[1][5] = 46120 -> 5206
        state[1][6] = 46122 -> 5207
        state[1][7] = 46124 -> 5208

        state[1][8] = 5201 -> 46110
        state[1][9] = 5202 -> 46112
        state[1][10] = 5203 -> 46114
        state[1][11] = 5204 -> 46116
        state[1][12] = 5205 -> 46118
        state[1][13] = 5206 -> 46120
        state[1][14] = 5207 -> 46122
        state[1][15] = 5208 -> 46124

        """

        for flow in active_flows_objs:
            flow_byte_count = int(flow['byteCount'])

            if flow['match']['tcp_src'] == '46110':
                flows_byte_count[0] = flow_byte_count
            elif flow['match']['tcp_src'] == '46112':
                flows_byte_count[1] = flow_byte_count
            elif flow['match']['tcp_src'] == '46114':
                flows_byte_count[2] = flow_byte_count
            elif flow['match']['tcp_src'] == '46116':
                flows_byte_count[3] = flow_byte_count
            elif flow['match']['tcp_src'] == '46118':
                flows_byte_count[4] = flow_byte_count
            elif flow['match']['tcp_src'] == '46120':
                flows_byte_count[5] = flow_byte_count
            elif flow['match']['tcp_src'] == '46122':
                flows_byte_count[6] = flow_byte_count
            elif flow['match']['tcp_src'] == '46124':
                flows_byte_count[7] = flow_byte_count
            elif flow['match']['tcp_src'] == '5201':
                flows_byte_count[8] = flow_byte_count
            elif flow['match']['tcp_src'] == '5202':
                flows_byte_count[9] = flow_byte_count
            elif flow['match']['tcp_src'] == '5203':
                flows_byte_count[10] = flow_byte_count
            elif flow['match']['tcp_src'] == '5204':
                flows_byte_count[11] = flow_byte_count
            elif flow['match']['tcp_src'] == '5205':
                flows_byte_count[12] = flow_byte_count
            elif flow['match']['tcp_src'] == '5206':
                flows_byte_count[13] = flow_byte_count
            elif flow['match']['tcp_src'] == '5207':
                flows_byte_count[14] = flow_byte_count
            elif flow['match']['tcp_src'] == '5208':
                flows_byte_count[15] = flow_byte_count

        state[0] = net_usage
        state[1] = flows_byte_count
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

        if in_port == 0 and out_port == 0:
            # Regra que envia pacotes para o controlador
            rule_name = 'regra-{0}-controller--{1}:{2}-to-{3}:{4}'.format(switch_id, ipv4_src, tcp_src, ipv4_dst, tcp_dst)
            return {
                "switch": switch_id,
                "name": rule_name,
                "priority": "32760",
                "active": "true",
                "eth_type": "0x0800",
                "ipv4_src": ipv4_src,
                "ipv4_dst": ipv4_dst,
                "tcp_src": tcp_src,
                "tcp_dst": tcp_dst,
                "ip_proto": "0x06",
                "hard_timeout": "10", # timeout bem menor pois não queremos usar essa regra por muito tempo, apenas para sair do loop
                "actions": "output=controller"
            }


        else:
            rule_name = 'regra-{0}-in_{1}-out_{2}--{3}:{4}-to-{5}:{6}'.format(switch_id, in_port, out_port, ipv4_src, tcp_src, ipv4_dst, tcp_dst)
            return {
                "switch": switch_id,
                "name": rule_name,
                "priority": "32760",
                "in_port": str(numpy.int8(in_port)),
                "active": "true",
                "eth_type": "0x0800",
                "ipv4_src": ipv4_src,
                "ipv4_dst": ipv4_dst,
                "tcp_src": tcp_src,
                "tcp_dst": tcp_dst,
                "ip_proto": "0x06",
                "idle_timeout": "60",
                "actions": "output={0}".format(numpy.int8(out_port))
            }

    def existsRuleWithAction(self, switch_id, in_port, out_port, match):
        # Não instala regras repetidas para o mesmo match
       response = requests.get('{host}/wm/staticflowpusher/list/{switch_id}/json'.format(host=CONTROLLER_HOST, switch_id=switch_id))
       response_data = response.json()

       for item in response_data[switch_id]:
           for rule_name, rule in item.items():
               try:
                   if rule['match']['tcp_src'] == match['tcp_src'] and rule['match']['tcp_dst'] == match['tcp_dst']:
                       return rule_name
               except:
                   continue

       return None


    def step0(self, action):
        # Action indica uma ação para cada fluxo.
        # state[0] = net_usage
        # state[1] = flows_byte_count

        print('...........')
        done = False # Aprendizado continuado
        next_state = []
        reward = 0
        info = {}

        action_rule = action[0]
        action_flow = action[1]

        print('Action =', action)

        if action_rule == 33:
            next_state = self.getState()
            reward = 0

            print('State: {0} -- Reward = {1}'.format(self.state, reward))
            print('...........')
            print()

            return next_state, reward, done, info
        else:
            action_vec = actionWithFlowMap(action_rule)

            switch_index = action_vec[0]
            in_port_index = action_vec[1]
            out_port_index = action_vec[2]
            flow_index = action_vec[3]

            switch_id = self.switch_ids[switch_index]
            in_port = in_port_index + 1
            out_port = out_port_index + 1
            # flow_match = self.getMostCostlyFlow(switch_id) # em caso de agentes normais

            flow_match = flowMap(action_flow)

            rule_to_install = self.actionToRule(switch_id, in_port, out_port, flow_match)
            # print('Regra a ser instalada: ', rule)

            existing_rule_name = self.existsRuleWithAction(switch_id, in_port, out_port, flow_match)

            # acho que nao pode ter... posso querer mexer em um fluxo que antes era grande e agora tem um maior
            if existing_rule_name:
                # Desintala regra para não haver conflito
                response_uninstall = self.uninstallRule(existing_rule_name)
                # print('Resposta desinstalação: ', response_uninstall.json())

            response_install = self.installRule(rule_to_install)
            # print('Resposta instalação: ', response_install.json())

            time.sleep(7) # aguarda regras refletirem e pacotes serem enviados novamente

            next_state = self.getState()
            reward = self.calculateReward(next_state)
            self.state = next_state

            print('State: {0} -- Reward = {1}'.format(self.state, reward))
            print('...........')
            print()

            return next_state, reward, done, info


    def step(self, action):
        print('...........')
        done = False # Aprendizado continuado
        next_state = []
        reward = 0
        info = {}

        if action == 33:
            next_state = self.getState()
            reward = 0

            print('State: {0} -- Reward = {1}'.format(self.state, reward))
            print('...........')
            print()

            return next_state, reward, done, info
        else:
            action_vec = actionWithFlowMap(action)

            switch_index = action_vec[0]
            in_port_index = action_vec[1]
            out_port_index = action_vec[2]
            flow_index = action_vec[3]

            switch_id = self.switch_ids[switch_index]
            in_port = in_port_index + 1
            out_port = out_port_index + 1
            flow_match = flowMap(flow_index)

            rule_to_install = self.actionToRule(switch_id, in_port, out_port, flow_match)

            existing_rule_name = self.existsRuleWithAction(switch_id, in_port, out_port, flow_match)

            if existing_rule_name:
                response_uninstall = self.uninstallRule(existing_rule_name)

            response_install = self.installRule(rule_to_install)

            time.sleep(7) # aguarda regras refletirem e pacotes serem enviados novamente

            next_state = self.getState()
            reward = self.calculateReward(next_state, flow_match)
            self.state = next_state

            print('State: {0} -- Reward = {1}'.format(self.state, reward))
            print('...........')
            print()

            return next_state, reward, done, info


    def getNetworkUsageReward(self, state):
        total_usage_links = 0
        for i in range(len(state)):
            if state[i] > 1:
                total_usage_links += state[i] * 2
            else:
                # link não está sendo usado
                total_usage_links += 1

        s1_1_tx_mbps = state[0]
        s3_1_tx_mbps = state[7] # usado para detectar potencial estado de loop

        reward = float(total_usage_links * (s3_1_tx_mbps + s1_1_tx_mbps))

    def getHMeanReward(self, state):
        hmean = EPSILON
        if numpy.sum(state) < EPSILON:
            hmean = len(state) / numpy.sum(1.0/EPSILON)
        else:
            # soma máxima = 1/170 = 0.00588
            # hmean máxima = 9/0.00588 = 0,05292
            hmean = len(state) / numpy.sum(1.0/state)

        s1_1_tx_mbps = state[0]
        s3_1_tx_mbps = state[7] # usado para detectar potencial estado de loop


        # valor máximo considerando topologia 1 = 0,05292 * (50+50) = 5.29
        reward = float(hmean * (s3_1_tx_mbps + s1_1_tx_mbps))

        if reward < EPSILON:
            return EPSILON

        return reward

    def getSTDReward(self, state):
        std = numpy.std(state)

        s1_1_tx_mbps = state[0]
        s3_1_tx_mbps = state[7] # usado para detectar potencial estado de loop

        reward = float(std * (s3_1_tx_mbps + s1_1_tx_mbps))

        return reward

    def getElephantFlows(self):
        active_flows = self.getActiveFlows()
        elephant_flows = []

        for flow in active_flows:
            if self.isElephantFlow(flow):
                elephant_flows.append(flow)

        return elephant_flows


    def getLookAheadReward(self, state, flow_for_action):
        # Como olhar para o meu estado e penalizar decisões que mexem em fluxos que não são EF?
        # Com a equação aqui descrita, não precisaria de um IF EF pré agente,
        # pois qualquer ação que não envolva um EF, independente de qual seja, não será escolhida
        # pelo agente por conta da recompensa.
        elephant_flows = self.getElephantFlows()
        chosen_flow_is_elephant = False

        for ef in elephant_flows:
            if ef['match']['tcp_src'] == flow_for_action['tcp_src']:
                chosen_flow_is_elephant = True

        print('chosen_flow_is_elephant = ', chosen_flow_is_elephant)


        if flow_for_action == None or not chosen_flow_is_elephant:
            # recompensa deve ser muito baixa
            return MIN_LA_REWARD
        else:
            # escolheu EF para action
            hmean = self.getHMeanReward(state)
            reward = hmean + ELEPHANT_FLOW_REWARD_FACTOR
            return  reward

        # se o agente escolher um fluxo que já terminou, o estado se mantem o mesmo


    def calculateReward(self, state, flow_for_action):
        # Pega métricas de performance do controlador
        # response = requests.get('{host}/wm/performance/data/json'.format(host=CONTROLLER_HOST))
        # response_data = response.json()
        #
        # for item in response_data['modules']:
        #     if item['module-name'] == "net.floodlightcontroller.forwarding.Forwarding":
        #         forwarding_avg_time = item['average']
        #         break

        """ Agente A """
        # reward = self.getNetworkUsageReward(state)

        """ Agente B """
        # reward = self.getHMeanReward(state)

        """ Agente C """
        # reward = self.getSTDReward(state)

        """ Agente Look Ahead """
        reward = self.getLookAheadReward(state, flow_for_action)

        return reward


    def render(self, render='console'):
        self.state = self.getState()
        print('State = ', self.state)
