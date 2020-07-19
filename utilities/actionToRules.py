MAX_PRIORITY = "32768"

def getRule(source_link, target_link, flow_name, priority=None):
    priority = priority or MAX_PRIORITY

    if source_link == 'a':
        if target_link == 'b':
            return {
                "switch": switch_ids["S1"],
                "name": flow_name,
                "priority": priority,
                "ingress-port": "1",
                "active": "true",
                "actions": "output=2"
            }
        elif target_link == 'c':
            return {
                "switch": switch_ids["S1"],
                "name": flow_name,
                "priority": priority,
                "ingress-port": "1",
                "active": "true",
                "actions": "output=3"
            }
        else:
            return None
    elif source_link == 'b':
        if target_link == 'd':
            return {
                "switch": switch_ids["S2"],
                "name": flow_name,
                "priority": priority,
                "ingress-port": "1",
                "active": "true",
                "actions": "output=3"
            }
        elif target_link == 'e':
            return {
                "switch": switch_ids["S2"],
                "name": flow_name,
                "priority": priority,
                "ingress-port": "1",
                "active": "true",
                "actions": "output=2"
            }
        elif and target_link == 'f'
            return {
                "switch": switch_ids["S2"],
                "name": flow_name,
                "priority": priority,
                "ingress-port": "1",
                "active": "true",
                "actions": "output=4"
            }
        else:
            return None
    elif source_link == 'c':
        if target_link == 'e':
            return {
                "switch": switch_ids["S4"],
                "name": flow_name,
                "priority": priority,
                "ingress-port": "1",
                "active": "true",
                "actions": "output=2"
            }
        if target_link == 'g':
            return {
                "switch": switch_ids["S4"],
                "name": flow_name,
                "priority": priority,
                "ingress-port": "1",
                "active": "true",
                "actions": "output=3"
            }
        else:
            return None
    elif source_link == 'd':
        if target_link == 'h':
            return {
                "switch": switch_ids["S5"],
                "name": flow_name,
                "priority": priority,
                "ingress-port": "1",
                "active": "true",
                "actions": "output=2"
            }
        else:
            return None
    elif source_link == 'e':
        if target_link == 'd':
            return {
                "switch": switch_ids["S2"],
                "name": flow_name,
                "priority": priority,
                "ingress-port": "2",
                "active": "true",
                "actions": "output=3"
            }
        if target_link == 'f':
            return {
                "switch": switch_ids["S2"],
                "name": flow_name,
                "priority": priority,
                "ingress-port": "2",
                "active": "true",
                "actions": "output=4"
            }

        if target_link == 'g':
            return {
                "switch": switch_ids["S4"],
                "name": flow_name,
                "priority": priority,
                "ingress-port": "2",
                "active": "true",
                "actions": "output=3"
            }
        if target_link == 'i':
            return {
                "switch": switch_ids["S3"],
                "name": flow_name,
                "priority": priority,
                "ingress-port": "2",
                "active": "true",
                "actions": "output=1"
            }
        else:
            return None
    elif source_link == 'g':
        if  target_link == 'i':
            return {
                "switch": switch_ids["S3"],
                "name": flow_name,
                "priority": priority,
                "ingress-port": "3",
                "active": "true",
                "actions": "output=1"
            }
        else:
            return None
    elif source_link == 'h':
        if target_link == 'i':
            return {
                "switch": switch_ids["S3"],
                "name": flow_name,
                "priority": priority,
                "ingress-port": "4",
                "active": "true",
                "actions": "output=1"
            }
        else:
            return None

