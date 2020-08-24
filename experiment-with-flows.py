from utilities.staticEntryPusher import StaticEntryPusher


"""
Ideia do experimento: iniciar com 3 fluxos.

sleep(30)

Mais um fluxo. Mais um fluxo, e assim por dianteself.

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
pusher = StaticEntryPusher(CONTROLLER_IP)

sleep(10)

flow1 = {
    'switch':'00:00:00:00:00:00:00:01',
    'name':'flow_1',
    'cookie':'0',
    'priority':'32768',
    'in_port':'1',
    'active':'true',
    'actions':'output=2'
    }

flow2 = {
    'switch':'00:00:00:00:00:00:00:01',
    'name':'flow_2',
    'cookie':'0',
    'priority':'32768',
    'in_port':'1',
    'active':'true',
    'actions':'output=2'
    }

pusher.set(flow1)
pusher.set(flow2)

# sleep(30)
# flow3 = {
#     'switch':'00:00:00:00:00:00:00:01',
#     'name':'flow_1',
#     'cookie':'0',
#     'priority':'32768',
#     'in_port':'1',
#     'active':'true',
#     'actions':'output=flood'
#     }
#
# pusher.set(flow3)
