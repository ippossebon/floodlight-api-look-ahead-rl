import json

data = {}
with open('./snapshots/h1-as-server/snapshot-h2-client-h1-server--fallback.txt', 'r') as infile, \
     open('./snapshots/h1-as-server/snapshot-h2-client-h1-server--fallback-formatted.txt', 'w+') as outfile:
    data = infile.read()
    data = data.replace("\\", "")
    outfile.write(data)
