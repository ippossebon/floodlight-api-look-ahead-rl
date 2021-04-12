import csv

from os import listdir
from os.path import isfile, join

"""
Gerar um arquivo final com os dados de iperf no seguinte formato:

MODEL, ORIGINAL_SIZE, TRANSFERRED, RETRIES, TIME, NUM_IPERFS

"""

OUTPUT_APP_DIR_NAME = '../output-experiments-app/'

OUTPUT_FILENAME = './data/temp-costs.csv'

def parseFile(file_path):

    with open(file_path, 'r') as inputfile:
        lines = inputfile.readlines()

        time_string = lines[0]
        time_splitted = time_string.split(':')
        time_hours = float(time_splitted[0])
        time_min = float(time_splitted[1])
        time_sec_str = time_splitted[2].strip()
        time_sec = float(time_sec_str)

        time_interval_min = (time_hours * 60) + time_min
        time_interval_sec = (time_interval_min * 60) + time_sec

        memory_usage_kb = float(lines[1].strip())

    return time_interval_sec, memory_usage_kb


def generateIperfCSVFile(agent, interval, workload):
    dir_name = '{0}-{1}-{2}/'.format(agent, interval, workload)
    dir_path = OUTPUT_APP_DIR_NAME + dir_name
    files_in_dir = [f for f in listdir(dir_path) if isfile(join(dir_path, f))]

    # import pdb; pdb.set_trace()
    for filename in files_in_dir:
        # Formato filename: A1-client-46112-2-flows-50M-v3.log
        if filename != '.DS_Store' and 'compcosts.txt' in filename:
            file_port = None
            file_iter = None

            file_path = dir_path + filename
            filename_splitted = filename.split('-')

            # filename_splitted
            # ['het', 'B_HET_LA', '8_flows', 'ALL_FLOWS', '600steps', '5_sec', 'prop_0', 'v_0', 'compcosts.txt']
            # ['B', 'HET', 'LA', '8_flows', 'ALL_FLOWS', '700steps', '10_sec', 'prop_1', 'v_0', 'compcosts.txt']
            num_iperfs_str = filename_splitted[2]
            num_iperfs = int(num_iperfs_str.split('_')[0])

            file_iter_string = filename_splitted[7]
            iter = int(file_iter_string.split('_')[1])

            time_interval_sec, memory_usage_kb = parseFile(file_path)

            line = '{0},{1},{2},{3},{4},{5},{6}'.format(
                agent,
                num_iperfs,
                interval,
                workload,
                time_interval_sec,
                memory_usage_kb,
                iter
            )

            print('{0} --- {1}'.format(filename, line))

            writeLineToFile(line, OUTPUT_FILENAME)


def writeLineToFile(line, filename):
    with open(filename, 'a') as file:
        file.write("%s\n" % line)

def main():
    experiments_config_file = './experiments-to-consolidate-LA.csv'

    header = 'agent, num_iperfs, interval, workload, time, memory, iter'
    writeLineToFile(header, OUTPUT_FILENAME)

    with open(experiments_config_file) as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        line_count = 0

        for row in csv_reader:
            if line_count > 0:
                agent = row[0]
                interval = row[1]
                workload = row[2]
                generateIperfCSVFile(agent, interval, workload)

            line_count = line_count + 1

if __name__ == '__main__':
    main()
