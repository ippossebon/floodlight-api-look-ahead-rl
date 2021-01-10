import csv

from os import listdir
from os.path import isfile, join

"""
Gerar um arquivo final com os dados de iperf no seguinte formato:

MODEL, ORIGINAL_SIZE, TRANSFERRED, RETRIES, TIME, NUM_IPERFS

"""

OUTPUT_APP_DIR_NAME = '../output-experiments-app/'

OUTPUT_FILENAME = './comp-costs-A-B-C-F.csv'

def parseFile(file_path):

    with open(file_path, 'r') as inputfile:
        lines = inputfile.readlines()

        time_string = lines[0]
        time_splitted = time_string.split(':')
        time_hours = float(time_splitted[0])
        time_min = float(time_splitted[1])
        time_interval_min = (time_hours * 60) + time_min

        memory_usage_kb = float(lines[1].strip())


    return time_interval_min, memory_usage_kb


def generateIperfCSVFile(agent, num_iperfs, flow_size):
    dir_path = OUTPUT_IPERFS_DIR_NAME + '{0}-{1}iperfs-{2}/'.format(agent, num_iperfs, flow_size)
    files_in_dir = [f for f in listdir(dir_path) if isfile(join(dir_path, f))]

    for filename in files_in_dir:
        # Formato filename: A1-client-46112-2-flows-50M-v3.log
        if filename != '.DS_Store' and 'compcosts' in filename:
            file_port = None
            file_iter = None

            is_client = 'client' in filename
            file_path = dir_path + filename

            if is_client:
                time_interval_min, memory_usage_kb = parseFile(file_path)
                iter = int(file_iter_string.replace('v', ''))


                line = '{0},{1},{2},{3},{4},{5},{6}'.format(
                    agent,
                    num_iperfs,
                    flow_size,
                    time_interval_min,
                    memory_usage_kb,
                    iter
                )

                print('{0} --- {1}'.format(filename, line))

                writeLineToFile(line, OUTPUT_FILENAME)


def writeLineToFile(line, filename):
    with open(filename, 'a') as file:
        file.write("%s\n" % line)

def main():
    experiments_config_file = './experiments-to-consolidate.csv'

    # agent, num_iperfs, flow_size, time (min), memory (KB), iter
    header = 'agent, num_iperfs, flow_size, time, memory, iter'
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
