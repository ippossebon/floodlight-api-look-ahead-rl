import csv

# 21 fluxos por arquivo

file_list = [
    './h4-as-server/snapshot-h3-client-h4-server--serverless-data.csv',
    './h4-as-server/snapshot-h2-client-h4-server--serverless-data.csv'
]

snapshots = []

for filename in file_list:
    with open(filename, 'r+') as csvfile:
        reader = csv.DictReader(csvfile, delimiter=',')

        for row in reader:
            snapshots.append(row)

print('Number of snapshots: ', len(snapshots))
flows = {}

max_byte_count = -1
total_byte_count = 0

flow_count = 0
current_flow_id = 'fluxo-{flow_count}'.format(flow_count=flow_count)
flows[current_flow_id] = {}
flows[current_flow_id]['features'] = []

for snapshot in snapshots:

    # preciso adicionar algum threshold para identificação dos fluxos (300mb ?)
    if int(snapshot['byte_count']) >= max_byte_count + 1024*1024*300:
        # faz parte do mesmo fluxo atual
        max_byte_count = int(snapshot['byte_count'])
        # byte_count vai sendo incrementado por fluxo? ou mostra o total atual? acho que mostra o total atual
        total_byte_count = int(snapshot['byte_count'])
        # total_byte_count = total_byte_count + int(snapshot['byte_count'])

        flows[current_flow_id]['features'].append(snapshot)
    else:
        # termina o fluxo atual e vai preparar para o próximo
        flows[current_flow_id]['total_byte_count'] = total_byte_count

        # limpa todas as variaveis
        max_byte_count = -1
        total_byte_count = 0

        # inicia novo fluxo
        flow_count = flow_count + 1
        current_flow_id = 'fluxo-{flow_count}'.format(flow_count=flow_count)
        flows[current_flow_id] = {}
        flows[current_flow_id]['features'] = []

import ipdb; ipdb.set_trace()
print('isadora')
