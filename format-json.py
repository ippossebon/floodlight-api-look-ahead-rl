import json

data = {}
with open('./snapshots-json-big-file.txt', 'r') as infile, \
     open('./snapshots-json-big-file-formatted.txt', 'w+') as outfile:
    data = infile.read()
    data = data.replace("\\", "")
    outfile.write(data)
