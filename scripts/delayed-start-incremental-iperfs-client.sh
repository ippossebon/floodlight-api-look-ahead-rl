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

flows_sizes_0=("50M" "80M" "100M" "200M" "300M" "400M" "800M" "1024M") # 25/75
flows_sizes_1=("50M" "60M" "80M" "90M" "100M" "400M" "800M" "1024M") # 50/50
flows_sizes_2=("50M" "60M" "100M" "200M" "300M" "400M" "800M" "1024M") # 25/75

case $proportion in
  0) flows_sizes=$flows_sizes_0 ;;
  1) flows_sizes=$flows_sizes_1 ;;
  2) flows_sizes=$flows_sizes_2 ;;
esac

sleep 10

for j in ${!flows_sizes[@]}; do
  server_port=$(($j+5201))
  client_port=$(($j*2+46110))
  flow_size=${flows_sizes[$j]}

  filename="~/floodlight-api-look-ahead-rl/output-experiments-iperfs/$agent-client-$client_port-$flow_size-$interval-proportion_$proportion-v$iter.log"
  echo "$filename"
  # ssh mininet@192.168.68.250 "ssh -f 10.0.0.1 iperf3 -c 10.0.0.2 -B 10.0.0.1 --cport $client_port -p $server_port -n $flow_size > ~/floodlight-api-look-ahead-rl/output-experiments-iperfs/$agent-client-$client_port-$flow_size-v$iter.log &"
  ssh mininet@192.168.68.250 "ssh 10.0.0.1 iperf3 -c 10.0.0.2 -B 10.0.0.1 --cport $client_port -p $server_port -n $flow_size > $filename" &
  sleep $interval

done

wait
echo "Clients done"
