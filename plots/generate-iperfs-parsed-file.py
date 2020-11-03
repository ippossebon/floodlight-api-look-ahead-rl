import csv

from os import listdir
from os.path import isfile, join

"""
1. Gerar um arquivo para cada config de experimento no seguinte formato:
    -> A1-2iperfs-10M-iperfsdata.csv
        * port_number, flow_completion_time, mbytes_transfered, bandwidth, retries, iter

2. Organizar arquivos no seguinte formato:
    -> A1-2iperfs-10M
        * A1-2iperfs-10M-iperfsdata.csv
        * A1-2iperfs-10M-app.csv
        * A1-2iperfs-10M-compcosts.csv

3. Gerar gráfico de completion time x size por número de fluxos

4. Gerar gráfico de recompensa x tempo

"""

OUTPUT_IPERFS_DIR_NAME = '../output-experiments-iperfs/'
OUTPUT_APP_DIR_NAME = '../output-experiments-app/'

def parseClient(file_path):
    flow_completion_time = None
    transferred_mbytes = None
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

                # print(splitted_line)

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

def parseServer(file_path):
    flow_completion_time = None
    transferred_mbytes = None
    bandwidth_mbits = None
    retries = None

    with open(file_path, 'r') as inputfile:
        lines = inputfile.readlines()

        for line in lines:
            if 'receiver' in line:
                # linha de interesse onde contém todas as infos
                replaced_line = line.replace('  ', ' ')
                replaced_line = replaced_line.replace('   ', ' ')
                replaced_line = replaced_line.replace('             ', ' ')
                replaced_line = replaced_line.replace('   ', ' ')
                replaced_line = replaced_line.replace('[', '')
                replaced_line = replaced_line.replace(']', '')

                splitted_line_raw = replaced_line.split(' ')
                splitted_line = [item for item in splitted_line_raw if item != '']

                # print(splitted_line)

                # ['4', '0.00-91.00', 'sec', '50.8', 'MBytes', '4.68', 'Mbits/sec', 'receiver\n']
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

                retries = -1

    return flow_completion_time, transferred_mbytes, bandwidth_mbits, retries


def generateIperfCSVFile(agent, num_iperfs, flow_size):
    dir_path = OUTPUT_IPERFS_DIR_NAME + '{0}-{1}iperfs-{2}/'.format(agent, num_iperfs, flow_size)
    files_in_dir = [f for f in listdir(dir_path) if isfile(join(dir_path, f))]

    experiment_output_file = dir_path + 'parsed/' + '{0}-{1}iperfs-{2}-iperfsdata.csv'.format(agent, num_iperfs, flow_size)
    header = 'Port number, Flow completion time (sec), transfered (MBytes), bandwidth (Mbps), Retries, Iter'
    writeLineToFile(header, experiment_output_file)

    for filename in files_in_dir:
        # Formato filename: A1-client-46112-2-flows-50M-v3.log

        file_port = None
        file_iter = None

        is_client = 'client' in filename
        file_path = dir_path + filename
        flow_completion_time, transferred_mbytes, bandwidth_mbits, retries = parseClient(file_path) if is_client else parseServer(file_path)

        filename_splitted = filename.split('-')
        file_port = filename_splitted[2]
        file_iter_string = filename_splitted[len(filename_splitted)-1].replace('.log', '')
        file_iter = int(file_iter_string.replace('v', ''))

        line = '{0}, {1}, {2}, {3}, {4}, {5}'.format(file_port, flow_completion_time, transferred_mbytes, bandwidth_mbits, retries, file_iter)
        writeLineToFile(line, experiment_output_file)


def writeLineToFile(line, filename):
    with open(filename, 'a') as file:
        file.write("%s\n" % line)

def main():
    experiments_config_file = './experiments-to-plot.csv'

    with open(experiments_config_file) as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        line_count = 0

        for row in csv_reader:
            if line_count > 0:
                agent = row[0]
                iperfs = row[1]
                size = row[2]
                timesteps = row[3]
                iter = row[4]
                generateIperfCSVFile(agent, iperfs, size)

                # plotCompletionTime()

                # plotRewardOverTime()

            line_count = line_count + 1

if __name__ == '__main__':
    main()
