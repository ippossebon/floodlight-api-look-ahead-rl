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


# load-balance-gym
Gym for Reinforcement Learning load balancing on SDN


**To install the environment go to the root folder and run:**


Referece: https://medium.com/analytics-vidhya/building-custom-gym-environments-for-reinforcement-learning-24fa7530cbb5

`pip install -e .` inside `load_balance_gym` file


**How to use the gym environment**

```
import gym
import gym_foo
env = gym.make('load-balance-v0')
```


**Environment topology**

![Network topology used for modeling this OpenAi gym environment](./topology.jpg?raw=true "Network topology")


**Actions mapping**

* Action 0 = void action, keeps everything as it is


* Action 1 = Splits incoming flow on S1. Should route half of the flow to [a, c, g, i] and the other half to [a, b, f, i]


* Action 2 = Splits incoming flow on S2. Should route half of the flow to [a, b, d, h, i] and the other half to [a, b, e, g, i]

*Flow came through b, came out through d and e*


* Action 3 = Should route the flow to [a, b, f, i]


* Action 4 = Splits incoming flow on S4. Should route half of the flow to [a, c, g, i] and the other half to [a, c, e, f, i]

*Flow came through c and came out through g and e*

* Action 5 = Should route the flow to [a, c, g, i]


* Action 6 = Should route the flow to [a, b, d, h, i]


* Action 7 = Should route the flow to [a, b, e, g, i]


* Action 8 = Should route the flow to [a, c, e, d, h, i]


* Action 9 = Should route the flow to [a, c, e, f, i]


* Action 4 = Splits incoming flow on S3. Should route 1/3 of the flow to [a, b, d, h, i], 1/3 to [a, b, e, g, i], and 1/3 to [a, b, f, i]
*Flow came through b and came out through d, e and f*
