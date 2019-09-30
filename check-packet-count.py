import csv

filename = './snapshots/csv/snapshots-json-big-file--client.csv'

with open(filename, 'r+') as csvfile:
    readCSV = csv.reader(csvfile, delimiter=';')

    for row in readCSV:
        print(row[8])
