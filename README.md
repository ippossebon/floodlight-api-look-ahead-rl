# floodlight-api-look-ahead-rl



**FLOW features**

Data format for each flow on `/wm/core/switch/all/flow/json`:

```
"priority": "1",
"hard_timeout_s": "0",
"byte_count": "294",
"idle_timeout_s": "5",
"duration_nsec": "608000000",
"packet_count": "3",
"duration_sec": "3",
"version": "OF_13",
"table_id": "0x0",
"flags": [],
"cookie": "9007199758057472",
"match": {
  "eth_dst": "00:00:00:00:00:02",
  "ipv4_dst": "10.0.0.2",
  "ipv4_src": "10.0.0.1",
  "eth_type": "0x800", // protocol
  "eth_src": "00:00:00:00:00:01",
  "in_port": "1"
},
"instructions": {
  "instruction_apply_actions": {
    "actions": "output=2"
  }
}
```

**SWITCH features**

Data format from `/wm/statistics/bandwidth/all/all/json`:

```
{
  "bits-per-second-rx" : "0",
  "dpid" : "00:00:00:00:00:00:00:02",
  "updated" : "Mon Sep 02 15:54:17 EDT 2019",
  "link-speed-bits-per-second" : "10000000",
  "port" : "1",
  "bits-per-second-tx" : "6059"
}
```

**Dataset collection**
Flows duration (seconds):
7
9
10
20
24
36
42
58
69
76
81
99
115
120
150
200
300
500
800
1000

h1 -> h2
h3 -> h2
h4 -> h2
h5 -> h2

h2 -> h1
h3 -> h1
h4 -> h1
h5 -> h1

h1 -> h3
h2 -> h3
h4 -> h3
h5 -> h3

h1 -> h4
h2 -> h4
h3 -> h4
h5 -> h4

h1 -> h5
h2 -> h5
h3 -> h5
h4 -> h5
