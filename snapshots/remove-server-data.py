import csv


filename = './h1-as-server/original-data/snapshot-h2-client-h1-server.csv'
output_filename = './h1-as-server/isadora.csv'

instances = []

SOURCE_ETH = '00:00:00:00:00:01'
TARGET_ETH = '00:00:00:00:00:02'


with open(filename, 'r+') as original_file:
    original_file_reader = csv.DictReader(original_file, delimiter=',')

    with open(output_filename, 'w+') as output_file:
        fieldnames = ['timestamp','switch_id','eth_dst','eth_src','eth_type','ipv4_src','ipv4_dst','in_port','packet_count','byte_count','duration_sec','idle_timeout_s','hard_timeout_s','priority','flow_id']
        writer = csv.DictWriter(output_file, fieldnames=fieldnames)
        writer.writeheader()

        for row in original_file_reader:
            server_data = row['eth_src'] == SOURCE_ETH and row['eth_dst'] == TARGET_ETH
            if not server_data:
                import ipdb; ipdb.set_trace()

                writer.writerow({
                    'timestamp': row['timestamp'],
                    'switch_id': row['switch_id'],
                    'eth_dst': row['eth_dst'],
                    'eth_src': row['eth_src'],
                    'eth_type': row['eth_type'],
                    'ipv4_src': row['ipv4_src'],
                    'ipv4_dst': row['ipv4_dst'],
                    'in_port': row['in_port'],
                    'packet_count': row['packet_count'],
                    'byte_count': row['byte_count'],
                    'duration_sec': row['duration_sec'],
                    'idle_timeout_s': row['idle_timeout_s'],
                    'hard_timeout_s': row['hard_timeout_s'],
                    'priority': row['priority'],
                    'flow_id': row['flow_id']
                })
