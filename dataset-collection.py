from graphModel.activeFlow import ActiveFlow
from graphModel.flow import Flow
from graphModel.graph import Graph
from graphModel.link import Link
from graphModel.node import Node

from routing.binPacking import BinPackingRouting

from operator import attrgetter

import csv
import datetime
import json
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
        snapshots = {}
        minutes = 6 * 60
        timeout = time.time() + minutes # 5 minutes from now
        test = 0

        link_A_usage_rate = -1
        link_B_usage_rate = -1
        link_C_usage_rate = -1
        link_D_usage_rate = -1
        link_E_usage_rate = -1
        link_F_usage_rate = -1

        dataframe = []
        snapshot_count = 0
        try:
            while True:
                # List of all devices tracked by the controller. This includes MACs, IPs, and attachment points.
                # /wm/core/switch/<switchId>/<statType>/json
                response = requests.get('{host}/wm/statistics/bandwidth/all/all/json'.format(host=CONTROLLER_HOST))
                response_data = response.json()

                for item in response_data:
                    print(item)
                    if item["dpid"] == "00:00:00:00:00:00:00:01":
                        if item["port"] == "1":
                            # link A
                            link_A_usage = float(item["bits-per-second-rx"])
                            link_A_capacity = float(item["link-speed-bits-per-second"])
                            link_A_usage_rate = float(link_A_usage / link_A_capacity)

                    elif item["dpid"] == "00:00:00:00:00:00:00:02":
                        if item["port"] == "1":
                            # link B
                            link_B_usage = float(item["bits-per-second-rx"])
                            link_B_capacity = float(item["link-speed-bits-per-second"])
                            link_B_usage_rate = float(link_B_usage / link_B_capacity)

                        elif item["port"] == "2":
                            # link E
                            link_E_usage = float(item["bits-per-second-rx"])
                            link_E_capacity = float(item["link-speed-bits-per-second"])
                            link_E_usage_rate = float(link_E_usage / link_E_capacity)

                        elif item["port"] == "3":
                            # link E
                            link_D_usage = float(item["bits-per-second-rx"])
                            link_D_capacity = float(item["link-speed-bits-per-second"])
                            link_D_usage_rate = float(link_D_usage / link_D_capacity)

                    elif item["dpid"] == "00:00:00:00:00:00:00:03":
                        if item["port"] == "1":
                            # link C
                            link_C_usage = float(item["bits-per-second-rx"])
                            link_C_capacity = float(item["link-speed-bits-per-second"])
                            link_C_usage_rate = float(link_C_usage / link_C_capacity)

                        elif item["port"] == "3":
                            # link F
                            link_F_usage = float(item["bits-per-second-rx"])
                            link_F_capacity = float(item["link-speed-bits-per-second"])
                            link_F_usage_rate = float(link_F_usage / link_F_capacity)

                snapshot = [
                    snapshot_count,
                    link_A_usage_rate,
                    link_B_usage_rate,
                    link_C_usage_rate,
                    link_D_usage_rate,
                    link_E_usage_rate,
                    link_F_usage_rate
                ]

                dataframe.append(snapshot)

                time.sleep(1)
                snapshot_count = snapshot_count + 1

                # Roda script por um tempo fixo
                # if test == minutes or time.time() > timeout:
                #     snapshots_json = json.dumps(snapshots)
                #     with open('./snapshot-h2-client-h4-server.txt', 'w+') as json_file:
                #         json.dump(snapshots_json, json_file)
                #     break
                # test = test - 1

        except KeyboardInterrupt:
            with open('./dados-rede.csv', 'w+', newline='') as csv_file:
                wr = csv.writer(csv_file)
                header = [
                    'snapshot',
                    'link_A_usage_rate',
                    'link_B_usage_rate',
                    'link_C_usage_rate',
                    'link_D_usage_rate',
                    'link_E_usage_rate',
                    'link_F_usage_rate'
                ]
                wr.writerow(header)

                for row in dataframe:
                    wr.writerow(row)

                print('Criou arquivo')


    def shouldReroute(self, predicted_size):
        if predicted_size > THRESHOLD:
            return True
        return False

    def enableStatisticsCollection(self):
        # curl -X POST -d "" http://0.0.0.0:8080/wm/statistics/config/enable/json
        response = requests.post('{host}/wm/statistics/config/enable/json'.format(host=CONTROLLER_HOST), data='')

    def run(self):
        # Create network graph
        self.initializeNetworkGraph()
        self.routing_model.setNetworkGraph(self.network_graph)

        self.enableStatisticsCollection()
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
