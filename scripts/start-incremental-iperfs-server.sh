#!/bin/bash

if [[ $# -ne 4 ]]; then
  echo "Expected 4 parameters, received $#"
  echo "Usage: $0 <agent> <interval> <proportion> <iter>"
  exit 0
fi

agent=$1
interval=$2
proportion=$3
iter=$4


# MiceFlows / EF
case $proportion in
  0) flows_sizes=("50M" "80M" "100M" "200M" "300M" "400M" "800M" "1024M") ;; # 25/75
  1) flows_sizes=("50M" "60M" "80M" "90M" "100M" "400M" "800M" "1024M") ;; # 50/50
  2) flows_sizes=("50M" "60M" "70M" "80M" "90M" "95M" "100M" "1024M") ;; # 75/25
esac


for j in "${!flows_sizes[@]}"; do
  flow_size=${flows_sizes[j]}
  port=$(($j+5201))
  filename="~/floodlight-api-look-ahead-rl/output-experiments-iperfs/$agent-server-$port-$flow_size-$interval-proportion_$proportion-v$iter.log"

  ssh mininet@192.168.68.250 "ssh -f 10.0.0.2 iperf3 -s -p $port -1 > $filename" &
  echo "$filename"
done

sleep 5
echo "Servers ready"
