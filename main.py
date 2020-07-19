from agent.DQNAgent import DQNAgent

from graphModel.activeFlow import ActiveFlow
from graphModel.flow import Flow
from graphModel.graph import Graph
from graphModel.link import Link
from graphModel.node import Node

# from routing.binPacking import BinPackingRouting

from utilities.actionToRules import actionToRules
from utilities.staticFlowPusher import StaticFlowPusher

import load_balance_gym

import gym
import requests
import time

from operator import attrgetter

CONTROLLER_IP = 'http://0.0.0.0'
CONTROLLER_HOST = '{CONTROLLER_IP}:8080'

THRESHOLD_TIME_SEC = 10 # IDEAFIX uses 10 seg
THRESHOLD_SIZE = 10485760 # 10MB

SPLIT_FLOW_LOOP_TIME_SEC = 3
MAX_LOOP_DURATION_MIN = 2

# Reinforcement Learning Agent configs
NUM_EPISODES = 1000


class LookAheadRLApp(object):
    def __init__(self):
        self.network_graph = Graph()
        # self.routing_model = BinPackingRouting()
        self.switch_info = {} # dicionário cuja chave é o MAC do switch. Ex: current_flows["00:00:00:00:00:00:00:01"]
        self.active_flows = [] # lista de ActiveFlow: active_flows = ['F1', 'F2']
        self.links_usage = []
        self.switch_ids = {
            'S1': '00:00:00:00:00:00:00:01',
            'S2': '00:00:00:00:00:00:00:02',
            'S3': '00:00:00:00:00:00:00:03',
            'S4': '00:00:00:00:00:00:00:04',
            'S5': '00:00:00:00:00:00:00:05'
        }
        self.flow_count = 0
        self.flow_pusher = StaticFlowPusher(CONTROLLER_IP)

        self.active_flows_id = []
        self.active_flows_paths = {} # {
        #     'F1': [['A', 'B', 'F', 'I']],
        #     'F2': [['A', 'B', 'F', 'I']]
        # }
        self.active_flows_size = {}

        self.initial_usage = [
            0,    # A
            0,    # B
            0,    # C
            0,    # D
            0,    # E
            0,    # F
            0,    # G
            0,    # H
            0     # I
        ]

        env = gym.make('Load-Balance-v1', usage=self.initial_usage)
        self.agent = DQNAgent(env)

        self.enableSwitchStatisticsEndpoit()

    def initializeNetworkGraph(self):
        switches_response = requests.get('{host}/wm/core/controller/switches/json'.format(host=CONTROLLER_HOST))
        switches_response_data = switches_response.json()

        switches = []
        for item in switches_response_data:
            switch_node = Node(
                id=item['switchDPID'],
                inetAddress=item['inetAddress'],
                connectedSince=item['connectedSince']
            )
            switches.append(switch_node)

        self.network_graph.setNodes(switches)

        links_response = requests.get('{host}/wm/topology/links/json'.format(host=CONTROLLER_HOST))
        links_response_data = links_response.json()

        links = []
        for item in links_response_data:
            node1_id = item['src-switch']
            node1_port = item['src-port']
            node2_id = item['dst-switch']
            node2_port = item['dst-port']

            node1 = self.network_graph.getNodeById(node1_id)
            node2 = self.network_graph.getNodeById(node2_id)

            if node1 == None:
                print('Error finding node {0} on network graph'.format(node1_id))
            if node2 == None:
                print('Error finding node {0} on network graph'.format(node2_id))

            link = Link(node1, node2, node1_port, node2_port)
            links.append(link)

        self.network_graph.setLinks(links)

        self.network_graph.createCostMatrix()
        self.network_graph.printCostMatrix()


    def getNetworkSummary(self):
        response = requests.get('{host}/wm/core/controller/summary/json'.format(host=CONTROLLER_HOST))
        response_data = response.json()

        return response_data

    def getPossiblePaths(self, src_dpid, dst_dpid, num_paths):
        # GET /wm/routing/paths/<src-dpid>/<dst-dpid>/<num-paths>/json
        # Get an ordered list of paths from the shortest to the longest path
        response = requests.get('{host}/wm/routing/paths/{src}/{dst}/{num_paths}/json'.format(
            host=CONTROLLER_HOST,
            src=src_dpid,
            dst=dst_dpid,
            num_paths=num_paths
        ))
        response_data = response.json()

        return response_data

    def getPossiblePaths(self, src_dpid, dst_dpid):
        # GET /wm/routing/paths/<src-dpid>/<dst-dpid>/<num-paths>/json
        # Get an ordered list of paths from the shortest to the longest path
        response = requests.get('{host}/wm/routing/paths/{src}/{dst}/json'.format(
            host=CONTROLLER_HOST,
            src=src_dpid,
            dst=dst_dpid
        ))
        response_data = response.json()

        return response_data

    def containsFlowAsActive(self, flow):
        for item in self.active_flows:
            if flow.id == item.id:
                return True
        return False

    def getFlow(self, flow_id):
        for item in self.active_flows:
            if flow_id == item.id:
                return item
        return None

    def addActiveFlow(self, flow):
        # # TODO: talvez não faça sentido verificar se o flow já está na lista. O Controle será feito por mim.
        if not self.containsFlowAsActive(flow):
            self.active_flows.append(flow)

            # TODO pegar mais infos do flow e atualizar variaveis

            flow_id = 'flow-{self.flow_count}'
            self.flow_paths[flow_id] = []
            self.flow_sizes[flow_id] = 0

            self.flow_count = self.flow_count + 1

    def getActiveFlows(self):
        pass

    def setFlowsSnapshots(self):
        # List of all devices tracked by the controller. This includes MACs, IPs, and attachment points.
        response = requests.get('{host}/wm/core/switch/all/flow/json'.format(host=CONTROLLER_HOST))
        response_data = response.json()

        print(response_data)
        return None

        # Guarda todos os fluxos relativos a cada switch
        for item in response_data:
            # item é o switch DPID
            self.switch_info[item] = response_data[item]

        # Para cada fluxo ativo em cada um dos switches
        for switch_id in self.switch_info.keys():
            for flow in self.switch_info[switch_id]['flows']:
                if flow['match']: # checa se existem fluxos correntes
                    flow_id = '{eth_dst}-{eth_src}-{in_port}-{eth_type}'.format(
                        eth_dst=flow['match']["eth_dst"],
                        eth_src=flow['match']["eth_src"],
                        in_port=flow['match']["in_port"],
                        eth_type=flow['match']["eth_type"]
                    )
                    flow_item = self.getFlow(flow_id)

                    if flow_item:
                        # Se o fluxo já existe (ou seja, é um fluxo ativo na rede), appenda features
                        snapshot = [
                            flow["hard_timeout_s"],
                            flow["byte_count"],
                            flow["idle_timeout_s"],
                            flow["packet_count"],
                            flow["duration_sec"]
                        ]
                        flow_item.features.append(snapshot)
                    else:
                        ## É um novo fluxo na rede

                        # considera pacotes sem IPv4 (ex. ARP)
                        contains_ipv4_info = True if "ipv4_dst" in flow['match'].keys() else False
                        ipv4_dst = flow['match']["ipv4_dst"] if contains_ipv4_info else None
                        ipv4_src = flow['match']["ipv4_src"] if contains_ipv4_info else None

                        new_flow = ActiveFlow(
                            eth_dst=flow['match']["eth_dst"],
                            eth_src=flow['match']["eth_src"],
                            ipv4_dst=ipv4_dst,
                            ipv4_src=ipv4_src,
                            eth_type=flow['match']["eth_type"],
                            in_port=flow['match']["in_port"]
                        )
                        snapshot = [
                            flow["hard_timeout_s"],
                            flow["byte_count"],
                            flow["idle_timeout_s"],
                            flow["packet_count"],
                            flow["duration_sec"]
                        ]
                        new_flow.features.append(snapshot)
                        self.active_flows.append(new_flow)

    def listNetworkDevices(self):
        # List static flows for a switch or all switches
        response = requests.get('{host}/wm/device'.format(host=CONTROLLER_HOST))
        response_data = response.json()

        return response

    # Só será utilizado quando tivermos mais de um fluxo na rede (afinal, nosso
    # foco é balanceamento de carga)
    def findBinPackingRoutes(self, source, target):
        flows_running_on_network = self.getNetworkCurrentFlows()

        # Retorna um dicionario do tipo path_per_flow[FLOW_ID] = PATH
        path_per_flow = self.routing_model.findPaths(flows)
        return path_per_flow

    def enableSwitchStatisticsEndpoit(self):
        # Enable statistics collection
        response = requests.post(
            '{host}/wm/statistics/config/enable/json'.format(host=CONTROLLER_HOST),
            data={}
        )
        response_data = response.json()

        return response_data

    def setSwitchStatistics(self):
        # Get statistics from all switches
        response = requests.get('{host}/wm/statistics/bandwidth/all/all/json'.format(host=CONTROLLER_HOST))
        response_data = response.json()

        for item in response_data:
            switch_dpid = item["dpid"]
            # item é um objeto com o formato:
            #    {
            #       "bits-per-second-rx" : "0",
            #       "dpid" : "00:00:00:00:00:00:00:02",
            #       "updated" : "Mon Sep 02 15:54:17 EDT 2019",
            #       "link-speed-bits-per-second" : "10000000",
            #       "port" : "1",
            #       "bits-per-second-tx" : "6059"
            #    }
            self.switch_info[switch_dpid]["statistics"] = item

    def getLinksUsage(self):
        # Deve retornar uma lista no formato:
        # initial_usage = [
        #     700,    # A
        #     700,    # B
        #     0,      # C
        #     0,      # D
        #     0,      # E
        #     700,    # F
        #     0,      # G
        #     0,      # H
        #     700     # I
        # ]
        # Get statistics from all switches
        response = requests.get('{host}/wm/statistics/bandwidth/all/all/json'.format(host=CONTROLLER_HOST))
        response_data = response.json()

        links_usage = list(self.links_usage)

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
            if item['dpid'] == '1' and item['port'] == '1':
                # link A
                links_usage[0] = item['bits-per-second-rx']

            elif item['dpid'] == '2' and item['port'] == '1':
                # link B
                links_usage[1] = float(item['bits-per-second-rx'])

            elif item['dpid'] == '4' and item['port'] == '1':
                # link C
                links_usage[2] = float(item['bits-per-second-rx'])

            elif item['dpid'] == '4' and item['port'] == '2':
                # link E
                links_usage[4] = float(item['bits-per-second-rx'])

            elif item['dpid'] == '5' and item['port'] == '1':
                # link D
                links_usage[3] = float(item['bits-per-second-rx'])

            elif item['dpid'] == '3' and item['port'] == '2':
                # link F
                links_usage[5] = float(item['bits-per-second-rx'])

            elif item['dpid'] == '3' and item['port'] == '4':
                # link H
                links_usage[7] = float(item['bits-per-second-rx'])

            elif item['dpid'] == '3' and item['port'] == '3':
                # link G
                links_usage[6] = float(item['bits-per-second-rx'])

            elif item['dpid'] == '00:00:00:00:00:02' and item['port'] == '1':
                # link I
                links_usage[8] = float(item['bits-per-second-rx'])

        return links_usage

    def isElephantFlow(self, flow):
        if flow.duration_sec > THRESHOLD_TIME_SEC and flow.byte_count > THRESHOLD_SIZE:
            return True
        return False

    def getRulesFromAction(self, action, flow_to_reroute):
        # self.links_usage
        # como identificar fluxos ativos na rede? o fluxo mais recente, maior?
        fixed_rules, loop_rules = actionToRules(action, current_paths, flow_name, self.switch_ids)
        return fixed_rules, loop_rule

    def installRule(self, rule):
        return self.flow_pusher.set(rule)

    def uninstallRule(self, rule):
        return self.flow_pusher.remove(rule)

    def performAction(self, action, flow_to_reroute):
        fixed_rules, loop_rules = getRulesFromAction(action, flow_to_reroute)

        for rule in fixed_rules:
            self.installRule(rule)

        if len(loop_rules):
            # Slip entre caminhos
            # Assumindo que o fluxo elephant vai durar pelo menos THRESHOLD_TIME_SEC segundos + pelo menos 3 * SPLIT_FLOW_LOOP_TIME_SEC
            # Usando threshold de 10seg + split time de 2 seg = o elephant flow deve durar pelo menos 16 segundos. (Máximo de 3min?)

            # Para garantir que não há perda de pacotes: usamos a primeira regra como base e iteramos sobre a outra.
            self.installRule(loop_rules[0])

            t_end = time.time() + 60 * MAX_LOOP_DURATION_MIN # tempo máximo de duração do loop é de 2 minutos
            while time.time() < t_end:
                for rule in loop_rules:
                    self.installRule(rule)
                    time.sleep(SPLIT_FLOW_LOOP_TIME_SEC)
                    self.uninstallRule(rule)
                    # Atenção: neste instante, até que a nova regra seja instalada, os pacotes serão enviados pela primeira rota.

    def executeTrainingPhase(self):
        # rodar por 10min ?
        while True:
            # Coleta estatísticas
            self.setSwitchStatistics()
            self.setFlowsSnapshots()

            self.active_flows_id, self.active_flows_paths, self.active_flows_size = self.getActiveFlows()

            if self.containsElephantFlow():
                # action = self.env.action_space.sample()
                # state, reward, done, info = self.env.step(action)

                # flow_to_reroute = 'F2'
                # flow_to_reroute_size = self.flow_sizes[flow_to_reroute]
                # flow_to_reroute_paths = self.flow_paths[flow_to_reroute]

                # next_state, reward, done, info = env.step(
                #     action=action,
                #     flow_total_size=flow_to_reroute_size,
                #     flow_current_paths=flow_to_reroute_paths
                # )
                #
                # self.performAction(action, flow_to_reroute)

                # # Updates flow information
                # self.flow_paths[flow_to_reroute] = info['next_paths']

            # time.sleep(5)

    def run(self):
        # Initialize variables
        self.enableSwitchStatisticsEndpoit()
        self.initializeNetworkGraph()
        self.initial_usage = self.getLinksUsage()

        # Aguarda inicio de fluxos
        time.sleep(10)

        # self.executeTrainingPhase()

        while True:
            # Coleta estatísticas
            self.setSwitchStatistics()
            self.setFlowsSnapshots()

            # TODO: como diferenciar fluxos com o mesmo ip de origem, destino e protocolo?
            time.sleep(5)

            # self.active_flows_id, self.active_flows_paths, self.active_flows_size = self.getActiveFlows()
            #
            # if self.containsElephantFlow():
                # action = self.env.action_space.sample()
                # state, reward, done, info = self.env.step(action)

                # flow_to_reroute = 'F2'
                # flow_to_reroute_size = self.flow_sizes[flow_to_reroute]
                # flow_to_reroute_paths = self.flow_paths[flow_to_reroute]

                # next_state, reward, done, info = env.step(
                #     action=action,
                #     flow_total_size=flow_to_reroute_size,
                #     flow_current_paths=flow_to_reroute_paths
                # )
                #
                # self.performAction(action, flow_to_reroute)

                # # Updates flow information
                # self.flow_paths[flow_to_reroute] = info['next_paths']

            # time.sleep(5)


if __name__ == '__main__':
    app = LookAheadRLApp()
    app.run()
