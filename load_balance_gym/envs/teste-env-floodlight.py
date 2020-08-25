from load_balance_with_floodlight import LoadBalanceEnv
from staticFlowPusher import StaticFlowPusher

import time
import http.client, urllib.parse

CONTROLLER_IP = 'http://127.0.0.1:8080'

# Fluxo sai de H1 e vai para H2
env = LoadBalanceEnv(num_flows = 10, source_port = 1, source_switch = 0, target_port = 1, target_switch = 2)

params = urllib.parse.urlencode({
    'switch':'00:00:00:00:00:00:00:01',
        'name':'flow_1',
        'cookie':'0',
        'priority':'32768',
        'in_port':'1',
        'active':'true',
        'actions':'output=2'
})
headers = {
    'Content-type': 'application/json',
    'Accept': 'application/json',
}
conn = http.client.HTTPConnection(CONTROLLER_IP)
conn.request('POST', '', params, headers)
response = conn.getresponse()

print('Status = ', response.status )
print('Reason = ', response.reason)
data = response.read()

print('Data = ', data)

conn.close()

# print('vai criar o pusher')
# pusher = StaticFlowPusher(CONTROLLER_IP)
# print('criou o pusher')
#
#
# flow1 = {
#     'switch':'00:00:00:00:00:00:00:01',
#     'name':'flow_1',
#     'cookie':'0',
#     'priority':'32768',
#     'in_port':'1',
#     'active':'true',
#     'actions':'output=2'
#     }
#
# flow2 = {
#     'switch':'00:00:00:00:00:00:00:01',
#     'name':'flow_2',
#     'cookie':'0',
#     'priority':'32768',
#     'in_port':'1',
#     'active':'true',
#     'actions':'output=2'
#     }
#
# pusher.set(flow1)
# pusher.set(flow2)
# print('Adicionou fluxos.')

time.sleep(4)

print('Vai fazer um GET nos fluxos.')

env.getFlows()

print('Feito.')
