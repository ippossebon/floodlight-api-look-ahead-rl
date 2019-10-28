import csv
import os

DIR_PATH = './flow-files-with-int-features-without-timestamp/'
OUTPUT_FILE_NAME = './all-flows-input-nn-2.csv'

# desconsidera fluxos com menos de 10gb
black_list_files = [
    '-mb-10.',
    '-mb-9.',
    '-mb-8.',
    '-mb-7.',
    '-mb-6.',
    '-mb-5.',
    '-mb-4.',
    '-mb-3.',
    '-mb-2.',
    '-mb-1.'
]


# considera os primeiros 15 snapshots como features
TIMESTAMPS_TO_CONSIDER = 15

instances = []
original_features = [
    'switch_id',
    'eth_dst',
    'eth_src',
    'eth_type',
    'ipv4_src',
    'ipv4_dst',
    'in_port',
    'packet_count',
    'byte_count',
    'duration_sec',
    'idle_timeout_s',
    'hard_timeout_s',
    'priority'
]

def generateFeaturesNames():
    features_per_timestamp = {}

    for i in range(0, TIMESTAMPS_TO_CONSIDER):
        features_per_timestamp[i] = []

        for feature in original_features:
            new_feature_name = feature + str(i)
            features_per_timestamp[i].append(new_feature_name)

    return features_per_timestamp

features_per_timestamp = generateFeaturesNames()
# print('new_features:')
# print(features_per_timestamp)

fieldnames = []
for row in features_per_timestamp.values():
    for item in row:
        fieldnames.append(item)


with open(OUTPUT_FILE_NAME, 'w+', newline='') as output_file:
    writer = csv.DictWriter(output_file, fieldnames=fieldnames)
    writer.writeheader()

    # Coleta features de todos os fluxos
    for flow_file in os.listdir(DIR_PATH):
        should_countinue = True

        # checa se podemos considerar esse fluxo (deve ser maior que 10gb)
        for item in black_list_files:
            if item in flow_file:
                print('skipped {0} file'.format(flow_file))
                should_countinue = False

        if should_countinue:
            flow_file_path = DIR_PATH + flow_file

            # Abre arquivo de UM fluxo
            with open(flow_file_path, 'r') as input_file:
                flow_instance = {}
                reader = csv.DictReader(input_file, delimiter=',')
                timestamp_count = 0

                for row in reader:
                    if timestamp_count < TIMESTAMPS_TO_CONSIDER:
                        feature_name_index = 0

                        for feature_key in features_per_timestamp[timestamp_count]:
                            original_feature_name = original_features[feature_name_index]
                            flow_instance[feature_key] = row[original_feature_name]
                            feature_name_index = feature_name_index + 1

                    timestamp_count = timestamp_count + 1

                writer.writerow(flow_instance) # corresponde a um fluxo com todas as features dos 20 snapshots


print('Arquivo criado')

# Testando o arquivo criado

# with open(OUTPUT_FILE_NAME, 'r') as csvfile:
#     reader = csv.DictReader(csvfile, delimiter=',')
#
#     for row in reader:
#         for item in row:
#             if print('a')
