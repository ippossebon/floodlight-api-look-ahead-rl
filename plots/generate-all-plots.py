import csv

from os import listdir
from os.path import isfile, join

"""
1. Gerar um arquivo para cada config de experimento no seguinte formato:
    -> A1-2iperfs-10M-iperfs
        * port_number, flow_completion_time, mbytes_transfered, bandwidth, retries, iter

2. Organizar arquivos no seguinte formato:
    -> A1-2iperfs-10M
        * A1-2iperfs-10M-iperfs
        * A1-2iperfs-10M-app
        * A1-2iperfs-10M-compcosts

3. Gerar gráfico de completion time x size por número de fluxos

4. Gerar gráfico de recompensa x tempo

"""

OUTPUT_IPERFS_DIR_NAME = '../output-experiments-iperfs/'
OUTPUT_APP_DIR_NAME = '../output-experiments-app/'



def generateIperfCSVFile(agent, iperfs, size):
    dir_path = OUTPUT_IPERFS_DIR_NAME + '{0}-{1}iperfs-{2}'.format(agent, iperfs,size)
    files_in_dir = [f for f in listdir(dir_path) if isfile(join(dir_path, f))]

    print('dir_path', dir_path)

    print('files_in_dir', files_in_dir)
    for filename in files_in_dir:
        # arquivo com nome no formato output-experiments-iperfs/A1-client-46110-4-flows-100M-v0.log
        # pegar o nome do arquivo, para extrair infos
        file_agent = None
        file_port = None
        file_iperfs = None
        file_flow_size = None
        file_iter = None
        print(filename)




def plotCompletionTime():
    pass

def plotRewardOverTime():
    pass

def main():
    experiments_config_file = './experiments-configs.csv'

    with open(experiments_config_file) as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        line_count = 0

        for row in csv_reader:
            print(row)
            if line_count > 1:
                agent = row[0]
                iperfs = row[1]
                size = row[2]
                timesteps = row[3]
                iter = row[4]

                generateIperfCSVFile(agent, iperfs, size)
                exit(0)

                # plotCompletionTime()

                # plotRewardOverTime()

            line_count += 1

if __name__ == '__main__':
    main()
