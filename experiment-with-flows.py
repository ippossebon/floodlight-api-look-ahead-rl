from utilities.staticEntryPusher import StaticEntryPusher


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

flow3 = {
    'switch':'00:00:00:00:00:00:00:01',
    'name':'flow_3',
    'cookie':'0',
    'priority':'32768',
    'in_port':'1',
    'active':'true',
    'actions':'output=2'
}

flow4 = {
    'switch':'00:00:00:00:00:00:00:01',
    'name':'flow_4',
    'cookie':'0',
    'priority':'32768',
    'in_port':'1',
    'active':'true',
    'actions':'output=2'
}

flow5 = {
    'switch':'00:00:00:00:00:00:00:01',
    'name':'flow_5',
    'cookie':'0',
    'priority':'32768',
    'in_port':'1',
    'active':'true',
    'actions':'output=2'
}

pusher.set(flow1)
pusher.set(flow2)
pusher.set(flow3)
pusher.set(flow4)
pusher.set(flow5)

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
