from load_balance_with_floodlight import LoadBalanceEnv
from staticFlowPusher import StaticFlowPusher

import json
import time
import requests

# Fluxo sai de H1 e vai para H2
env = LoadBalanceEnv(num_flows = 10, source_port = 1, source_switch = 0, target_port = 1, target_switch = 2)

# headers = {
#     'Content-type': 'application/json',
#     'Accept': 'application/json',
# }

flow1 = {
    'switch':'00:00:00:00:00:00:00:01',
    'name':'flow_1',
    'cookie':'0',
    'priority':'32768',
    'in_port':'1',
    'active':'true',
    'actions':'output=2'
}

response = requests.post(
    'http://localhost:8080/wm/staticentrypusher/json',
    data=json.dumps(flow1)
)
print('response = ', response)

time.sleep(4)

print('Vai fazer um GET nos fluxos.')

env.getFlows()

print('Feito.')
