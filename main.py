# -*- coding: utf-8 -*-

from graphModel.flow import Flow
from graphModel.graph import Graph
from graphModel.link import Link
from graphModel.node import Node

from routing.binPacking import BinPackingRouting

from operator import attrgetter

import requests
import time

CONTROLLER_HOST = 'http://0.0.0.0:8080'


class LookAheadRLApp(object):
    def __init__(self):
        self.network_graph = Graph()
        self.routing_model = BinPackingRouting()
        self.switch_info = {} # dicionário cuja chave é o MAC do switch. Ex: current_flows["00:00:00:00:00:00:00:01"]

    def initializeNetworkGraph(self):
        # 1. Consome topologia floodlight
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
        print('Network summary: ')
        response = requests.get('{host}/wm/core/controller/summary/json'.format(host=CONTROLLER_HOST))
        response_data = response.json()

        return response_data

    def setSwitchCurrentFlows(self):
        # List of all devices tracked by the controller. This includes MACs, IPs, and attachment points.
        response = requests.get('{host}/wm/core/switch/all/flow/json'.format(host=CONTROLLER_HOST))
        response_data = response.json()

        for item in response_data:
            # item é o switch DPID
            self.switch_info[item] = response_data[item]

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


    def run(self):
        self.initializeNetworkGraph()
        self.routing_model.setNetworkGraph(self.network_graph)

        self.enableSwitchStatisticsEndpoit()

        # # Testando caminho de custo mínimo
        # source_switch_id = '00:00:00:00:00:00:00:01'
        # target_switch_id = '00:00:00:00:00:00:00:06'
        #
        # # Procura caminho de custo mínimo entre dois switches
        # # custo = 1 / capacidade_atual
        # min_cost_path = self.network_graph.getMinimumCostPath(source_switch_id, target_switch_id)
        # print('Caminho de custo minimo entre 1 e 6: {0}\n'.format(min_cost_path))
        #
        # self.getNetworkSummary()
        # self.listNetworkDevices()

        # Fluxos correntes e estatítiscas estão aramazenados em self.switch_info
        self.setSwitchCurrentFlows()
        self.setSwitchStatistics()

        # Usar estatísticas do fluxo para prever o tamanho total dele



if __name__ == '__main__':
    app = LookAheadRLApp()
    app.run()
