- **Dataset collection**


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

h2 -> h1
h3 -> h1
h4 -> h1

h1 -> h3
h2 -> h3
h4 -> h3

h1 -> h4
h2 -> h4
h3 -> h4

- **Features collected for each snapshot**


snapshot_count,
flow_id,
flow["hard_timeout_s"],
flow["byte_count"],
flow["idle_timeout_s"],
flow["packet_count"],
flow["duration_sec"],
timestamp



- **File format**


One instance per line, with the features on the following order:


`snapshot_count, flow_id, flow["hard_timeout_s"], flow["byte_count"], flow["idle_timeout_s"], flow["packet_count"], flow["duration_sec"], timestamp`

Each snapshot file corresponds to a flow.
