import csv

from os import listdir
from os.path import isfile, join

"""
Gerar um arquivo final com os dados de iperf no seguinte formato:

MODEL, ORIGINAL_SIZE, TRANSFERRED, RETRIES, TIME, NUM_IPERFS

"""

OUTPUT_IPERFS_DIR_NAME = '../output-experiments-iperfs-raw/'

OUTPUT_FILENAME = './temp-iperfs.csv'

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
                if transferred_unity == 'MBytes':
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

def getOriginalSize(filename):
    # "25M" "50M" "80M" "100M" "200M" "400M" "800M" "1600M"
    size_map = ['25M', '50M', '80M', '100M', '200M', '400M', '800M', '1600M']

    if '-1' in filename:
        return size_map[0]
    elif '-2' in filename:
        return size_map[1]
    elif '-3' in filename:
        return size_map[2]
    elif '-4' in filename:
        return size_map[3]
    elif '-5' in filename:
        return size_map[4]
    elif '-6' in filename:
        return size_map[5]
    elif '-7' in filename:
        return size_map[6]
    elif '-8' in filename:
        return size_map[7]

def getPort(filename):
    port_map = ['46110', '46112', '46114', '46116', '46118', '46120', '46122', '46124']

    if '-1' in filename:
        return port_map[0]
    elif '-2' in filename:
        return port_map[1]
    elif '-3' in filename:
        return port_map[2]
    elif '-4' in filename:
        return port_map[3]
    elif '-5' in filename:
        return port_map[4]
    elif '-6' in filename:
        return port_map[5]
    elif '-7' in filename:
        return port_map[6]
    elif '-8' in filename:
        return port_map[7]

def getNumIter(filename):
    if '_0' in filename:
        return 0
    elif '_1' in filename:
        return 1
    elif '_2' in filename:
        return 2
    elif '_3' in filename:
        return 3
    elif '_4' in filename:
        return 4




def generateIperfCSVFile(agent):
    dir_path = '{0}/'.format(agent)
    files_in_dir = [f for f in listdir(dir_path) if isfile(join(dir_path, f))]
    num_iperfs = 8

    for filename in files_in_dir:
        # Formato filename: A1-client-46112-2-flows-50M-v3.log
        if filename != '.DS_Store':
            file_port = None
            file_iter = None

            is_client = 'client' in filename
            file_path = dir_path + filename

            if is_client:
                flow_completion_time, transferred_mbytes, bandwidth_mbits, retries = parseClient(file_path)

                original_size = getOriginalSize(filename)
                port = getPort(filename)
                num_iters = getNumIter(filename)

                line = '{0},{1},{2},{3},{4},{5},{6},{7},{8}'.format(
                    agent,
                    num_iperfs,
                    port,
                    original_size,
                    transferred_mbytes,
                    retries,
                    flow_completion_time,
                    bandwidth_mbits,
                    num_iters
                )

                print('{0} --- {1}'.format(filename, line))

                writeLineToFile(line, OUTPUT_FILENAME)


def writeLineToFile(line, filename):
    with open(filename, 'a') as file:
        file.write("%s\n" % line)

def main():
    experiments_config_file = './experiments-to-consolidate.csv'

    # agent, num_iperfs, port_number, original_size (MB), transferred (MB), retries, flow_completion_time (sec), bandwidth (Mbps), iter
    header = 'agent, num_iperfs, port_number, original_size, transferred, retries, flow_completion_time, bandwidth, iter'
    writeLineToFile(header, OUTPUT_FILENAME)

    for agent in ['B-HET', 'B-LA-HET']:
        generateIperfCSVFile(agent)


if __name__ == '__main__':
    main()
