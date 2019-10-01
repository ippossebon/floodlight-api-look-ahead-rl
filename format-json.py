import json

data = {}
with open('./snapshots-madrugada-30-set--fallback.txt', 'r') as infile, \
     open('./snapshots-madrugada-30-set--fallback-formatted.txt', 'w+') as outfile:
    data = infile.read()
    data = data.replace("\\", "")
    outfile.write(data)
