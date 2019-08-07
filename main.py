# -*- coding: utf-8 -*-

from graphModel.flow import Flow
from graphModel.graph import Graph
from graphModel.link import Link
from graphModel.node import Node

from operator import attrgetter

import requests

CONTROLLER_HOST = 'http://0.0.0.0:8080'

class LoohAheadRLApp(object):
    def initializeNetworkGraph(self):
        # 1. Consome topologia floodlight
        response = requests.get('{host}/wm/core/controller/switches/json'.format(host=CONTROLLER_HOST))

        print(response)
        # 2. Monta grafo da rede
        nodes = []
        links = []

        node0 = Node(id='S0', index=0)
        nodes.append(node0)
        node1 = Node(id='S1', index=1)
        nodes.append(node1)
        node2 = Node(id='S2', index=2)
        nodes.append(node2)
        node3 = Node(id='S3', index=3)
        nodes.append(node3)
        node4 = Node(id='S4', index=4)
        nodes.append(node4)
        node5 = Node(id='S5', index=5)
        nodes.append(node5)

        link01 = Link(node0, node1, 500)
        links.append(link01)
        link04 = Link(node0, node4, 500)
        links.append(link04)
        link12 = Link(node1, node2, 500)
        links.append(link12)
        link14 = Link(node1, node4, 500)
        links.append(link14)
        link23 = Link(node2, node3, 500)
        links.append(link23)
        link34 = Link(node3, node4, 500)
        links.append(link34)
        link35 = Link(node3, node5, 500)
        links.append(link35)
        link45 = Link(node4, node5, 500)
        links.append(link45)

        network = Graph(links=links, nodes=nodes)
        network.printCostMatrix()



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



if __name__ == '__main__':
    app = LoohAheadRLApp()
    app.initializeNetworkGraph()
