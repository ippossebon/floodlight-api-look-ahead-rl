import csv

txt_filename = '../data/output-app-2.csv'
csv_filename = '../data/output-app-2_new.csv'

count = 0

def parseLine(line):
    splitted_text = line.split(';')
    step = splitted_text[0]
    state = splitted_text[1]
    reward_str = splitted_text[2]

    reward = reward_str.replace('[', '')
    reward = reward.replace(']', '')
    reward = reward.replace(' ', '')

    return step, state, float(reward)


def main():
    input_lines = []
    count = 0

    with open(txt_filename, 'r') as inputfile:
        lines = inputfile.readlines()

        for line in lines:
            if count > 2:
                if line == '- - - - - - - - - - - - - - - - - - - - - - - - -\n':
                    break

                step, state, reward = parseLine(line)
                input_lines.append([step, state, reward])
            count += 1

    with open(csv_filename, 'w+', newline='') as csvfile:
        writer = csv.writer(csvfile, delimiter=';')
        writer.writerow(['Step', 'State', 'Reward'])

        for line in input_lines:
            writer.writerow(line)


if __name__ == '__main__':
    main()
