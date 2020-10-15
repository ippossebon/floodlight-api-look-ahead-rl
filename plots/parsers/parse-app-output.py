import csv

txt_filename = '../data/output-app-15-set-1.csv'
csv_filename = '../data/output-app-15-set-1_new.csv'

count = 0

def parseLine(line):
    splitted_text = line.split(';')
    line = "1; [0.408447265625, 11.921875, 0.0, 0.408447265625, 0.0, 0.0, 11.8515625, 11.7734375, 0.408203125, 11.7734375, 11.7734375, 0.0, 0.0, 0.0, 0.0, 0.0]; [1520.3286]"
    step = splitted_text[0]
    state = splitted_text[1]
    reward_str = splitted_text[2]

    reward = reward_str.replace('[', '')
    reward = reward.replace(']', '')
    reward = reward.replace(' ', '')

    return step, state, reward



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
