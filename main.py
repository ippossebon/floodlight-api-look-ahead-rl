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

        for switch in switches:
            switch.printInfo()
        # [
        # {u'inetAddress': u'/127.0.0.1:38951', u'connectedSince': 1565172781116, u'switchDPID': u'00:00:00:00:00:00:00:02'},
        # {u'inetAddress': u'/127.0.0.1:38947', u'connectedSince': 1565172781462, u'switchDPID': u'00:00:00:00:00:00:00:06'},
        # {u'inetAddress': u'/127.0.0.1:38949', u'connectedSince': 1565172781349, u'switchDPID': u'00:00:00:00:00:00:00:03'},
        # {u'inetAddress': u'/127.0.0.1:38948', u'connectedSince': 1565172781444, u'switchDPID': u'00:00:00:00:00:00:00:04'},
        # {u'inetAddress': u'/127.0.0.1:38950', u'connectedSince': 1565172781344, u'switchDPID': u'00:00:00:00:00:00:00:05'},
        # {u'inetAddress': u'/127.0.0.1:38946', u'connectedSince': 1565172781109, u'switchDPID': u'00:00:00:00:00:00:00:01'}]

        # 2. Monta grafo da rede
        #
        #
        # link01 = Link(node0, node1, 500)
        # links.append(link01)
        # link04 = Link(node0, node4, 500)
        # links.append(link04)
        # link12 = Link(node1, node2, 500)
        # links.append(link12)
        # link14 = Link(node1, node4, 500)
        # links.append(link14)
        # link23 = Link(node2, node3, 500)
        # links.append(link23)
        # link34 = Link(node3, node4, 500)
        # links.append(link34)
        # link35 = Link(node3, node5, 500)
        # links.append(link35)
        # link45 = Link(node4, node5, 500)
        # links.append(link45)
        #
        # network = Graph(links=links, nodes=nodes)
        # network.printCostMatrix()



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
