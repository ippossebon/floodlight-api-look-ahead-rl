import csv

def parseLine(line):
    splitted_text = line.split(';')

    step = splitted_text[0]
    state = splitted_text[1]
    reward_str = splitted_text[2]


    reward = reward_str.replace('[', '')
    reward = reward.replace(']', '')
    reward = reward.replace(' ', '')

    return step, state, float(reward)


def parseAppOutput(filename):
    input_lines = []
    count = 0

    original_filename = filename + '.csv'
    with open(original_filename, 'r') as inputfile:
        lines = inputfile.readlines()

        for line in lines:
            if count > 1:
                step, state, reward = parseLine(line)
                input_lines.append([step, state, reward])
            count += 1

    new_filename = filename + '-parsed.csv'
    with open(new_filename, 'w+', newline='') as csvfile:
        writer = csv.writer(csvfile, delimiter=';')
        writer.writerow(['Step', 'State', 'Reward'])

        for line in input_lines:
            writer.writerow(line)

    return new_filename
