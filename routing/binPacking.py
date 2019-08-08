# -*- coding: utf-8 -*-

from graphModel.flow import Flow
from graphModel.graph import Graph
from graphModel.link import Link
from graphModel.node import Node

from operator import attrgetter

class BinPackingRouting(object):
    def __init__(self, graphNetwork = None):
        self.graphNetwork = graphNetwork

    def setGraphNetwork(self, graphNetwork):
        self.graphNetwork = graphNetwork

    def findPaths(self, flows_running_on_network):
        # Ordena pares de switches de forma decrescente em relação ao volume de
        # tráfego
        flows_copy = list(flows_running_on_network)
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
        path_per_flow = {}
        for flow in ordered_flows:
            min_cost_path = self.graphNetwork.getMinimumCostPath(
                source_switch_id = flow.source.id,
                target_switch_id = flow.target.id
            )
            path_per_flow[flow.id] = min_cost_path

        return path_per_flow

if __name__ == '__main__':
    nodes = []
    links = []

    routingModel = BinPackingRouting(graphNetwork)

    flow05 = Flow(node0, node5, 200)
    flow13 = Flow(node1, node3, 50)
    flow25 = Flow(node2, node5, 100)

    # custo = 1 / capacidade_atual
    min_cost_path = graphNetwork.getMinimumCostPath(flow25)
    min_cost_path = graphNetwork.getMinimumCostPath(flow13)

    # flows = []
    # flows.append(flow05)
    # flows.append(flow13)
    # flows.append(flow25)
    #
    # paths = routingModel.findPaths(flows)
