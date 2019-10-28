import csv


def transformSnapshotData(snapshot, snapshot_count):
    """
    Transforma features em números

    timestamp,switch_id,eth_dst,eth_src,eth_type,ipv4_src,ipv4_dst,in_port,packet_count,byte_count,duration_sec,idle_timeout_s,hard_timeout_s,priority,flow_id
    "10/02/2019, 05:15:36",00:00:00:00:00:00:00:05,00:00:00:00:00:01,00:00:00:00:00:02,0x800,10.0.0.2,10.0.0.1,5,2656,149670840,0,5,0,1,00:00:00:00:00:02-00:00:00:00:00:01-0x800-10.0.0.2-10.0.0.1-5
    """
    switch_id_number_index = len(snapshot['switch_id'])-1
    switch_id = int(snapshot['switch_id'][switch_id_number_index])

    eth_dst_number_index = len(snapshot['eth_dst'])-1
    eth_dst = int(snapshot['eth_dst'][eth_dst_number_index])

    eth_src_number_index = len(snapshot['eth_src'])-1
    eth_src = int(snapshot['eth_src'][eth_src_number_index])

    eth_type_number = snapshot['eth_type'][2:]
    eth_type = int(eth_type_number)

    ipv4_src_id_number_index = len(snapshot['ipv4_src'])-1
    ipv4_src = int(snapshot['ipv4_src'][ipv4_src_id_number_index])

    ipv4_dst_id_number_index = len(snapshot['ipv4_dst'])-1
    ipv4_dst = int(snapshot['ipv4_dst'][ipv4_dst_id_number_index])

    new_snapshot_data = [

        switch_id,
        eth_dst,
        eth_src,
        eth_type,
        ipv4_src,
        ipv4_dst,
        int(snapshot['in_port']),
        int(snapshot['packet_count']),
        int(snapshot['byte_count']),
        int(snapshot['duration_sec']),
        int(snapshot['idle_timeout_s']),
        int(snapshot['hard_timeout_s']),
        int(snapshot['priority'])
    ]

    return new_snapshot_data




# 21 fluxos por arquivo
file_list = [
    './h1-as-server/snapshot-h2-client-h1-server--serverless-data.csv',
    './h1-as-server/snapshot-h3-client-h1-server--serverless-data.csv',
    './h1-as-server/snapshot-h4-client-h1-server--serverless-data.csv',
    './h2-as-server/snapshot-h1-client-h2-server--serverless-data.csv',
    './h2-as-server/snapshot-h3-client-h2-server--serverless-data.csv',
    './h2-as-server/snapshot-h4-client-h2-server--serverless-data.csv',
    './h3-as-server/snapshot-h1-client-h3-server--serverless-data.csv',
    './h3-as-server/snapshot-h2-client-h3-server--serverless-data.csv',
    './h3-as-server/snapshot-h4-client-h3-server--serverless-data.csv',
    './h4-as-server/snapshot-h3-client-h4-server--serverless-data.csv',
    './h4-as-server/snapshot-h2-client-h4-server--serverless-data.csv'
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
snapshot_count = 0

"""
Identifica o tamanho total de cada fluxo
"""
index = 0
for snapshot in snapshots:
    try:
        if int(snapshot['duration_sec']) >= max_duration:
            # faz parte do mesmo fluxo atual
            max_duration = int(snapshot['duration_sec'])

            # atualiza tamanho total deste fluxo
            total_byte_count = int(snapshot['byte_count'])

            # transforma todas as features em numeros
            snapshot_transformed = transformSnapshotData(snapshot, snapshot_count)

            # adiciona snapshot como parte das features deste fluxo
            flows[current_flow_id]['features'].append(snapshot_transformed)
        else:
            # termina o fluxo atual e vai preparar para o próximo
            flows[current_flow_id]['total_byte_count'] = total_byte_count

            # limpa todas as variaveis
            max_duration = -1
            total_byte_count = 0

            # inicia novo fluxo
            flow_count = flow_count + 1
            snapshot_count = 0
            current_flow_id = 'fluxo-{flow_count}'.format(flow_count=flow_count)
            flows[current_flow_id] = {}
            flows[current_flow_id]['features'] = []
    except:
        print('skipped index = ', index)
        continue
    index = index + 1


# Pega dados do último fluxo
flows[current_flow_id]['total_byte_count'] = total_byte_count

"""
Printa dados e gera um arquivo pra cada flow
"""
# para checar os valores: flows['fluxo-0']['total_byte_count']/1024/1024/1024 em GByte

for flow_id in flows.keys():
    total_byte_count = flows[flow_id]['total_byte_count']
    size_mb = total_byte_count/1024/1024
    size_gb = total_byte_count/1024/1024/1024

    features = flows[flow_id]['features']
    print('{0} --> {1} Mb // {2} Gb'.format(flow_id, size_mb, size_gb))

    # Gera um arquivo csv pra cada fluxo e suas features
    output_filename = './flow-files-with-int-features/{0}-size-{1}-mb-{2}-gb.csv'.format(flow_id, size_mb, size_gb)
    with open(output_filename, 'w+') as output_file:
        writer = csv.writer(output_file)

        header = ['switch_id', 'eth_dst', 'eth_src', 'eth_type', 'ipv4_src', 'ipv4_dst', 'in_port', 'packet_count', 'byte_count', 'duration_sec', 'idle_timeout_s', 'hard_timeout_s', 'priority']
        writer.writerow(header)

        for snapshot in features:
            writer.writerow(snapshot)
