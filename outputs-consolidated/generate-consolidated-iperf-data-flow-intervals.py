import csv

from os import listdir
from os.path import isfile, join

"""
Gerar um arquivo final com os dados de iperf no seguinte formato:

MODEL, ORIGINAL_SIZE, TRANSFERRED, RETRIES, TIME, NUM_IPERFS

"""

OUTPUT_IPERFS_DIR_NAME = '../output-experiments-iperfs-raw/'

OUTPUT_FILENAME = './data/temp-iperfs.csv'

def parseClient(file_path):
    flow_completion_time = None
    transferred_mbytes = None
    received_mbytes = None
    bandwidth_mbits = None
    retries = None

    with open(file_path, 'r') as inputfile:
        lines = inputfile.readlines()

        for line in lines:
            if 'sender' in line:
                # linha de interesse onde contém todas as infos
                replaced_line = line.replace('  ', ' ')
                replaced_line = replaced_line.replace('   ', ' ')
                replaced_line = replaced_line.replace('             ', ' ')
                replaced_line = replaced_line.replace('   ', ' ')
                replaced_line = replaced_line.replace('[', '')
                replaced_line = replaced_line.replace(']', '')

                splitted_line_raw = replaced_line.split(' ')
                splitted_line = [item for item in splitted_line_raw if item != '']

                # ['4', '0.00-173.00', 'sec', '100', 'MBytes', '4.85', 'Mbits/sec', '6177', 'sender\n']
                time_interval = splitted_line[1]
                splitted_time = time_interval.split('-')
                flow_completion_time = float(splitted_time[1])

                transferred_count = float(splitted_line[3])
                transferred_unity = splitted_line[4]
                transferred_mbytes = None

                if transferred_unity == 'GBytes':
                    transferred_mbytes = transferred_count * 1024
                elif transferred_unity == 'MBytes':
                    transferred_mbytes = transferred_count
                elif transferred_unity == 'KBytes':
                    transferred_mbytes = transferred_count/1024

                bandwidth_count = float(splitted_line[5])
                bandwidth_unity = splitted_line[6]
                bandwidth_mbits = None

                if bandwidth_unity == 'Mbits/sec':
                    bandwidth_mbits = bandwidth_count
                elif bandwidth_unity == 'Kbits/sec':
                    bandwidth_mbits = bandwidth_count/1024
                elif bandwidth_unity == 'bits/sec':
                    bandwidth_mbits = bandwidth_count/(1024 * 1024)

                retries = float(splitted_line[7])

    return flow_completion_time, transferred_mbytes, bandwidth_mbits, retries


def generateIperfCSVFile(agent, interval, workload, num_iperfs):
    dir_name = '{0}-{1}-{2}/'.format(agent, interval, workload)
    dir_path = OUTPUT_IPERFS_DIR_NAME + dir_name
    files_in_dir = [f for f in listdir(dir_path) if isfile(join(dir_path, f))]

    for filename in files_in_dir:
        # Formato filename: B-HET-LA-client-46110-50M-5-proportion_2-v0
        if filename != '.DS_Store':
            file_port = None
            file_iter = None

            is_client = 'client' in filename
            file_path = dir_path + filename

            if is_client:
                flow_completion_time, transferred_mbytes, bandwidth_mbits, retries = parseClient(file_path)

                filename_splitted = filename.split('-')
                port = filename_splitted[4]
                original_size = filename_splitted[5]
                file_iter_string = filename_splitted[len(filename_splitted)-1].replace('.log', '')
                num_iter = int(file_iter_string.replace('v', ''))
                interval_splitted = interval.split('_')
                interval_sec = interval_splitted[0]

                line = '{agent},{num_iperfs},{port},{original_size},{transferred_mbytes},{retries},{flow_completion_time},{bandwidth_mbits},{interval_sec},{workload},{num_iter}'.format(
                    agent=agent,
                    num_iperfs=num_iperfs,
                    port=port,
                    original_size=original_size,
                    transferred_mbytes=transferred_mbytes,
                    retries=retries,
                    flow_completion_time=flow_completion_time,
                    bandwidth_mbits=bandwidth_mbits,
                    interval_sec=interval_sec,
                    workload=workload,
                    num_iter=num_iter
                )

                print('{0} --- {1}'.format(filename, line))

                writeLineToFile(line, OUTPUT_FILENAME)


def writeLineToFile(line, filename):
    with open(filename, 'a') as file:
        file.write("%s\n" % line)

def main():
    experiments_config_file = './experiments-to-consolidate-LA.csv'
    # Possible workloads:
    # 25_75 = 25/75 (MF/EF)
    # 50_50 = 50/50 (MF/EF)
    # 75_25 = 75/25 (MF/EF)

    num_iperfs = 8
    # agent, num_iperfs, port_number, original_size (MB), transferred (MB), retries, flow_completion_time (sec), bandwidth (Mbps), interval (sec), workload, iter
    header = 'agent, num_iperfs, port_number, original_size, transferred, retries, flow_completion_time, bandwidth, interval, workload, iter'
    writeLineToFile(header, OUTPUT_FILENAME)

    with open(experiments_config_file) as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        line_count = 0

        for row in csv_reader:
            if line_count > 0:
                agent = row[0]
                interval = row[1]
                workload = row[2]
                generateIperfCSVFile(agent, interval, workload, num_iperfs)

            line_count = line_count + 1

if __name__ == '__main__':
    main()
