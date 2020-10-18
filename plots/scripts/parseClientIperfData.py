import csv

def generateServerCSVs(filenames):
    for filename in filenames:
        count = 0
        input_lines = []

        filename_txt = filename + '.txt'
        filename_csv = filename + '.csv'

        with open(filename_txt, 'r') as inputfile:
            lines = inputfile.readlines()

            for line in lines:
                if count > 5:
                    end_of_info = line == '- - - - - - - - - - - - - - - - - - - - - - - - -\n'
                    error_line = 'error' in line
                    end_of_content = end_of_info or error_line

                    if end_of_content:
                        break

                    timestep, transferred_bytes, bandwidth_mbps = parseLine(line)
                    input_lines.append([timestep, transferred_bytes, bandwidth_mbps])
                count += 1

        with open(filename_csv, 'w+', newline='') as csvfile:
            writer = csv.writer(csvfile, delimiter=';')
            writer.writerow(['Timestep', 'Transferred Bytes', 'Bandwidth (Mbps)'])

            for line in input_lines:
                writer.writerow(line)
        print('Created: ', filename_csv)

    return filenames


def parseLine(line):
    line1 = line.replace('  ', ' ')
    line2 = line1.replace('   ', ' ')
    line_replaced = line2.replace('    ', ' ')
    new_line = line_replaced.replace('[', '')
    new_line = new_line.replace(']', '')
    splitted_text = new_line.split(' ')
    line_values = [item for item in splitted_text if item != '']

    timestep_string = line_values[1]
    timestep_splitted = timestep_string.split('-')
    timestep = float(timestep_splitted[0])

    transferred_value = float(line_values[3])
    transferred_unity = line_values[4]

    transferred_bytes = -1
    if transferred_unity == 'MBytes':
        transferred_bytes = transferred_value * 1024 * 1024
    elif transferred_unity == 'KBytes':
        transferred_bytes = transferred_value * 1024
    else:
        transferred_bytes = transferred_value

    bandwidth_value = float(line_values[5])
    bandwidth_unity = line_values[6]
    bandwidth_mbps = None

    if bandwidth_unity == 'Mbits/sec':
        bandwidth_mbps = bandwidth_value
    elif bandwidth_unity == 'Kbits/sec':
        bandwidth_mbps = bandwidth_value / 1024
    else:
        # bits
        bandwidth_mbps = bandwidth_value

    return timestep, transferred_bytes, bandwidth_mbps
