#!/bin/bash

if [[ $# -ne 4 ]]; then
  echo "Expected 4 parameters, received $#"
  echo "Usage: $0 <agent> <num_flows> <flow_size> <replication>"
  exit 0
fi

agent=$1
num_flows=$2
flow_size=$3
replication=$4

# Start iperf3 servers

for (( i=0; i < $num_flows; i++ )); do
  port=$(($i+5201))
  filename="~/floodlight-api-look-ahead-rl/output-experiments-iperfs/$agent-server-$port-$num_flows-flows-$flow_size-v$replication.log"
  echo "$filename"
  ssh mininet@192.168.68.250 "ssh -f 10.0.0.2 iperf3 -s -p $port -1 > $filename"
done

echo "Servers ready"

sleep 5


ssh mininet@192.168.68.250 "ssh -f 10.0.0.1 ~/floodlight-api-look-ahead-rl/scripts/iperf-client.sh $agent $num_flows $flow_size $replication"
