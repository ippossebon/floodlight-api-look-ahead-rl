import csv

csv_filename = '../data/output-app-15-set-1_new.csv'
new_filename = '../data/rx-values/15-set_new.csv'
count = 0

def parseLine(line):
    splitted_text = line.split(';')
    state_str = splitted_text[1]
    state_str = state_str.replace('[',  '')
    state_str = state_str.replace(']', '')
    state = state_str.split(' ')

    new_state = []
    for value in state:
        if value != '':
            new_state.append(float(value.replace(',', '')))

    return new_state

def main():
    input_lines = []
    count = 0

    with open(csv_filename, 'r') as inputfile:
        lines = inputfile.readlines()

        for line in lines:
            if count > 0:
                if line == '- - - - - - - - - - - - - - - - - - - - - - - - -\n':
                    break

                new_state = parseLine(line)
                input_lines.append([step, state, reward])
            count += 1

    with open(csv_filename, 'w+', newline='') as csvfile:
        writer = csv.writer(csvfile, delimiter=';')
        writer.writerow(['S1.1', 'S1.2', 'S1.3', 'S2.1', 'S2.2', 'S2.3', 'S2.4', 'S3.1', 'S3.2', 'S3.3', 'S3.4', 'S4.1', 'S4.2', 'S4.3', 'S5.1', 'S5.2'])

        for line in input_lines:
            writer.writerow(line)


if __name__ == '__main__':
    main()
