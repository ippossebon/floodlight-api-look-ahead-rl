#!/bin/bash
INPUT=initial_flow_entries.csv
OLDIFS=$IFS
IFS=','
[ ! -f $INPUT ] && { echo "$INPUT file not found"; exit 99; }

while read rulename switchid tcpsrc tcpdst outport
do
  RULENAME=rulename
  SWITCHID=switchid
  TCPSRC=tcpsrc
  TCPDST=tcpdst
  OUTPORT=outport

  wget --no-check-certificate --quiet \
    --method POST \
    --timeout=0 \
    --header 'Content-Type: application/json' \
    --body-data '{
      "name": "{{rulename}}",
      "switch": "{{switchid}}",
      "active": "true",
      "eth_type": "0x0800",
      "ipv4_src": "10.0.0.1",
      "ipv4_dst": "10.0.0.2",
      "ip_proto": "0x06",
      "tcp_src": "{{tcpsrc}}",
      "tcp_dst": "{{tcpdst}}",
      "actions": "output={{outport}}"
  }' \
     'http://192.168.68.250:8080/wm/staticflowpusher/json'
done < $INPUT
IFS=$OLDIFS
