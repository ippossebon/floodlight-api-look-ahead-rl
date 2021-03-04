#!/bin/bash

if [[ $# -ne 2 ]]; then
  echo "Expected 2 parameters, received $#"
  echo "Usage: $0 <agent> <iter>"
  exit 0
fi

agent=$1
iter=$2

flows_sizes=("25M" "50M" "100M" "200M" "400M" "800M" "1600M")

for j in ${!flows_sizes[@]}; do
  flow_size=${flows_sizes[$j]}
  port=$(($j+5201))
  filename="~/floodlight-api-look-ahead-rl/output-experiments-iperfs/$agent-server-$port-$flow_size-v$iter.log"

  echo "$filename"
  ssh mininet@192.168.68.250 "ssh -f 10.0.0.2 iperf3 -s -p $port -1 > $filename"
done

sleep 5
echo "Servers ready"
