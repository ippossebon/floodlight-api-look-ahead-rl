import json

data = {}
with open('snahpshots-json.txt', 'r') as infile, \
     open('snahpshots-json-formatted.txt', 'w+') as outfile:
    data = infile.read()
    data = data.replace("\\", "")
    outfile.write(data)
