"""
No max, 8 iperfs simultaneos = 16 fluxos

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
        action, _ = agent.predict(state)
        state, reward, done, info = env.step(action) #= regra (IN, OUT, SWITCH) + flow_match
    else:
        continue


def reward(state, flow_for_action):
    # Como olhar para o meu estado e penalizar decisões que mexem em fluxos que não são EF?
    # Com a equação aqui descrita, não precisaria de um IF EF pré agente,
    # pois qualquer ação que não envolva um EF, independente de qual seja, não será escolhida
    # pelo agente por conta da recompensa.
    elephant_flows = getActiveElephantFlows()
    chosen_flow_is_elephant = False

    for ef in elephant_flows:
        if ef == flow_for_action:
            chosen_flow_is_elephant = True

    if not chosen_flow_is_elephant:
        # recompensa deve ser muito baixa, para penalizar o agente
        return MIN_LA_REWARD
    else:
        # escolheu EF para action
        hmean = getHMeanReward(state)
        reward = hmean + ELEPHANT_FLOW_REWARD_FACTOR
        return reward


def step(action):
    done = False # Aprendizado continuado
    next_state = []
    reward = 0
    info = {}

    if action == 33:
        next_state = getState()
        reward = MIN_LA_REWARD
        return next_state, reward, done, info
    else:
        flow_match, rule = actionWithFlowMap(action)
        rule_to_install = generateRule(flow_match, rule)

        installRule(rule_to_install)

        time.sleep(7) # aguarda regras refletirem e pacotes serem enviados novamente

        next_state = getState()
        reward = calculateReward(next_state, flow_match)
        state = next_state

        return next_state, reward, done, info


def testAgent(env, original_env, agent, timesteps):
    model = DQN.load(load_path=agent, env=env)
    state = env.reset()

    for step in range(num_steps):
        action, _ = model.predict(state)
        state, reward, done, info = env.step(action)
        step += 1