"""
Input:

Output: {
    "switch": "00:00:00:00:00:00:00:01",
    "name":"flow-mod-1",
    "priority":"32768",
    "ingress-port":"1",
    "active":"true",
    "actions":"output=2"
}

How to test:
curl -d '{
    "switch": "00:00:00:00:00:00:00:01",
    "name":"flow-mod-1",
    "priority":"32768",
    "ingress-port":"1",
    "active":"true",
    "actions":"output=2"
}'
"""
# Retorna fixed_rules, loop_rules
def actionToRules(action, current_paths, flow_name, switch_ids):

    if action == 0:
        # should keep everything as it is
        return []
    elif action == 1:
        # half of the flow to [a, c, g, i] and the other half to [a, b, f, i]
        # Pra dividir o fluxo entre dois caminhos, será necessário:

        # Instalar regra que leva de a pra b. Sleep 2 segundos. Instala regra de a pra c, com maior prioridade
        # Só é necessário ficar sobrescrevendo as regras do switch 1 - pois é o switch que faz o split.
        loop_rules = [] # regras pelas quais vamos precisar intercalar entre intervalos, pra que o fluxo seja dividido
        # TODO: checar se usar sempre a mesma prioridade e ficar sobrescrevendo as regras funciona (precisamos remover a anterior). Se não funcionar,
        # devemos usar diferenes prioridades e definir o tempo correto de sleep, sabendo que só vamos fazer isso para elephant flows.
        loop_rules.append(getRule(source_link='a', target_link='b', flow_name=flow_name), priority=MAX_PRIORITY-1)
        loop_rules.append(getRule(source_link='a', target_link='c', flow_name=flow_name), priority=MAX_PRIORITY-1)

        fixed_rules = []
        fixed_rules.append(getRule(source_link='c', target_link='g', flow_name=flow_name))
        fixed_rules.append(getRule(source_link='g', target_link='i', flow_name=flow_name))
        fixed_rules.append(getRule(source_link='b', target_link='f', flow_name=flow_name))
        fixed_rules.append(getRule(source_link='f', target_link='i', flow_name=flow_name))

        return fixed_rules, loop_rules

    elif action == 2:
        # half of the flow to [a, b, d, h, i] and the other half to [a, b, e, g, i]

        # Instalar regra que leva de b pra d. Sleep 2 segundos. Instala regra de b pra e, com maior prioridade
        # Só é necessário ficar sobrescrevendo as regras do switch 2 - pois é o switch que faz o split.
        loop_rules = [] # regras pelas quais vamos precisar intercalar entre intervalos, pra que o fluxo seja dividido
        loop_rules.append(getRule(source_link='b', target_link='d', flow_name=flow_name))
        loop_rules.append(getRule(source_link='b', target_link='e', flow_name=flow_name))

        fixed_rules = []
        fixed_rules.append(getRule(source_link='a', target_link='b', flow_name=flow_name))
        fixed_rules.append(getRule(source_link='d', target_link='h', flow_name=flow_name))
        fixed_rules.append(getRule(source_link='h', target_link='i', flow_name=flow_name))
        fixed_rules.append(getRule(source_link='e', target_link='g', flow_name=flow_name))
        fixed_rules.append(getRule(source_link='g', target_link='i', flow_name=flow_name))

        return fixed_rules, loop_rules

    elif action == 3:
        # route the flow to [a, b, f, i]
        rules = []
        rules.append(getRule(source_link='a', target_link='b', flow_name=flow_name))
        rules.append(getRule(source_link='b', target_link='f', flow_name=flow_name))
        rules.append(getRule(source_link='f', target_link='i', flow_name=flow_name))

        return rules

    elif action == 4:
        # half of the flow to [a, c, g, i] and the other half to [a, c, e, f, i]

        # Instalar regra que leva de c pra g. Sleep 2 segundos. Instala regra de c pra e, com maior prioridade
        # Só é necessário ficar sobrescrevendo as regras do switch 4 - pois é o switch que faz o split.
        loop_rules = [] # regras pelas quais vamos precisar intercalar entre intervalos, pra que o fluxo seja dividido
        loop_rules.append(getRule(source_link='c', target_link='g', flow_name=flow_name))
        loop_rules.append(getRule(source_link='c', target_link='e', flow_name=flow_name))

        fixed_rules = []
        fixed_rules.append(getRule(source_link='a', target_link='c', flow_name=flow_name))
        fixed_rules.append(getRule(source_link='g', target_link='i', flow_name=flow_name))
        fixed_rules.append(getRule(source_link='e', target_link='f', flow_name=flow_name))
        fixed_rules.append(getRule(source_link='f', target_link='i', flow_name=flow_name))

        return fixed_rules, loop_rules

    elif action == 5:
        # route the flow to [a, c, g, i]
        rules = []
        rules.append(getRule(source_link='a', target_link='c', flow_name=flow_name))
        rules.append(getRule(source_link='c', target_link='g', flow_name=flow_name))
        rules.append(getRule(source_link='g', target_link='i', flow_name=flow_name))

    elif action == 6:
        # oute the flow to [a, b, d, h, i]
        rules = []
        rules.append(getRule(source_link='a', target_link='b', flow_name=flow_name))
        rules.append(getRule(source_link='b', target_link='d', flow_name=flow_name))
        rules.append(getRule(source_link='d', target_link='h', flow_name=flow_name))
        rules.append(getRule(source_link='h', target_link='i', flow_name=flow_name))

        return rules

    elif action == 7:
        # route the flow to [a, b, e, g, i]
        rules = []
        rules.append(getRule(source_link='a', target_link='b', flow_name=flow_name))
        rules.append(getRule(source_link='b', target_link='e', flow_name=flow_name))
        rules.append(getRule(source_link='e', target_link='g', flow_name=flow_name))
        rules.append(getRule(source_link='g', target_link='i', flow_name=flow_name))

        return rules

    elif action == 8:
        # route the flow to [a, c, e, d, h, i]
        rules = []
        rules.append(getRule(source_link='a', target_link='c', flow_name=flow_name))
        rules.append(getRule(source_link='c', target_link='e', flow_name=flow_name))
        rules.append(getRule(source_link='e', target_link='d', flow_name=flow_name))
        rules.append(getRule(source_link='d', target_link='h', flow_name=flow_name))
        rules.append(getRule(source_link='h', target_link='i', flow_name=flow_name))

        return rules

    elif action == 9:
        # route the flow to [a, c, e, f, i]
        rules = []
        rules.append(getRule(source_link='a', target_link='c', flow_name=flow_name))
        rules.append(getRule(source_link='c', target_link='e', flow_name=flow_name))
        rules.append(getRule(source_link='e', target_link='f', flow_name=flow_name))
        rules.append(getRule(source_link='f', target_link='i', flow_name=flow_name))

        return rules

    elif action == 10:
        # route 1/3 of the flow to [a, b, d, h, i], 1/3 to [a, b, e, g, i], and 1/3 to [a, b, f, i]

        # Instalar regra que leva de b pra d. Sleep 2 segundos. Instala regra de b pra f, com maior prioridade. Sleep 2 segundos. Instala regra de b pra e, com maior prioridade.
        # Só é necessário ficar sobrescrevendo as regras do switch 2 - pois é o switch que faz o split.
        loop_rules = [] # regras pelas quais vamos precisar intercalar entre intervalos, pra que o fluxo seja dividido
        loop_rules.append(getRule(source_link='b', target_link='d', flow_name=flow_name))
        loop_rules.append(getRule(source_link='b', target_link='f', flow_name=flow_name))
        loop_rules.append(getRule(source_link='b', target_link='e', flow_name=flow_name))

        fixed_rules = []
        fixed_rules.append(getRule(source_link='a', target_link='b', flow_name=flow_name))
        fixed_rules.append(getRule(source_link='d', target_link='h', flow_name=flow_name))
        fixed_rules.append(getRule(source_link='h', target_link='i', flow_name=flow_name))
        fixed_rules.append(getRule(source_link='e', target_link='g', flow_name=flow_name))
        fixed_rules.append(getRule(source_link='g', target_link='i', flow_name=flow_name))
        fixed_rules.append(getRule(source_link='f', target_link='i', flow_name=flow_name))

        return fixed_rules, loop_rules
