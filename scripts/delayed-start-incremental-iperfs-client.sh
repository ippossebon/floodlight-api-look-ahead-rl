#!/bin/bash

if [[ $# -ne 2 ]]; then
  echo "Expected 2 parameters, received $#"
  echo "Usage: $0 <agent> <iter>"
  exit 0
fi

agent=$1
iter=$2

# declare -A num_steps_per_size=(["25M"] = 75 ["50M"] = 150 ["100M"] = 250 ["200M"] = 350 ["400M"] = 750 ["800M"] = 1750 ["1600M"] = 3750)
flows_sizes=("25M" "50M" "100M" "200M" "400M" "800M" "1600M")

sleep 10

for j in ${!flows_sizes[@]}; do
  server_port=$(($j+5201))
  client_port=$(($j*2+46110))
  flow_size=${allThreads[$j]}

  # ssh mininet@192.168.68.250 "ssh -f 10.0.0.1 iperf3 -c 10.0.0.2 -B 10.0.0.1 --cport $client_port -p $server_port -n $flow_size > ~/floodlight-api-look-ahead-rl/output-experiments-iperfs/$agent-client-$client_port-$flow_size-v$iter.log &"
  ssh mininet@192.168.68.250 "ssh 10.0.0.1 iperf3 -c 10.0.0.2 -B 10.0.0.1 --cport $client_port -p $server_port -n $flow_size > ~/floodlight-api-look-ahead-rl/output-experiments-iperfs/$agent-client-$client_port-$flow_size-v$iter.log" &
done

wait
echo "Clients done"
