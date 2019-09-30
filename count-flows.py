import csv

filename = './snapshots/csv/snapshots-json-big-file--client.csv'


instances = []
with open(filename, 'r+') as csvfile:
    readCSV = csv.reader(csvfile, delimiter=';')

    for row in readCSV:
        instances.append(row)


flows = {}
flow_snapshots = []
max_byte_count = -1
total_byte_count = 0
flows_byte_count = {}
instances_count = 0
print('Instances: ', len(instances))

# retira lista do nome das features
del instances[0]

flow_id = instances[0][13] # inicializa id do fluxo
for instance in instances:
    current_flow_id = instance[13]
    byte_count = int(instance[8])

    if byte_count >= max_byte_count:
        # faz parte do mesmo fluxo
        max_byte_count = byte_count
        total_byte_count = total_byte_count + byte_count
        flow_snapshots.append(row)
    else:
        # print(flows)
        # termina o fluxo atual e vai preparar para o próximo
        flows[total_byte_count] = flow_snapshots

        # limpa todas as variaveis
        flow_snapshots = []
        max_byte_count = -1
        total_byte_count = 0

        # inicia novo fluxo
        flow_id = current_flow_id
        flow_snapshots = []

import ipdb; ipdb.set_trace()
print(flows)
