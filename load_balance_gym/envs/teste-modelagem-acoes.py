def generateNextState(self, total_usage, action_to_apply, flow_index): # switch_array_index
    # Atualiza estado com base na ação que foi escolhida
    next_state = list(self.usage)
    next_paths = []

    # Pega os caminhos anteriores utilizados, para atulizar o estado
    previous_paths = self.flow_paths[flow_id]

    # Zera utilização anterior
    next_state = self.resetPreviousPathsUsage(previous_paths)

    if action_to_apply == 1:
        # split de fluxo em S1
        next_paths.append(['a', 'c', 'g', 'i'])
        next_paths.append(['a', 'b', 'f', 'i'])

        next_state[0] = flow_size # A
        next_state[1] = flow_size/2 # B
        next_state[2] = flow_size/2 # C
        next_state[5] = flow_size/2 # F
        next_state[6] = flow_size/2 # G
        next_state[8] = flow_size # I

    elif action_to_apply == 2:
        # split de fluxo em S2
        next_paths.append(['a', 'b', 'd', 'h', 'i'])
        next_paths.append(['a', 'b', 'e', 'G', 'i'])

        next_state[0] = flow_size # A
        next_state[1] = flow_size # B
        next_state[3] = flow_size/2 # D
        next_state[4] = flow_size/2 # E
        next_state[6] = flow_size/2 # G
        next_state[7] = flow_size/2 # H
        next_state[8] = flow_size # I

    elif action_to_apply == 3:
        next_paths.append(['a', 'b', 'f', 'i'])

        next_state[0] = flow_size # A
        next_state[1] = flow_size # B
        next_state[5] = flow_size # F
        next_state[8] = flow_size # I

    elif action_to_apply == 4:
        # split de fluxo em S4
        next_paths.append(['a', 'c', 'g', 'i'])
        next_paths.append(['a', 'c', 'e', 'f', 'i'])

        next_state[0] = flow_size # A
        next_state[2] = flow_size # C
        next_state[4] = flow_size/2 # E
        next_state[5] = flow_size/2 # F
        next_state[6] = flow_size/2 # G
        next_state[8] = flow_size # I

    elif action_to_apply == 5:
        next_paths.append(['a', 'c', 'g', 'i'])

        next_state[0] = flow_size # A
        next_state[2] = flow_size # C
        next_state[6] = flow_size # G
        next_state[8] = flow_size # I

    elif action_to_apply == 6:
        next_paths.append(['a', 'b', 'd', 'h', 'i'])

        next_state[0] = flow_size # A
        next_state[1] = flow_size # B
        next_state[3] = flow_size # D
        next_state[7] = flow_size # H
        next_state[8] = flow_size # I

    elif action_to_apply == 7:
        next_paths.append(['a', 'b', 'e', 'g', 'i'])

        next_state[0] = flow_size # A
        next_state[1] = flow_size # B
        next_state[4] = flow_size # E
        next_state[6] = flow_size # G
        next_state[8] = flow_size # I

    elif action_to_apply == 8:
        next_paths.append(['a', 'c', 'e', 'd', 'h', 'i'])

        next_state[0] = flow_size # A
        next_state[2] = flow_size # C
        next_state[3] = flow_size # D
        next_state[4] = flow_size # E
        next_state[7] = flow_size # H
        next_state[8] = flow_size # I

    elif action_to_apply == 9:
        next_paths.append(['a', 'c', 'e', 'f', 'i'])

        next_state[0] = flow_size # A
        next_state[2] = flow_size # C
        next_state[4] = flow_size # E
        next_state[5] = flow_size # F
        next_state[8] = flow_size # I

    else:
        print ('Error: invalid action type [generateNextState]: ', action_to_apply)
        exit(0)

    next_paths_index = []
    for path in next_paths:
        path_index = self.getPathIndex(path)
        next_paths_index.append(path_index)

    # Altera caminhos utilizados pelo fluxo
    flow_id = self.active_flows[flow_index]
    self.flow_paths[flow_id] = list(next_paths_index)

    return next_state


def resetPreviousPathsUsage(self, previous_paths):
    new_usage = list(self.usage)
    for path in previous_paths:
        for link in path:
            link_index = self.getLinkIndex(link)
            new_usage[link_index] = 0

    return new_usage
