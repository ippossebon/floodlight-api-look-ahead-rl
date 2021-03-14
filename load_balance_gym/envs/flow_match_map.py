import numpy

# 46110_to_5201
# 46112_to_5202
# 46114_to_5203
# 46116_to_5204
# 46118_to_5205
# 46120_to_5206
# 46122_to_5207
# 46124_to_5208


def flowMap(flow_index):
    # 46110_to_5201
    if flow_index == 0:
        return {
            'ipv4_src': '10.0.0.1',
            'ipv4_dst': '10.0.0.2',
            'tcp_src': '46110',
            'tcp_dst': '5201'
        }

    # 46112_to_5202
    elif flow_index == 1:
        return {
            'ipv4_src': '10.0.0.1',
            'ipv4_dst': '10.0.0.2',
            'tcp_src': '46112',
            'tcp_dst': '5202'
        }

    # 46114_to_5203
    elif flow_index == 2:
        return {
            'ipv4_src': '10.0.0.1',
            'ipv4_dst': '10.0.0.2',
            'tcp_src': '46114',
            'tcp_dst': '5203'
        }

    # 46116_to_5204
    elif flow_index == 3:
        return {
            'ipv4_src': '10.0.0.1',
            'ipv4_dst': '10.0.0.2',
            'tcp_src': '46116',
            'tcp_dst': '5204'
        }
    # 46118_to_5205
    elif flow_index == 4:
        return {
            'ipv4_src': '10.0.0.1',
            'ipv4_dst': '10.0.0.2',
            'tcp_src': '46118',
            'tcp_dst': '5205'
        }

    # 46120_to_5206
    elif flow_index == 5:
        return {
            'ipv4_src': '10.0.0.1',
            'ipv4_dst': '10.0.0.2',
            'tcp_src': '46120',
            'tcp_dst': '5206'
        }

    # 46122_to_5207
    elif flow_index == 6:
        return {
            'ipv4_src': '10.0.0.1',
            'ipv4_dst': '10.0.0.2',
            'tcp_src': '46122',
            'tcp_dst': '5207'
        }

    # 46124_to_5208
    elif flow_index == 7:
        return {
            'ipv4_src': '10.0.0.1',
            'ipv4_dst': '10.0.0.2',
            'tcp_src': '46124',
            'tcp_dst': '5208'
        }

    # 5201_to_46110
    elif flow_index == 8:
        return {
            'ipv4_src': '10.0.0.2',
            'ipv4_dst': '10.0.0.1',
            'tcp_src': '5201',
            'tcp_dst': '46110'
        }

    # 5202_to_46112
    elif flow_index == 9:
        return {
            'ipv4_src': '10.0.0.2',
            'ipv4_dst': '10.0.0.1',
            'tcp_src': '5202',
            'tcp_dst': '46112'
        }

    # 5203_to_46114
    elif flow_index == 10:
        return {
            'ipv4_src': '10.0.0.2',
            'ipv4_dst': '10.0.0.1',
            'tcp_src': '5203',
            'tcp_dst': '46114'
        }

    # 5204_to_46116
    elif flow_index == 11:
        return {
            'ipv4_src': '10.0.0.2',
            'ipv4_dst': '10.0.0.1',
            'tcp_src': '5204',
            'tcp_dst': '46116'
        }

    # 5205_to_46118
    elif flow_index == 12:
        return {
            'ipv4_src': '10.0.0.2',
            'ipv4_dst': '10.0.0.1',
            'tcp_src': '5205',
            'tcp_dst': '46118'
        }

    # 5206_to_46120
    elif flow_index == 13:
        return {
            'ipv4_src': '10.0.0.2',
            'ipv4_dst': '10.0.0.1',
            'tcp_src': '5206',
            'tcp_dst': '46120'
        }

    # 5207_to_46122
    elif flow_index == 14:
        return {
            'ipv4_src': '10.0.0.2',
            'ipv4_dst': '10.0.0.1',
            'tcp_src': '5207',
            'tcp_dst': '46122'
        }

    # 5208_to_46124
    elif flow_index == 15:
        return {
            'ipv4_src': '10.0.0.2',
            'ipv4_dst': '10.0.0.1',
            'tcp_src': '5208',
            'tcp_dst': '46124'
        }
