# -*- coding: utf-8 -*-

from graphModel.flow import Flow
from graphModel.graph import Graph
from graphModel.link import Link
from graphModel.node import Node

from operator import attrgetter

import requests

CONTROLLER_HOST = 'http://0.0.0.0:8080'


class LookAheadRLApp(object):
    def __init__(self):
        self.networkGraph = Graph()

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

        self.networkGraph.setNodes(switches)


        links_response = requests.get('{host}/wm/topology/links/json'.format(host=CONTROLLER_HOST))
        links_response_data = links_response.json()

        links = []
        for item in links_response_data:
            node1_id = item['src-switch']
            node1_port = item['src-port']
            node2_id = item['dst-switch']
            node2_port = item['dst-port']

            node1 = self.networkGraph.getNodeById(node1_id)
            node2 = self.networkGraph.getNodeById(node2_id)

            if node1 == None:
                print('Error finding node {0} on network graph'.format(node1_id))
            if node2 == None:
                print('Error finding node {0} on network graph'.format(node2_id))

            link = Link(node1, node2, node1_port, node2_port)
            links.append(link)

        self.networkGraph.setLinks(links)

        self.networkGraph.createCostMatrix()
        self.networkGraph.printCostMatrix()


    def getNetworkSummary(self):
        response = requests.get('{host}/wm/core/controller/summary/json'.format(host=CONTROLLER_HOST))
        response_data = switches_response.json()

        return response_data


    def findPaths(self, flows):
        # Ordena pares de switches de forma decrescente em relação ao volume de
        # tráfego
        flows_copy = list(flows)
        ordered_flows = []
        while len(flows_copy) > 0:
            max_volume_required_item = max(flows_copy, key=attrgetter('bandwidth'))
            ordered_flows.append(max_volume_required_item)
            item_index = flows_copy.index(max_volume_required_item)
            del flows_copy[item_index]

        # ordered_flows contém a lista de pares de switches ordenados por volume
        # de tráfego necessário

        # Calcula caminho de custo mínimo, onde o custo de cada caminho é o recíproco
        # da sua capacidade disponível (1/capacidade). Após associar um par de
        # switches a um caminho, atualiza o custo de cada link.
        for flow in ordered_flows:
            min_cost_path = self.network.getMinimumCostPath(flow)

    def run(self):
        self.initializeNetworkGraph()

        source_switch_id = '00:00:00:00:00:00:00:01'
        target_switch_id = '00:00:00:00:00:00:00:06'

        # Procura caminho de custo mínimo entre dois switches
        min_cost_path = self.networkGraph.getMinimumCostPath(source_switch_id, target_switch_id)
        print('Caminho de custo minimo entre 1 e 6: {0}\n'.format(min_cost_path))



if __name__ == '__main__':
    app = LookAheadRLApp()
    app.run()
