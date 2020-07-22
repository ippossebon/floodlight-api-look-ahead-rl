def rulesToLink(switch_address, out_port):
    if switch_address == '00:00:00:00:00:00:00:01':
        if out_port == 2:
            return 'b'
        if out_port == 3:
            return 'c'
        else: # erro
            return None

    if switch_address == '00:00:00:00:00:00:00:02':
        if out_port == 2:
            return 'e'
        if out_port == 3:
            return 'd'
        if out_port == 4:
            return 'f'
        else: # erro
            return None

    if switch_address == '00:00:00:00:00:00:00:03':
        if out_port == 1:
            return 'i'
        else: # erro
            return None

    if switch_address == '00:00:00:00:00:00:00:04':
        if out_port == 2:
            return 'e'
        if out_port == 3:
            return 'g'
        else: # erro
            return None

    if switch_address == '00:00:00:00:00:00:00:05':
        if out_port == 2:
            return 'h'
        else: # erro
            return None
