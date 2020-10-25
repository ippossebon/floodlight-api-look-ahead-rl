#!/bin/bash

if [[ $# -ne 3 ]]; then
  echo "Expected 3 parameters, received $#"
  echo "Usage: $0 <agent> <num_flows> <flow_size>"
  exit 0
fi

agent=$1
num_flows=$2
flow_size=$3

ssh mininet@192.168.68.250 "ssh 10.0.0.2 ~/floodlight-api-look-ahead-rl/scripts/iperf-server.sh $agent $num_flows $flow_size &"
sleep 2
ssh mininet@192.168.68.250 "ssh 10.0.0.1 ~/floodlight-api-look-ahead-rl/scripts/iperf-client.sh $agent $num_flows $flow_size &"
