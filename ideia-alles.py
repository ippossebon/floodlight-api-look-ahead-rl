state = env.reset()

state = [link_A_usage, link_B_usage, ...] # 16 links
action = 544 # SWITCH, IN, OUT (34) + FLOW_INDEX (16)

"""
No max, 8 iperfs simultaneos = 16 fluxos
"""



"""
Fluxos que podemos considerar ativos (máximo de 8 simultaneos)
46110 -> 5201
46112 -> 5202
46114 -> 5203
46116 -> 5204
46118 -> 5205
46120 -> 5206
46122 -> 5207
46124 -> 5208

5201 -> 46110
5202 -> 46112
5203 -> 46114
5204 -> 46116
5205 -> 46118
5206 -> 46120
5207 -> 46122
5208 -> 46124
"""
#        A,  B,    C,  D,   E, F
state = [0, 100, 100, 100, 0, 0]
active_flows = [F1, F2, F3]

for flow in active_flows:
    if isElephantFlow(flow):
        # nao preciso indicar sobre qual fluxo atuar pois a funçao de recompensa vai penalizar escolhas que envolvem mice flows
        # e dar grandes recompensas a ações com EF

        action, _ = agent.predict(state, deterministic=False)
        state, reward, done, info = env.step(action)
    else:
        continue


# active_flows tem 16 posicões (16 fluxos)
# 20M, 40M, 50M, 100M, 200M, 400M, 500M, 1024M
def reward(state, action, active_flows):
    # como olhar para o meu estado e penalizar decisões que mexem em fluxos que não são EF?
    # com esses dados, consigo resolver.



    # se o agente escolher um fluxo que já terminou, o estado se mantem o mesmo



def step(action):
    action_vec = actionFlowMap(action_rule)

    switch_index = action_vec[0]
    in_port_index = action_vec[1]
    out_port_index = action_vec[2]
    flow_index = action_vec[3]

    switch_id = self.switch_ids[switch_index]
    in_port = in_port_index + 1
    out_port = out_port_index + 1
    flow_match = flowMap(flow_index)

    rule_to_install = self.actionToRule(switch_id, in_port, out_port, flow_match)

    existing_rule_name = self.existsRuleWithAction(switch_id, in_port, out_port, flow_match)

    if existing_rule_name:
        response_uninstall = self.uninstallRule(existing_rule_name)

    response_install = self.installRule(rule_to_install)

    time.sleep(7) # aguarda regras refletirem e pacotes serem enviados novamente

    next_state = self.getState()
    reward = self.calculateReward(next_state, action)
