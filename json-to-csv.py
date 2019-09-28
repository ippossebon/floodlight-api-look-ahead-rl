import csv
import datetime
import json

with open('./snapshots-json-20gb-formatted.txt', 'r') as jsonfile:
    data = json.load(jsonfile)

csv_lines = []
timeslot = 0

for timestamp in data.keys():
    for switch_id in data[timestamp]:
        for flow_item in data[timestamp][switch_id]['flows']:
            if flow_item['match'].keys():
                # desconsidera pacotes ARP
                if not flow_item['match']['eth_type'] == '0x806':
                    # se o flow_item em questão possui um match associado,
                    # significa que ele representa um fluxo corrente
                    flow_id = '{eth_src}-{eth_dst}-{eth_type}-{ipv4_src}-{ipv4_dst}-{in_port}'.format(
                        eth_dst=flow_item['match']['eth_dst'],
                        eth_src=flow_item['match']['eth_src'],
                        eth_type=flow_item['match']['eth_type'],
                        ipv4_src=flow_item['match']['ipv4_src'],
                        ipv4_dst=flow_item['match']['ipv4_dst'],
                        in_port=flow_item['match']['in_port']
                    )
                    instance = [
                        timeslot,
                        flow_item['match']['eth_dst'],
                        flow_item['match']['eth_src'],
                        flow_item['match']['eth_type'],
                        flow_item['match']['ipv4_src'],
                        flow_item['match']['ipv4_dst'],
                        flow_item['match']['in_port'],
                        flow_item['packet_count'],
                        flow_item['byte_count'],
                        flow_item['duration_sec'],
                        flow_item['idle_timeout_s'],
                        flow_item['hard_timeout_s'],
                        flow_item['priority'],
                        flow_id
                    ]
                    csv_lines.append(instance)
                    print(instance)
    timeslot = timeslot + 1



# Cria arquivo CSV de saida
# timestamp = datetime.datetime.now().strftime("%m/%d/%Y, %H:%M:%S")
filename = './snapshots/csv/ssnapshots-json-20gb.csv'
with open(filename, 'w+') as csvfile:
    spamwriter = csv.writer(csvfile, delimiter=';')
    spamwriter.writerow(['timeslot', 'eth_dst', 'eth_src', 'eth_type', 'ipv4_src', 'ipv4_dst', 'in_port', 'packet_count', 'byte_count', 'duration_sec', 'idle_timeout_s', 'hard_timeout_s', 'priority', 'flow_id'])

    for item in csv_lines:
        print('.', end = '')
        spamwriter.writerow(item)