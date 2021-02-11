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


def generateIperfCSVFile(agent, num_iperfs, flow_size):
    dir_path = OUTPUT_IPERFS_DIR_NAME + '{0}-{1}iperfs-{2}/'.format(agent, num_iperfs, flow_size)
    files_in_dir = [f for f in listdir(dir_path) if isfile(join(dir_path, f))]

    for filename in files_in_dir:
        # Formato filename: A1-client-46112-2-flows-50M-v3.log
        if filename != '.DS_Store':
            file_port = None
            file_iter = None

            is_client = 'client' in filename
            file_path = dir_path + filename

            if is_client:
                flow_completion_time, transferred_mbytes, bandwidth_mbits, retries = parseClient(file_path)

                filename_splitted = filename.split('-')
                port = filename_splitted[2]
                num_iperfs = filename_splitted[3]
                original_size = filename_splitted[5]
                file_iter_string = filename_splitted[len(filename_splitted)-1].replace('.log', '')
                num_iters = int(file_iter_string.replace('v', ''))

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


    with open(experiments_config_file) as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        line_count = 0

        for row in csv_reader:
            if line_count > 0:
                agent = row[0]
                iperfs = row[1]
                size = row[2]
                iter = row[3]
                generateIperfCSVFile(agent, iperfs, size)

            line_count = line_count + 1

if __name__ == '__main__':
    main()
