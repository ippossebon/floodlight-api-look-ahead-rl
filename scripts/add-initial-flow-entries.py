#!/usr/bin/python
# -*- coding: utf-8 -*-

import requests
import json
from csv import reader

urlPath = 'http://192.168.68.250:8080/wm/staticflowpusher/json'
headers = {
    'Content-type': 'application/json',
    'Accept': 'application/json',
}

with open('./initial_flow_entries.csv', 'r') as read_obj:
    csv_reader = reader(read_obj)
    header = next(csv_reader)

    if header != None:
        for row in csv_reader:
            rule_name = str(row[0])
            switch_id = str(row[1])
            tcp_src = row[2]
            tcp_dst = row[3]
            out_port = str(row[4])

            print(switch_id)

            rule = {
                "name": rule_name,
                "switch": switch_id,
                "active": "true",
                "eth_type": "0x0800",
                "ipv4_src": "10.0.0.1",
                "ipv4_dst": "10.0.0.2",
                "tcp_src": tcp_src,
                "tcp_dst": tcp_dst,
                "ip_proto": "0x06",
                "actions": "output={0}".format(out_port)
            }

            data = json.dumps(rule)
            print(data)
            response = requests.post(urlPath, data=data, headers=headers)
            print(response)
