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

for (( i=0; i < $num_flows; i++ )); do
  server_port=$(($i+5201))
  client_port=$(($i*2+46110))

  iperf3 -c 10.0.0.2 -B 10.0.0.1 --cport $client_port -p $server_port -n $flow_size > ~/floodlight-api-look-ahead-rl/output-experiments-iperfs/$agent-client-$client_port-$num_flows-flows-$flow_size-v$replication.log &
done

echo "Clients done"
