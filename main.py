from agent.DQNAgent import DQNAgent

from graphModel.activeFlow import ActiveFlow
from graphModel.flow import Flow
from graphModel.graph import Graph
from graphModel.link import Link
from graphModel.node import Node

# from routing.binPacking import BinPackingRouting

from utilities.actionToRules import actionToRules
from utilities.rulesToLink import rulesToLink
# from utilities.staticFlowPusher import StaticFlowPusher # cant use http module with python 3.6 because of openssl issues

import load_balance_gym

import gym
import requests
import re
import time

from operator import attrgetter

CONTROLLER_IP = 'http://0.0.0.0'
CONTROLLER_HOST = '{host}:8080'.format(host=CONTROLLER_IP)
LLDP_PACKAGE_SIZE = 60

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
        self.active_flows = [] # lista de ActiveFlow: active_flows = ['F1', 'F2']
        self.switch_ids = {
            'S1': '00:00:00:00:00:00:00:01',
            'S2': '00:00:00:00:00:00:00:02',
            'S3': '00:00:00:00:00:00:00:03',
            'S4': '00:00:00:00:00:00:00:04',
            'S5': '00:00:00:00:00:00:00:05'
        }

        self.switch_address_to_id = {
            '00:00:00:00:00:00:00:01': 'S1',
            '00:00:00:00:00:00:00:02': 'S2',
            '00:00:00:00:00:00:00:03': 'S3',
            '00:00:00:00:00:00:00:04': 'S4',
            '00:00:00:00:00:00:00:05': 'S5'
        }

        self.switch_info = {
            '00:00:00:00:00:00:00:01': {},
            '00:00:00:00:00:00:00:02': {},
            '00:00:00:00:00:00:00:03': {},
            '00:00:00:00:00:00:00:04': {},
            '00:00:00:00:00:00:00:05': {}
        } # dicionário cuja chave é o MAC do switch. Ex: current_flows["00:00:00:00:00:00:00:01"]


        self.flow_count = 0
        # self.flow_pusher = StaticFlowPusher(CONTROLLER_IP)

        self.active_flows_id = []
        self.active_flows_paths = {} # {
        #     'F1': [['A', 'B', 'F', 'I']],
        #     'F2': [['A', 'B', 'F', 'I']]
        # }
        self.active_flows_size = {}

        self.links_usage = [
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

        env = gym.make('Load-Balance-v1', usage=self.links_usage)
        self.agent = DQNAgent(env)


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
        # self.network_graph.printCostMatrix()


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

    def addActiveFlow(self, flow_id):
        self.active_flows_id.append(flow_id)
        self.active_flows_size[flow_id] = 0 # inicializa
        self.flow_count = self.flow_count + 1

    def updateFlowPaths(self, flow_id, flow_paths):
        self.active_flows_paths[flow_id] = flow_paths

    def updateFlowSize(self, flow_id, flow_byte_counts):
        mean_byte_count = sum(flow_byte_counts) / len(flow_byte_counts)
        self.active_flows_size[flow_id] = mean_byte_count

    def updateFlowStatistics(self):
        # Objetivos:
        # 1. acrescentar/remover na lista de fluxos ativos
        # 2. Atualizar tamanho do fluxo
        # 3. Atualizar rotas do fluxo
        response = requests.get('{host}/wm/core/switch/all/flow/json'.format(host=CONTROLLER_HOST))
        response_data = response.json()

        flow_ids_to_update = []
        flow_paths = {}
        flow_size = {} # guarda o tamanho do fluxo em cada link, para no final fazer uma media

        for switch_address in response_data:
            for flow in response_data[switch_address]['flows']:
                contains_match = len(flow['match'].keys()) > 1

                if contains_match:
                    is_tcp_flow = False
                    tcp_src_port = None
                    try:
                        tcp_src_port = flow['match']['tcp_src']
                        is_tcp_flow = tcp_src_port or 0
                    except:
                        is_tcp_flow = False

                    if is_tcp_flow:
                        flow_id = 'flow-{tcp_src_port}'.format(tcp_src_port=tcp_src_port)
                        flow_ids_to_update.append(flow_id)

                        # Se não existir na lista de fluxos ativos, adiciona
                        if flow_id not in self.active_flows_id:
                            self.addActiveFlow(flow_id)

                            # Atualiza rotas pelas quais passa - variável auxiliar
                            flow_paths[flow_id] = []

                            # Atualiza tamanho do fluxo por link - variável auxiliar
                            flow_size[flow_id] = []

                        # Atualiza rotas pelas quais passa - variável auxiliar
                        in_port = flow['match']['in_port']
                        out_port_plain_text = flow['instructions']['instruction_apply_actions']['actions']
                        print('isadora', re.split(out_port_plain_text, '\d+'))
                        out_port = re.split(out_port_plain_text, '\d+')

                        link = rulesToLink(switch_address, out_port)
                        flow_paths[flow_id].append(link)

                        # Adiciona na lista para ter seu tamanho total atualizado
                        flow_size[flow_id].append(flow['byte_count'])

        for flow_id in flow_ids_to_update:
            self.updateFlowPaths(flow_id, flow_paths[flow_id])
            self.updateFlowSize(flow_id, flow_size[flow_id])


    def setFlowsSnapshots(self):
        # List of all devices tracked by the controller. This includes MACs, IPs, and attachment points.
        response = requests.get('{host}/wm/core/switch/all/flow/json'.format(host=CONTROLLER_HOST))
        response_data = response.json()

        print('isadora response_data', response_data)
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
        response = requests.post('{host}/wm/statistics/config/enable/json'.format(host=CONTROLLER_HOST), data={})
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
        # usage = [
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
            print('item', item)
            is_link_A = item['dpid'] == self.switch_ids['S1'] and item['port'] == '1'
            is_link_B = item['dpid'] == self.switch_ids['S2'] and item['port'] == '1'
            is_link_C = item['dpid'] == self.switch_ids['S4'] and item['port'] == '1'
            is_link_D = item['dpid'] == self.switch_ids['S5'] and item['port'] == '1'
            is_link_E = item['dpid'] == self.switch_ids['S4'] and item['port'] == '2'
            is_link_F = item['dpid'] == self.switch_ids['S3'] and item['port'] == '2'
            is_link_G = item['dpid'] == self.switch_ids['S3'] and item['port'] == '3'
            is_link_H = item['dpid'] == self.switch_ids['S3'] and item['port'] == '4'
            is_link_I = item['dpid'] == self.switch_ids['S3'] and item['port'] == '1' # TODO: como ver quanto que o host H2 está recebendo?

            if is_link_A:
                links_usage[0] = float(item['bits-per-second-rx'])

            elif is_link_B:
                links_usage[1] = float(item['bits-per-second-rx'])

            elif is_link_C:
                links_usage[2] = float(item['bits-per-second-rx'])

            elif is_link_E:
                links_usage[4] = float(item['bits-per-second-rx'])

            elif is_link_D:
                links_usage[3] = float(item['bits-per-second-rx'])

            elif is_link_F:
                links_usage[5] = float(item['bits-per-second-rx'])

            elif is_link_H:
                links_usage[7] = float(item['bits-per-second-rx'])

            elif is_link_G:
                links_usage[6] = float(item['bits-per-second-rx'])

            elif is_link_I:
                links_usage[8] = float(item['bits-per-second-tx'])

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
        urlPath = '{host}/wm/staticentrypusher/json'.format(host=CONTROLLER_HOST)
        headers = {
            'Content-type': 'application/json',
            'Accept': 'application/json',
            }

        return requests.post(urlPath, data=rule, headers=headers)
        # return self.flow_pusher.set(rule)

    def uninstallRule(self, rule):
        urlPath = '{host}/wm/staticentrypusher/json'.format(host=CONTROLLER_HOST)
        headers = {
            'Content-type': 'application/json',
            'Accept': 'application/json',
            }

        return requests.delete(urlPath, data=rule, headers=headers)
        # return self.flow_pusher.remove(rule)

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
            # self.setSwitchStatistics()
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
                pass

            # time.sleep(5)



    def printDebugInfo(self, step):
        print('-- Step {0} --'.format(step))
        print('Usage = {0}'.format(self.links_usage))
        print('Active flows = {0}'.format(self.active_flows))
        print('Flows paths = {0}'.format(self.active_flows_paths))
        print('Flows size = {0}'.format(self.active_flows_size))


    def run(self):
        # Initialize variables
        print('Running environment...')
        step = 0

        self.enableSwitchStatisticsEndpoit()
        self.initializeNetworkGraph()
        self.updateFlowStatistics()
        self.links_usage = self.getLinksUsage()

        self.printDebugInfo(step)
        step = step + 1

        time.sleep(10)

        # self.executeTrainingPhase()
        while True:
            # Coleta estatísticas
            # self.setSwitchStatistics()

            self.links_usage = self.getLinksUsage()
            self.updateFlowStatistics()

            self.printDebugInfo(step)
            step = step + 1

            # self.setFlowsSnapshots()

            time.sleep(1)

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
