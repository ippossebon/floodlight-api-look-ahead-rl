import json

data = {}
with open('./snapshots/h2-as-server/snapshot-h4-client-h2-server--fallback.txt', 'r') as infile, \
     open('./snapshots/h2-as-server/snapshot-h4-client-h2-server--fallback-formatted.txt', 'w+') as outfile:
    data = infile.read()
    data = data.replace("\\", "")
    outfile.write(data)
