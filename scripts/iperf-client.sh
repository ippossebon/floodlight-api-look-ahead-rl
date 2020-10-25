#!/bin/bash

if [[ $# -ne 3 ]]; then
  echo "Expected 3 parameters, received $#"
  echo "Usage: $0 <agent> <num_flows> <flow_size>"
  exit 0
fi

agent=$1
num_flows=$2
flow_size=$3

echo ""

for (( i=0; i < $num_flows; i++ )); do
  server_port=$(($i+5201))
  client_port=$(($i*2+46110))

  iperf3 -c iperfs_server_1 -B iperfs_client_1 --cport $client_port -p $server_port -n $flow_size > ~/floodlight-api-look-ahead-rl/output-experiments-iperfs/$agent-client-$client_port-$num_flows-$flow_size-v$i.log &
done

echo "Clients done"
