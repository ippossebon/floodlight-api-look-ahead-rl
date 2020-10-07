#!/bin/bash

# Declare an array of string with type
declare -a ClientPortsArray=("46110" "46112" "46114" "46116" "46118" "46120" "46122" "46124" "46126" "46128")

# Iterate the string array using for loop
for client_port in ${ClientPortsArray[@]}; do
  # Flow entries on S1
  entry1 = $client_port
  curl -X POST http://localhost:8080//wm/staticentrypusher/json -d '{
        "switch": "00:00:00:00:00:00:00:01",
        "name": "'s1-flow-$client_port'"
        "priority": "0",
        "in_port": "1",
        "active": "true",
        "eth_type": "0x0800",
        "ipv4_src": "10.0.0.1",
        "ipv4_dst": "10.0.0.2",
        "tcp_src": "'$client_port'",
        "tcp_dst": "5201",
        "actions": "output=2"
    }'

    # Flow entries on S2
    curl -X POST http://localhost:8080//wm/staticentrypusher/json -d '{
          switch": "00:00:00:00:00:00:00:02",
          "name": "'s2-flow-$client_port'",
          "priority": "0",
          "in_port": "1",
          "active": "true",
          "eth_type": "0x0800",
          "ipv4_src": "10.0.0.1",
          "ipv4_dst": "10.0.0.2",
          "tcp_src": "'$client_port'",
          "tcp_dst": "5201",
          "actions": "output=4"
      }'

      # Flow entries on S3
      curl -X POST http://localhost:8080//wm/staticentrypusher/json -d '{
            "switch": "00:00:00:00:00:00:00:03",
            "name": "'s3-flow-$client_port'",
            "priority": "0",
            "in_port": "2",
            "active": "true",
            "eth_type": "0x0800",
            "ipv4_src": "10.0.0.1",
            "ipv4_dst": "10.0.0.2",
            "tcp_src": "'$client_port'",
            "tcp_dst": "5201",
            "actions": "output=1"
      }'
done
