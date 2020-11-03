import csv

from os import listdir
from os.path import isfile, join


OUTPUT_IPERFS_DIR_NAME = '../output-experiments-iperfs/'

def writeLineToFile(line, filename):
    with open(filename, 'a') as file:
        file.write("%s\n" % line)


def createConsolidatedFile(agent, num_iperfs):
    flow_sizes = ['10M', '50M', '100M', '200M', '500M']
    output_file_path = OUTPUT_IPERFS_DIR_NAME + '{0}-{1}iperfs-flow_completion_time.csv'.format(agent, num_iperfs)

    for size in flow_sizes:
        filename = OUTPUT_IPERFS_DIR_NAME + '{agent}-{num_iperfs}iperfs-{flow_size}/parsed/{agent}-{num_iperfs}iperfs-{flow_size}-iperfsdata.csv'.format(
            agent=agent, num_iperfs=num_iperfs, flow_size=size)

        with open(filename) as csv_file:
            csv_reader = csv.reader(csv_file, delimiter=',')
            line_count = 0

            for row in csv_reader:
                if line_count > 0:
                    flow_time = row[1]
                    flow_size = row[2]

                    line = '{0}, {1}'.format(flow_time, flow_size)
                    writeLineToFile(line, output_file_path)
                line_count += 1


def main():
    agents = ['A1']
    num_iperfs = ['2', '4']

    for agent in agents:
        for num_iperf in num_iperfs:
            createConsolidatedFile(agent, num_iperf)

if __name__ == '__main__':
    main()
