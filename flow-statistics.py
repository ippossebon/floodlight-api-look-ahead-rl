import requests


response = requests.get('http://localhost:8080/wm/core/switch/all/flow/json')
response_data = response.json()

switch_ids = sorted(response_data.keys())
statistics = {}

for switch_id in switch_ids:
    num_flows = len(response_data[switch_id]['flows'])
    statistics[switch_id] = num_flows

print(statistics)
