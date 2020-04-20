import gym
import load_balance_gym

from agent.DQNAgent import DQNAgent
from agent.QNAgent import QNAgent

initial_usage = [
    700,    # A
    700,    # B
    0,      # C
    0,      # D
    0,      # E
    700,    # F
    0,      # G
    0,      # H
    700     # I
]

env = gym.make('Load-Balance-v1', usage=initial_usage)
print('----------> Starting Environment <----------')
print('--> Observation space ', env.observation_space)
print('--> Action space', env.action_space)

num_episodes = 100

agent = DQNAgent(env)
# qn_agent = QNAgent(env)


active_flows = ['F1', 'F2']
flow_sizes = {
    'F1': 200,
    'F2': 500
}
flow_paths = {
    'F1': [['A', 'B', 'F', 'I']],
    'F2': [['A', 'B', 'F', 'I']]
}

for ep in range(num_episodes):
    state = env.reset()
    total_reward = 0
    done = False

    while not done:
        print('--> State = ', state)

        action = agent.getAction(state)
        print('--> Action = ', action)

        flow_to_reroute = 'F2'
        flow_to_reroute_size = flow_sizes[flow_to_reroute]
        flow_to_reroute_paths = flow_paths[flow_to_reroute]

        next_state, reward, done, info = env.step(
            action=action,
            flow_total_size=flow_to_reroute_size,
            flow_current_paths=flow_to_reroute_paths
        )

        # Atualiza informações do fluxo
        flow_paths[flow_to_reroute] = info['next_paths']

        print('--> next_state = ', next_state)
        print('--> reward = ', reward)
        print('-------------------------')

        agent.train(state, action, next_state, reward, done)

        total_reward += reward
        state = next_state

    print('Episode: {}, total_reward: {:.2f}'.format(ep, total_reward))
