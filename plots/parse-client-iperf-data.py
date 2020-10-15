import csv

txt_filename = './data/client-iperf-data.txt'
csv_filename = './data/client-iperf-data.csv'

count = 0

def parseLine(line):
    splitted_text = line.split('  ')

    timestep_string = splitted_text[1]
    timestep = float(timestep_string.split('-')[1])

    transferred_string = splitted_text[3]
    transfered_split = transferred_string.split(' ')
    print('transfered_split', transfered_split)
    transferred_value = float(transfered_split[0]) if transfered_split[0] != '' else float(transfered_split[1])
    transferred_unity = transfered_split[1] if transfered_split[0] != '' else transfered_split[2]

    transferred_bytes = -1
    if transferred_unity == 'MBytes':
        transferred_bytes = transferred_value * 1024 * 1024
    elif transferred_unity == 'KBytes':
        transferred_bytes = transferred_value * 1024
    else:
        transferred_bytes = transferred_value


    bandwidth_string = splitted_text[4]
    bandwidth_split = bandwidth_string.split(' ')
    bandwidth_value = float(bandwidth_split[0])
    bandwidth_unity = bandwidth_split[1]

    bandwidth_mbps = -1
    if bandwidth_unity == 'Mbits/sec':
        bandwidth_mbps = bandwidth_value
    elif bandwidth_unity == 'Kbits/sec':
        bandwidth_mbps = bandwidth_value / 1024


    return timestep, transferred_bytes, bandwidth_mbps



def main():
    input_lines = []
    count = 0

    with open(txt_filename, 'r') as inputfile:
        lines = inputfile.readlines()

        for line in lines:
            if count > 2:
                if line == '- - - - - - - - - - - - - - - - - - - - - - - - -\n':
                    break

                timestep, transferred_bytes, bandwidth_mbps = parseLine(line)
                input_lines.append([timestep, transferred_bytes, bandwidth_mbps])
            count += 1

    with open(csv_filename, 'w+', newline='') as csvfile:
        writer = csv.writer(csvfile, delimiter=';')
        writer.writerow(['Timestep', 'Transferred Bytes', 'Bandwidth (Mbps)'])

        for line in input_lines:
            writer.writerow(line)


if __name__ == '__main__':
    main()
