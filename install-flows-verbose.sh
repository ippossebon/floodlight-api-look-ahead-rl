#!/bin/bash

# declare -a ClientPortsArray=("46110" "46112" "46114" "46116" "46118" "46120" "46122" "46124" "46126" "46128")
curl -X POST http://192.168.68.127:8080/wm/staticflowpusher/json -d '{
      "switch": "00:00:00:00:00:00:00:01",
      "name": "s1-flow-46110-to-5201",
      "priority": "0",
      "in_port": "1",
      "active": "true",
      "eth_type": "0x0800",
      "ipv4_src": "10.0.0.1",
      "ipv4_dst": "10.0.0.2",
      "tcp_src": "46110",
      "tcp_dst": "5201",
      "actions": "output=2"
  }'

curl -X POST http://192.168.68.127:8080/wm/staticflowpusher/json -d '{
    "switch": "00:00:00:00:00:00:00:01",
    "name": "s1-flow-5201-to-46110",
    "priority": "0",
    "in_port": "1",
    "active": "true",
    "eth_type": "0x0800",
    "ipv4_src": "10.0.0.1",
    "ipv4_dst": "10.0.0.2",
    "tcp_dst": "46110",
    "tcp_src": "5201",
    "actions": "output=2"
}'

# Flow entries on S2
curl -X POST http://192.168.68.127:8080/wm/staticflowpusher/json -d '{
    switch": "00:00:00:00:00:00:00:02",
    "name": "s2-flow-46110",
    "priority": "0",
    "in_port": "1",
    "active": "true",
    "eth_type": "0x0800",
    "ipv4_src": "10.0.0.1",
    "ipv4_dst": "10.0.0.2",
    "tcp_src": "46110",
    "tcp_dst": "5201",
    "actions": "output=4"
}'

curl -X POST http://192.168.68.127:8080/wm/staticflowpusher/json -d '{
      switch": "00:00:00:00:00:00:00:02",
      "name": "s2-flow-5201-to-46110",
      "priority": "0",
      "in_port": "1",
      "active": "true",
      "eth_type": "0x0800",
      "ipv4_src": "10.0.0.1",
      "ipv4_dst": "10.0.0.2",
      "tcp_dst": "46110",
      "tcp_src": "5201",
      "actions": "output=4"
  }'

# Flow entries on S3
curl -X POST http://192.168.68.127:8080/wm/staticflowpusher/json -d '{
      "switch": "00:00:00:00:00:00:00:03",
      "name": "s3-flow-46110",
      "priority": "0",
      "in_port": "2",
      "active": "true",
      "eth_type": "0x0800",
      "ipv4_src": "10.0.0.1",
      "ipv4_dst": "10.0.0.2",
      "tcp_src": "46110",
      "tcp_dst": "5201",
      "actions": "output=1"
}'

curl -X POST http://192.168.68.127:8080/wm/staticflowpusher/json -d '{
      "switch": "00:00:00:00:00:00:00:03",
      "name": "s3-flow-5201-to-46110",
      "priority": "0",
      "in_port": "2",
      "active": "true",
      "eth_type": "0x0800",
      "ipv4_src": "10.0.0.1",
      "ipv4_dst": "10.0.0.2",
      "tcp_dst": "46110",
      "tcp_src": "5201",
      "actions": "output=1"
}'
