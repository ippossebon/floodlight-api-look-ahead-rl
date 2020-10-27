#!/bin/bash

if [[ $# -ne 4 ]]; then
  echo "Expected 4 parameters, received $#"
  echo "Usage: $0 <agent> <num_iperfs> <flow_size> <iter>"
  exit 0
fi

agent=$1
num_iperfs=$2
flow_size=$3
iter=$4

# Start iperf3 servers

for (( i=0; i < $num_iperfs; i++ )); do
  port=$(($i+5201))
  filename="~/floodlight-api-look-ahead-rl/output-experiments-iperfs/$agent-server-$port-$num_iperfs-flows-$flow_size-v$iter.log"
  echo "$filename"
  ssh mininet@192.168.68.250 "ssh -f 10.0.0.2 iperf3 -s -p $port -1 > $filename"
done

sleep 5
echo "Servers ready"
