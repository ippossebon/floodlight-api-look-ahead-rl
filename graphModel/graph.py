# -*- coding: utf-8 -*-

from .link import Link
from .node import Node

NO_LINK = 999999

class Graph(object):
    def __init__(self, links = [], nodes = []):
        self.cost = {}
        self.links = links
        self.nodes = nodes

    def setLinks(self, links):
        self.links = links

    def setNodes(self, nodes):
        self.nodes = nodes

    def getNodeById(self, node_id):
        for node in self.nodes:
            if node.id == node_id:
                return node
        return None

    def containsLink(self, node_id_1, node_id_2):
        for link in self.links:
            if (link.node1.id == node_id_1 and link.node2.id == node_id_2) or (link.node1.id == node_id_2 and link.node2.id == node_id_1):
                return True
        return False

    def containsNodeId(self, node_id):
        for node in self.nodes:
            if node.id == node_id:
                return True
        return False

    def createCostMatrix(self):
        if len(self.links) == 0: return

        for link in self.links:
            # Inicializa dicionario de distancias pra cada node
            nodes_id = [link.node1.id, link.node2.id]
            for node_id in nodes_id:
                if node_id not in self.cost.keys():
                    self.cost[node_id] = {}
                    self.cost[node_id][node_id] = NO_LINK

            # Seta custo bidirecional
            self.cost[link.node1.id][link.node2.id] = 1 / link.weight
            self.cost[link.node2.id][link.node1.id] = 1 / link.weight


    def updatePathCostMatrix(self, path, consumed_bandwidth):
        # Atualiza as larguras de banda disponiveis de cada link
        for i in range(len(path) - 1):
            item_index_source = path[i]
            item_index_target = path[i+1]
            self.cost[item_index_source][item_index_target] = self.cost[item_index_source][item_index_target] - (1 / consumed_bandwidth)

        new_distances = self.createDistancesDict()


    def getMinimumCostPath(self, source_switch_id, target_switch_id):
        # Calcula caminho de custo mínimo, onde o custo de cada caminho é o recíproco
        # da sua capacidade disponível (1/capacidade). Após associar um par de
        # switches a um caminho, atualiza o custo de cada link.
        print('-> Get mininum cost path [Dijkstra] from switch {0} to switch {1}'.format(
            source_switch_id, target_switch_id))

        min_cost_path = self.dijsktra(source_switch_id, target_switch_id)

        return min_cost_path

    def dijsktra(self, source_switch_id, target_switch_id):
        # shortest paths is a dict of nodes whose value is a tuple of (previous node, weight)
        shortest_paths = {source_switch_id: (None, 0)}
        current_node = source_switch_id
        distances = dict(self.cost)
        visited = set()

        while current_node != target_switch_id:
            visited.add(current_node)
            destinations = distances[current_node]
            weight_to_current_node = shortest_paths[current_node][1]

            for next_node in destinations:
                weight = self.cost[current_node][next_node] + weight_to_current_node
                if next_node not in shortest_paths:
                    shortest_paths[next_node] = (current_node, weight)
                else:
                    current_shortest_weight = shortest_paths[next_node][1]
                    if current_shortest_weight > weight:
                        shortest_paths[next_node] = (current_node, weight)

            next_destinations = {node: shortest_paths[node] for node in shortest_paths if node not in visited}

            if len(next_destinations.values()) == 0:
                return "Route Not Possible"
            # next node is the destination with the lowest weight
            current_node = min(next_destinations, key=lambda k: next_destinations[k][1])

        # Work back through destinations in shortest path
        path = []
        while current_node is not None:
            path.append(current_node)
            next_node = shortest_paths[current_node][0]
            current_node = next_node
        # Reverse path
        path = path[::-1]
        return path

    def printCostMatrix(self):
        print('-> Cost matrix:')
        for item in self.cost:
            print('{0} => {1}'.format(item, self.cost[item]))
        print('\n')

    def printGraph(self):
        for link in self.links:
            print('{node1}-------({weight})-------{node2}'.format(
                node1=link.node1.id,
                weight=link.weight,
                node2=link.node2.id
            ))
