import gym
from gym import spaces, utils
from gym.utils import seeding

from .action_rules_map_s10 import actionMap

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
        self.num_links = 0

        self.discoverTopology()

        self.observation_space = spaces.Box(
            low=0,
            high=10485760, # maximo = 10Mbps = 10 * 1024 * 1024
            shape=(35,), # array com o RX de cada porta = 34 portas
            dtype=numpy.float16
        )

        self.action_space = spaces.Discrete(77)

        self.state = numpy.zeros(shape=self.observation_space.shape)
        self.prev_state = numpy.zeros(shape=self.observation_space.shape)
        self.reward_range = (0, 1400000) # max = 35 * 2 * 100 * (100 + 100) (100 é capacidade do link S3.1)

        self.previous_tx = numpy.zeros(shape=self.observation_space.shape)
        self.previous_timestamp = None
        self.initializeState()

    def initializeState(self):
        statistics_tx, timestamp = self.getStatisticsBandwidth()

        self.previous_tx = statistics_tx
        self.previous_timestamp = timestamp


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
            self.saveItemSwitchIds(item)

        self.switch_ids = sorted(self.switch_ids)

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
                statistics_tx[0] = float(item['bits-per-second-tx'])

            elif item['dpid'] == "00:00:00:00:00:00:00:01" and item['port'] == '2':
                #S1.2
                statistics_tx[1] = float(item['bits-per-second-tx'])

            elif item['dpid'] == "00:00:00:00:00:00:00:01" and item['port'] == '3':
                #S1.3
                statistics_tx[2] = float(item['bits-per-second-tx'])

            elif item['dpid'] == "00:00:00:00:00:00:00:01" and item['port'] == '4':
                #S1.4
                statistics_tx[3] = float(item['bits-per-second-tx'])

            elif item['dpid'] == "00:00:00:00:00:00:00:01" and item['port'] == '5':
                #S1.5
                statistics_tx[4] = float(item['bits-per-second-tx'])

            ### S2
            elif item['dpid'] == "00:00:00:00:00:00:00:02" and item['port'] == '1':
                #S2.1
                statistics_tx[5] = float(item['bits-per-second-tx'])

            elif item['dpid'] == "00:00:00:00:00:00:00:02" and item['port'] == '2':
                #S2.2
                statistics_tx[6] = float(item['bits-per-second-tx'])

            elif item['dpid'] == "00:00:00:00:00:00:00:02" and item['port'] == '3':
                #S2.3
                statistics_tx[7] = float(item['bits-per-second-tx'])

            elif item['dpid'] == "00:00:00:00:00:00:00:02" and item['port'] == '4':
                #S2.4
                statistics_tx[8] = float(item['bits-per-second-tx'])
            elif item['dpid'] == "00:00:00:00:00:00:00:02" and item['port'] == '5':
                #S2.5
                statistics_tx[9] = float(item['bits-per-second-tx'])

            ### S3
            elif item['dpid'] == "00:00:00:00:00:00:00:03" and item['port'] == '1':
                #S3.1
                statistics_tx[10] = float(item['bits-per-second-tx'])

            elif item['dpid'] == "00:00:00:00:00:00:00:03" and item['port'] == '2':
                #S3.2
                statistics_tx[11] = float(item['bits-per-second-tx'])

            elif item['dpid'] == "00:00:00:00:00:00:00:03" and item['port'] == '3':
                #S3.3
                statistics_tx[12] = float(item['bits-per-second-tx'])
            elif item['dpid'] == "00:00:00:00:00:00:00:03" and item['port'] == '4':
                #S3.4
                statistics_tx[13] = float(item['bits-per-second-tx'])
            elif item['dpid'] == "00:00:00:00:00:00:00:03" and item['port'] == '5':
                #S3.5
                statistics_tx[14] = float(item['bits-per-second-tx'])

            ### S4
            elif item['dpid'] == "00:00:00:00:00:00:00:04" and item['port'] == '1':
                #S4.1
                statistics_tx[15] = float(item['bits-per-second-tx'])

            elif item['dpid'] == "00:00:00:00:00:00:00:04" and item['port'] == '2':
                #S4.2
                statistics_tx[16] = float(item['bits-per-second-tx'])

            elif item['dpid'] == "00:00:00:00:00:00:00:04" and item['port'] == '3':
                #S4.3
                statistics_tx[17] = float(item['bits-per-second-tx'])
            elif item['dpid'] == "00:00:00:00:00:00:00:04" and item['port'] == '4':
                #S4.4
                statistics_tx[18] = float(item['bits-per-second-tx'])


            ### S5
            elif item['dpid'] == "00:00:00:00:00:00:00:05" and item['port'] == '1':
                #S5.1
                statistics_tx[19] = float(item['bits-per-second-tx'])
            elif item['dpid'] == "00:00:00:00:00:00:00:05" and item['port'] == '2':
                #S5.2
                statistics_tx[20] = float(item['bits-per-second-tx'])
            elif item['dpid'] == "00:00:00:00:00:00:00:05" and item['port'] == '3':
                #S5.3
                statistics_tx[21] = float(item['bits-per-second-tx'])

            ### S6
            elif item['dpid'] == "00:00:00:00:00:00:00:06" and item['port'] == '1':
                #S6.1
                statistics_tx[22] = float(item['bits-per-second-tx'])
            elif item['dpid'] == "00:00:00:00:00:00:00:06" and item['port'] == '2':
                #S6.2
                statistics_tx[23] = float(item['bits-per-second-tx'])
            elif item['dpid'] == "00:00:00:00:00:00:00:06" and item['port'] == '3':
                #S6.3
                statistics_tx[24] = float(item['bits-per-second-tx'])


            ### S7
            elif item['dpid'] == "00:00:00:00:00:00:00:07" and item['port'] == '1':
                #S7.1
                statistics_tx[25] = float(item['bits-per-second-tx'])
            elif item['dpid'] == "00:00:00:00:00:00:00:07" and item['port'] == '2':
                #S7.2
                statistics_tx[26] = float(item['bits-per-second-tx'])

            ### S8
            elif item['dpid'] == "00:00:00:00:00:00:00:08" and item['port'] == '1':
                #S8.1
                statistics_tx[27] = float(item['bits-per-second-tx'])
            elif item['dpid'] == "00:00:00:00:00:00:00:08" and item['port'] == '2':
                #S8.2
                statistics_tx[28] = float(item['bits-per-second-tx'])

            ### S9
            elif item['dpid'] == "00:00:00:00:00:00:00:09" and item['port'] == '1':
                #S9.1
                statistics_tx[29] = float(item['bits-per-second-tx'])
            elif item['dpid'] == "00:00:00:00:00:00:00:09" and item['port'] == '2':
                #S9.2
                statistics_tx[30] = float(item['bits-per-second-tx'])
            elif item['dpid'] == "00:00:00:00:00:00:00:09" and item['port'] == '3':
                #S9.3
                statistics_tx[31] = float(item['bits-per-second-tx'])

            ### S10
            elif item['dpid'] == "00:00:00:00:00:00:00:10" and item['port'] == '1':
                #S10.1
                statistics_tx[32] = float(item['bits-per-second-tx'])
            elif item['dpid'] == "00:00:00:00:00:00:00:10" and item['port'] == '2':
                #S10.2
                statistics_tx[34] = float(item['bits-per-second-tx'])


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
                "hard_timeout": "60",
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

    def getMostCostlyFlow(self, switch_id):
        # Retorna o fluxo que exige mais do switch
        response = requests.get('{host}/wm/core/switch/{switch_id}/flow/json'.format(host=CONTROLLER_HOST, switch_id=switch_id))
        response_data = response.json()

        max_byte_count = -1
        max_usage_flow_match = None

        for flow_obj in response_data['flows']:
            flow_cookie = flow_obj['cookie']
            flow_match = None

            try:
                flow_match = flow_obj['match']['tcp_src']
            except:
                flow_match = None

            if flow_match != None:
                flow_byte_count = int(flow_obj['byteCount'])
                if flow_byte_count > max_byte_count:
                    max_byte_count = flow_byte_count
                    max_usage_flow_match = flow_obj['match']

        # print('[getMostCostlyFlow] max_usage_flow_match: {0} - max_byte_count: {1}'.format(max_usage_flow_match, max_byte_count))

        return max_usage_flow_match

    def step(self, action):
        print('...........')
        done = False # Aprendizado continuado
        next_state = []
        reward = 0
        info = {}

        print('Action =', action)
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
            # print('Regra a ser instalada: ', rule)

            existing_rule_name = self.existsRuleWithAction(switch_id, in_port, out_port, flow_match)

            # acho que nao pode ter... posso querer mexer em um fluxo que antes era grande e agora tem um maior
            if existing_rule_name:
                # Desintala regra para não haver conflito
                response_uninstall = self.uninstallRule(existing_rule_name)
                # print('Resposta desinstalação: ', response_uninstall.json())

            response_install = self.installRule(rule)
            # print('Resposta instalação: ', response_install.json())

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
            # print('Sem regra a ser instalada.')

            next_state = self.getState()
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

        s1_1_tx_mbps = state[0]
        s3_1_tx_mbps = state[10] # usado para detectar potencial estado de loop

        reward = float(total_usage_links * (s3_1_tx_mbps + s1_1_tx_mbps))

        return reward


    def render(self, render='console'):
        self.state = self.getState()
        print('State = ', self.state)
