import json

data = {}
with open('./snapshots-json-20gb.txt', 'r') as infile, \
     open('./snapshots-json-20gb-formatted.txt', 'w+') as outfile:
    data = infile.read()
    data = data.replace("\\", "")
    outfile.write(data)
