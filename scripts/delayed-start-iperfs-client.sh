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

sleep 10

for (( i=0; i < $num_iperfs; i++ )); do
  server_port=$(($i+5201))
  client_port=$(($i*2+46110))

  ssh mininet@192.168.68.250 "ssh -f 10.0.0.1 iperf3 -c 10.0.0.2 -B 10.0.0.1 --cport $client_port -p $server_port -n $flow_size > ~/floodlight-api-look-ahead-rl/output-experiments-iperfs/$agent-client-$client_port-$num_iperfs-flows-$flow_size-v$iter.log &"
  # ssh mininet@192.168.68.250 "ssh 10.0.0.1 iperf3 -c 10.0.0.2 -B 10.0.0.1 --cport $client_port -p $server_port -n $flow_size > ~/floodlight-api-look-ahead-rl/output-experiments-iperfs/$agent-client-$client_port-$num_iperfs-flows-$flow_size-v$iter.log" &
done
wait
echo "Clients done"
