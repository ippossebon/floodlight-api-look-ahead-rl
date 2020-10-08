#!/bin/bash

# declare -a ClientPortsArray=("46110" "46112" "46114" "46116" "46118" "46120" "46122" "46124" "46126" "46128")
curl -X POST http://192.168.68.250:8080/wm/staticflowpusher/json -d '{
      "switch": "00:00:00:00:00:00:00:01",
      "name": "s1-flow-h1-to-h2",
      "priority": "0",
      "in_port": "1",
      "active": "true",
      "eth_type": "0x0800",
      "ipv4_src": "10.0.0.1",
      "ipv4_dst": "10.0.0.2",
      "actions": "output=2"
  }'

curl -X POST http://192.168.68.250:8080/wm/staticflowpusher/json -d '{
    "switch": "00:00:00:00:00:00:00:01",
    "name": "s1-flow-h1-to-h2--reversed",
    "priority": "0",
    "in_port": "2",
    "active": "true",
    "eth_type": "0x0800",
    "ipv4_src": "10.0.0.2",
    "ipv4_dst": "10.0.0.1",
    "actions": "output=1"
}'


# H3
curl -X POST http://192.168.68.250:8080/wm/staticflowpusher/json -d '{
      "switch": "00:00:00:00:00:00:00:01",
      "name": "s1-flow-h3-to-h2",
      "priority": "0",
      "in_port": "3",
      "active": "true",
      "eth_type": "0x0800",
      "ipv4_src": "10.0.0.3",
      "ipv4_dst": "10.0.0.2",
      "actions": "output=2"
  }'

curl -X POST http://192.168.68.250:8080/wm/staticflowpusher/json -d '{
    "switch": "00:00:00:00:00:00:00:01",
    "name": "s1-flow-h3-to-h2--reversed",
    "priority": "0",
    "in_port": "2",
    "active": "true",
    "eth_type": "0x0800",
    "ipv4_src": "10.0.0.3",
    "ipv4_dst": "10.0.0.1",
    "actions": "output=3"
}'

# H4
curl -X POST http://192.168.68.250:8080/wm/staticflowpusher/json -d '{
      "switch": "00:00:00:00:00:00:00:01",
      "name": "s1-flow-h4-to-h2",
      "priority": "0",
      "in_port": "4",
      "active": "true",
      "eth_type": "0x0800",
      "ipv4_src": "10.0.0.4",
      "ipv4_dst": "10.0.0.2",
      "actions": "output=2"
  }'

curl -X POST http://192.168.68.250:8080/wm/staticflowpusher/json -d '{
    "switch": "00:00:00:00:00:00:00:01",
    "name": "s1-flow-h4-to-h2--reversed",
    "priority": "0",
    "in_port": "2",
    "active": "true",
    "eth_type": "0x0800",
    "ipv4_src": "10.0.0.4",
    "ipv4_dst": "10.0.0.1",
    "actions": "output=4"
}'


# Flow entries on S2
curl -X POST http://192.168.68.250:8080/wm/staticflowpusher/json -d '{
    switch": "00:00:00:00:00:00:00:02",
    "name": "s2-flow-h1-t0-h2",
    "priority": "0",
    "in_port": "1",
    "active": "true",
    "eth_type": "0x0800",
    "ipv4_src": "10.0.0.1",
    "ipv4_dst": "10.0.0.2",
    "actions": "output=4"
}'

curl -X POST http://192.168.68.250:8080/wm/staticflowpusher/json -d '{
      switch": "00:00:00:00:00:00:00:02",
      "name": "s2-flow-h1-t0-h2--reversed",
      "priority": "0",
      "in_port": "4",
      "active": "true",
      "eth_type": "0x0800",
      "ipv4_src": "10.0.0.2",
      "ipv4_dst": "10.0.0.1",
      "actions": "output=1"
  }'

# Flow entries on S3
curl -X POST http://192.168.68.250:8080/wm/staticflowpusher/json -d '{
      "switch": "00:00:00:00:00:00:00:03",
      "name": "s3-flow-h1-to-h2",
      "priority": "0",
      "in_port": "2",
      "active": "true",
      "eth_type": "0x0800",
      "ipv4_src": "10.0.0.1",
      "ipv4_dst": "10.0.0.2",
      "actions": "output=1"
}'

curl -X POST http://192.168.68.250:8080/wm/staticflowpusher/json -d '{
      "switch": "00:00:00:00:00:00:00:03",
      "name": "s3-flow-h1-to-h2--reversed",
      "priority": "0",
      "in_port": "1",
      "active": "true",
      "eth_type": "0x0800",
      "ipv4_src": "10.0.0.2",
      "ipv4_dst": "10.0.0.1",
      "actions": "output=2"
}'
