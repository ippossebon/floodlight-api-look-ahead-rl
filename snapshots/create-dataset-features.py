import csv

# 21 fluxos por arquivo

file_list = [
    './h4-as-server/snapshot-h3-client-h4-server--serverless-data.csv'
    # './h4-as-server/snapshot-h2-client-h4-server--serverless-data.csv'
]

snapshots = []

for filename in file_list:
    with open(filename, 'r+') as csvfile:
        reader = csv.DictReader(csvfile, delimiter=',')

        for row in reader:
            snapshots.append(row)

flows = {}

max_duration = -1
total_byte_count = 0

flow_count = 0
current_flow_id = 'fluxo-{flow_count}'.format(flow_count=flow_count)
flows[current_flow_id] = {}
flows[current_flow_id]['features'] = []

for snapshot in snapshots:

    # preciso adicionar algum threshold para identificação dos fluxos (300mb ?)
    if int(snapshot['duration_sec']) >= max_duration:
        # faz parte do mesmo fluxo atual
        max_duration = int(snapshot['duration_sec'])

        # byte_count vai sendo incrementado por fluxo? ou mostra o total atual? acho que mostra o total atual
        total_byte_count = int(snapshot['byte_count'])
        # total_byte_count = total_byte_count + int(snapshot['byte_count'])

        flows[current_flow_id]['features'].append(snapshot)
    else:
        # termina o fluxo atual e vai preparar para o próximo
        flows[current_flow_id]['total_byte_count'] = total_byte_count

        # limpa todas as variaveis
        max_duration = -1
        total_byte_count = 0

        # inicia novo fluxo
        flow_count = flow_count + 1
        current_flow_id = 'fluxo-{flow_count}'.format(flow_count=flow_count)
        flows[current_flow_id] = {}
        flows[current_flow_id]['features'] = []

# Pega dados do último fluxo
flows[current_flow_id]['total_byte_count'] = total_byte_count



"""
Printa dados
"""
# import ipdb; ipdb.set_trace()
# para checar os valores: flows['fluxo-0']['total_byte_count']/1024/1024/1024 em GByte

for flow_id in flows.keys():
    total_byte_count = flows[flow_id]['total_byte_count']
    size_mb = total_byte_count/1024/1024
    size_gb = total_byte_count/1024/1024/1024

    print('{0} --> {1} Mb // {2} Gb'.format(flow_id, size_mb, size_gb))
