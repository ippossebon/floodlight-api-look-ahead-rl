#!/bin/bash

if [[ $# -ne 3 ]]; then
  echo "Expected 3 parameters, received $#"
  echo "Usage: $0 <agent> <num_flows> <flow_size>"
  exit 0
fi

agent=$1
num_flows=$2
flow_size=$3



for (( i=0; i < $num_flows; i++ )); do
  port=$(($i+5201))

  iperf3 -s -p $port -1 > ~/output/$agent-server-$port-$num_flows-$flow_size-v$i.log &
done