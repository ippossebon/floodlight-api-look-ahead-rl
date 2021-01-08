import csv

OUTPUT_FILENAME = './data/app-consolidated-avg-error-A1-and-F.csv'

def writeLineToFile(line, filename):
    with open(filename, 'a') as file:
        file.write("%s\n" % line)


"""
Gera um arquivo no formato
timestep, avg_reward, std_dev, agent, flow_size, num_iperfs
"""

def createConsolidatedFile():
    filename = './data/iperf-consolidated-A1-and-F.csv'

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



if __name__ == '__main__':
    createConsolidatedFile()
