import json
import requests

def addFlows(num_flows):
    flow_cookie = 49539595572507912

    for flow_index in range(0, num_flows):
        # Adiciona fluxo na rede.
        # For each switch we need to push 4 flows Forward, Reverse, ForwardARP, ReverseARP

        # FLuxo FORWARD
        flow_forward = {
          'switch':'00:00:00:00:00:00:00:01',
          'name': 'flow-{0}-forward'.format(flow_index),
          # "ether-type":"0x800",
          # "src-ip":"10.0.0.1",
          # "dst-ip":"10.0.0.2",
          'cookie': str(flow_cookie),
          'priority':'32768',
          'in_port':'1',
          'active':'true',
          'actions':'output=2'
        }
        response = requests.post(
          'http://localhost:8080/wm/staticentrypusher/json',
          data=json.dumps(flow_forward)
        )

        flow_forward = {
          'switch':'00:00:00:00:00:00:00:02',
          'name': 'flow-{0}-forward'.format(flow_index),
          # "ether-type":"0x800",
          # "src-ip":"10.0.0.1",
          # "dst-ip":"10.0.0.2",
          'cookie': str(flow_cookie),
          'priority':'32768',
          'in_port':'1',
          'active':'true',
          'actions':'output=4'
        }
        response = requests.post(
          'http://localhost:8080/wm/staticentrypusher/json',
          data=json.dumps(flow_forward)
        )

        flow_forward = {
          'switch':'00:00:00:00:00:00:00:03',
          'name': 'flow-{0}-forward'.format(flow_index),
          # "ether-type":"0x800",
          # "src-ip":"10.0.0.1",
          # "dst-ip":"10.0.0.2",
          'cookie': str(flow_cookie),
          'priority':'32768',
          'in_port':'2',
          'active':'true',
          'actions':'output=1'
        }
        response = requests.post(
          'http://localhost:8080/wm/staticentrypusher/json',
          data=json.dumps(flow_forward)
        )
        #
        #
        #
        # # Fluxo ForwardARP
        # flow_forward_arp = {
        #   'switch':'00:00:00:00:00:00:00:01',
        #   'name': 'flow-{0}-forward-arp'.format(flow_index),
        #   "ether-type":"0x806",
        #   "src-ip":"10.0.0.1",
        #   "dst-ip":"10.0.0.2",
        #   'cookie': str(flow_cookie),
        #   'priority':'2',
        #   'ingress-port':'1',
        #   'active':'true',
        #   'actions':'output=2'
        # }
        # response = requests.post(
        #   'http://localhost:8080/wm/staticentrypusher/json',
        #   data=json.dumps(flow_forward_arp)
        # )
        #
        # flow_forward_arp = {
        #   'switch':'00:00:00:00:00:00:00:02',
        #   'name': 'flow-{0}-forward-arp'.format(flow_index),
        #   "ether-type":"0x806",
        #   "src-ip":"10.0.0.1",
        #   "dst-ip":"10.0.0.2",
        #   'cookie': str(flow_cookie),
        #   'priority':'2',
        #   'ingress-port':'1',
        #   'active':'true',
        #   'actions':'output=4'
        # }
        # response = requests.post(
        #   'http://localhost:8080/wm/staticentrypusher/json',
        #   data=json.dumps(flow_forward_arp)
        # )
        #
        # flow_forward_arp = {
        #   'switch':'00:00:00:00:00:00:00:03',
        #   'name': 'flow-{0}-forward-arp'.format(flow_index),
        #   "ether-type":"0x806",
        #   "src-ip":"10.0.0.1",
        #   "dst-ip":"10.0.0.2",
        #   'cookie': str(flow_cookie),
        #   'priority':'2',
        #   'ingress-port':'2',
        #   'active':'true',
        #   'actions':'output=1'
        # }
        # response = requests.post(
        #   'http://localhost:8080/wm/staticentrypusher/json',
        #   data=json.dumps(flow_forward_arp)
        # )
        #
        #
        # # FLuxo REVERSE
        # flow_reverse = {
        #   'switch':'00:00:00:00:00:00:00:03',
        #   'name': 'flow-{0}-reverse'.format(flow_index),
        #   "ether-type":"0x800",
        #   "src-ip":"10.0.0.2",
        #   "dst-ip":"10.0.0.1",
        #   'cookie': str(flow_cookie),
        #   'priority':'2',
        #   'ingress-port':'1',
        #   'active':'true',
        #   'actions':'output=2'
        # }
        # response = requests.post(
        #   'http://localhost:8080/wm/staticentrypusher/json',
        #   data=json.dumps(flow_reverse)
        # )
        #
        # flow_reverse = {
        #   'switch':'00:00:00:00:00:00:00:02',
        #   'name': 'flow-{0}-reverse'.format(flow_index),
        #   "ether-type":"0x800",
        #   "src-ip":"10.0.0.2",
        #   "dst-ip":"10.0.0.1",
        #   'cookie': str(flow_cookie),
        #   'priority':'2',
        #   'ingress-port':'4',
        #   'active':'true',
        #   'actions':'output=1'
        # }
        # response = requests.post(
        #   'http://localhost:8080/wm/staticentrypusher/json',
        #   data=json.dumps(flow_reverse)
        # )
        #
        # flow_reverse = {
        #   'switch':'00:00:00:00:00:00:00:01',
        #   'name': 'flow-{0}-reverse'.format(flow_index),
        #   "ether-type":"0x800",
        #   "src-ip":"10.0.0.2",
        #   "dst-ip":"10.0.0.1",
        #   'cookie': str(flow_cookie),
        #   'priority':'2',
        #   'ingress-port':'2',
        #   'active':'true',
        #   'actions':'output=1'
        # }
        # response = requests.post(
        #   'http://localhost:8080/wm/staticentrypusher/json',
        #   data=json.dumps(flow_reverse)
        # )
        #
        #
        # # Fluxo ReverseARP
        # flow_reverse_arp = {
        #   'switch':'00:00:00:00:00:00:00:03',
        #   'name': 'flow-{0}-reverse-arp'.format(flow_index),
        #   "ether-type":"0x806",
        #   "src-ip":"10.0.0.2",
        #   "dst-ip":"10.0.0.1",
        #   'cookie': str(flow_cookie),
        #   'priority':'2',
        #   'ingress-port':'1',
        #   'active':'true',
        #   'actions':'output=2'
        # }
        # response = requests.post(
        #   'http://localhost:8080/wm/staticentrypusher/json',
        #   data=json.dumps(flow_reverse_arp)
        # )
        #
        # flow_reverse_arp = {
        #   'switch':'00:00:00:00:00:00:00:02',
        #   'name': 'flow-{0}-reverse-arp'.format(flow_index),
        #   "ether-type":"0x806",
        #   "src-ip":"10.0.0.2",
        #   "dst-ip":"10.0.0.1",
        #   'cookie': str(flow_cookie),
        #   'priority':'2',
        #   'ingress-port':'4',
        #   'active':'true',
        #   'actions':'output=1'
        # }
        # response = requests.post(
        #   'http://localhost:8080/wm/staticentrypusher/json',
        #   data=json.dumps(flow_reverse_arp)
        # )
        #
        # flow_reverse_arp = {
        #   'switch':'00:00:00:00:00:00:00:01',
        #   'name': 'flow-{0}-reverse-arp'.format(flow_index),
        #   "ether-type":"0x806",
        #   "src-ip":"10.0.0.2",
        #   "dst-ip":"10.0.0.1",
        #   'cookie': str(flow_cookie),
        #   'priority':'2',
        #   'ingress-port':'2',
        #   'active':'true',
        #   'actions':'output=1'
        # }
        # response = requests.post(
        #   'http://localhost:8080/wm/staticentrypusher/json',
        #   data=json.dumps(flow_reverse_arp)
        # )

        flow_cookie += 1

    print('- ' + str(num_flows) + ' flows added.')


def deleteFlows(num_flows):
    for flow_index in range(0, num_flows):
        for flow_type in ['forward', 'forward-arp', 'reverse', 'reverse-arp']:
            flow = {
                'name': 'flow-{0}-{1}'.format(flow_index,flow_type)
            }
            response = requests.delete(
              'http://localhost:8080/wm/staticentrypusher/json',
              data=json.dumps(flow)
            )
