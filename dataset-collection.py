from graphModel.activeFlow import ActiveFlow
from graphModel.flow import Flow
from graphModel.graph import Graph
from graphModel.link import Link
from graphModel.node import Node

from prediction.flowSizePredictor import FlowSizePredictor

from routing.binPacking import BinPackingRouting

from operator import attrgetter

import csv
import requests
import time

CONTROLLER_HOST = 'http://0.0.0.0:8080'
THRESHOLD = 10 # IDEAFIX uses 10MB or 10 seg


class LookAheadRLApp(object):
    def __init__(self):
        self.network_graph = Graph()
        self.routing_model = BinPackingRouting()
        self.switch_info = {} # dicionário cuja chave é o MAC do switch. Ex: current_flows["00:00:00:00:00:00:00:01"]
        self.active_flows = [] # lista de ActiveFlow

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


    def getFlow(self, flow_id):
        for item in self.active_flows:
            if flow_id == item.id:
                return item
        return None

    def collectSnapshots(self):
        snapshot_count = 0
        snapshots = []

        timeout_minutes = 3
        timeout = time.time() + 60*timeout_minutes   # 3 minutes from now
        while True:
            # List of all devices tracked by the controller. This includes MACs, IPs, and attachment points.
            response = requests.get('{host}/wm/core/switch/all/flow/json'.format(host=CONTROLLER_HOST))
            response_data = response.json()

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
                        snapshot = [
                            snapshot_count,
                            flow_id,
                            flow["hard_timeout_s"],
                            flow["byte_count"],
                            flow["idle_timeout_s"],
                            flow["packet_count"],
                            flow["duration_sec"]
                        ]
                        snapshots.append(snapshot)
            snapshot_count = snapshot_count + 1

            # Coleta snapshots por N minutos
            test = 0
            if test == timeout_minutes or time.time() > timeout:
                break
            test = test - 1

            time.sleep(5)


        # Escreve no arquivo de snapshots
        with open('snapshots1.csv', 'w+', newline='') as csvfile:
            print('vai escrever o arquivo')
            spamwriter = csv.writer(csvfile, delimiter=',')
            for item in snapshots:
                print('.', end = '')
                spamwriter.writerow(item)


    def listNetworkDevices(self):
        # List static flows for a switch or all switches
        response = requests.get('{host}/wm/device'.format(host=CONTROLLER_HOST))
        response_data = response.json()

        return response

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

    def shouldReroute(self, predicted_size):
        if predicted_size > THRESHOLD:
            return True
        return False

    def run(self):
        # Create network graph
        self.initializeNetworkGraph()
        self.routing_model.setNetworkGraph(self.network_graph)

        self.setSwitchStatistics()
        self.collectSnapshots()
        # Train prediction model
        # self.predictor.trainModel()


        # Fluxos correntes e snapshot de suas features adicionados as listas a cada 5 segundos
            # Estatítiscas estão aramazenados em self.switch_info


            # Usar estatísticas do fluxo para prever o tamanho total dele
            # for flow in self.active_flows:
            #     info_line = list(flow.features)
            #     # Features contem todos os snapshots ja coletados... Precisamos pegar apenas um snapshot
            #
            #     info_line.insert(0, flow.id)
            #     info_line.insert(1, snapshot_count)
            #
            #     print(info_line)
            #     # predicted_size = self.predictor.predictFlowSize(flow.features)
            #
            #     # if self.shouldReroute(predicted_size):
            #     #     source_switch_id = '00:00:00:00:00:00:00:01' # get from flow info
            #     #     target_switch_id = '00:00:00:00:00:00:00:06' # get from flow info
            #     #     new_route = self.network_graph.getMinimumCostPath(source_switch_id, target_switch_id)
            # snapshot_count = snapshot_count + 1
            # time.sleep(10)
            # print('---------------------------------------------')





if __name__ == '__main__':
    app = LookAheadRLApp()
    app.run()
