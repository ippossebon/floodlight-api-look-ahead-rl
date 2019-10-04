import csv

file_list = [
    './h4-as-server/snapshot-h3-client-h4-server.csv',
    './h4-as-server/snapshot-h2-client-h4-server.csv'
]

instances = []

for filename in file_list:
    with open(filename, 'r+') as csvfile:
        reader = csv.DictReader(csvfile, delimiter=',')

        count = 0
        for row in reader:
            if not count == 0:
                # skip first line (contains features names)
                instances.append(row)
            count = count + 1


print('Number of instances: ', len(instances))


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
