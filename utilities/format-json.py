import json

data = {}
with open('./snapshots/h4-as-server/snapshot-h3-client-h4-server--fallback.txt', 'r') as infile, \
     open('./snapshots/h4-as-server/snapshot-h3-client-h4-server--fallback-formatted.txt', 'w+') as outfile:
    data = infile.read()
    data = data.replace("\\", "")
    outfile.write(data)
