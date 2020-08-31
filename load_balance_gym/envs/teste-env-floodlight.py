from load_balance_with_floodlight import LoadBalanceEnv
from staticFlowPusher import StaticFlowPusher

import json
import time
import requests

"""
Ideia do experimento: iniciar com 5 fluxos.

sleep(30)

Mais um fluxo. Mais um fluxo, e assim por diante.

O objetivo é fazer com que o sistema acomode os fluxos na rede. Para um número N
de fluxos, em qualquer topologia (dado que utilizamos a aplicação para descobrir
os caminhos possíveis.)

Entrada para o sistema: source_switch, source_port, dst_switch, dst_port

source_switch: 00:00:00:00:00:00:00:01
source_port: 1
dst_switch: 00:00:00:00:00:00:00:03
dst_port: 1

Setup do experimento:
Todos os fluxos começam por a, b, f, i

"""
CONTROLLER_IP = 'http://localhost'
CONTROLLER_HOST = '{host}:8080'.format(host=CONTROLLER_IP)
NUM_FLOWS = 5

for flow_index in range(0, NUM_FLOWS):
    # Adiciona fluxo na rede.
    flow_name = 'flow-{0}'.format(flow_index)
    flow = {
        'switch':'00:00:00:00:00:00:00:01',
        'name': flow_name,
        'cookie':'0',
        'priority':'32768',
        'in_port':'1',
        'active':'true',
        'actions':'output=2'
    }

    response = requests.post(
        'http://localhost:8080/wm/staticentrypusher/json',
        data=json.dumps(flow)
    )
    print('Resposta ao adicionar novo fluxo na rede: ', response)


# Fluxo sai de H1 e vai para H2
env = LoadBalanceEnv(source_port=1, source_switch=0, target_port=1, target_switch=2)

time.sleep(10)


switch_id = '00:00:00:00:00:00:00:01'
# Indica quais sao os fluxos que passam por aquele switch.
# response = requests.get('{host}/wm/staticentrypusher/list/{switch_id}/json'.format(host=CONTROLLER_HOST, switch_id=switch_id))
# response_data = response.json()

# response = requests.get('{host}/wm/core/switch/all/flow/json'.format(host=CONTROLLER_HOST))
# response_data = response.json()
#
# print('Resposta desse cara ', response_data)

action = [0, 1, 2]
env.actionBelongsToPath(action)


# env.getMostCostlyFlow('00:00:00:00:00:00:00:01')
time.sleep(30)


#
# print('Vai dar um step.')
# action = env.action_space.sample()
# print('Action = ', action)
# next_state, reward = env.step(action)
# print('next_state = ', next_state)
# print('reward = ', reward)

print('Feito.')
