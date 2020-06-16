import gym
import load_balance_gym

from agent.DQNAgent import DQNAgent

# initial_usage = [
#     700,    # A
#     700,    # B
#     0,      # C
#     0,      # D
#     0,      # E
#     700,    # F
#     0,      # G
#     0,      # H
#     700     # I
# ]


class LoadBalanceAgent():
    def __init__(self, initial_usage, num_episodes=100, max_it=100):
        self.initial_usage = initial_usage
        self.env = gym.make('Load-Balance-v1', usage=initial_usage)
        self.agent = agent = DQNAgent(self.env)
        self.max_it = max_it


    def train():
        active_flows = ['F1', 'F2']
        flow_sizes = {
            'F1': 200,
            'F2': 500
        }
        flow_paths = {
            'F1': [['A', 'B', 'F', 'I']],
            'F2': [['A', 'B', 'F', 'I']]
        }
        
        for ep in range(self.num_episodes):
            state = self.env.reset()
            # done = False
            total_reward = float(0)
            iteraction = 0

            while iteraction < self.max_it:
                action = self.agent.getAction(state)
                # print('--> Action = ', action)

                flow_to_reroute = 'F2'
                flow_to_reroute_size = flow_sizes[flow_to_reroute]
                flow_to_reroute_paths = flow_paths[flow_to_reroute]

                next_state, reward, done, info = self.env.step(
                    action=action,
                    flow_total_size=flow_to_reroute_size,
                    flow_current_paths=flow_to_reroute_paths
                )

                # Atualiza informações do fluxo
                flow_paths[flow_to_reroute] = info['next_paths']

                # print('--> next_state = ', next_state)
                # print('--> reward = ', reward)
                # print('-------------------------')

                self.agent.train(state, action, next_state, reward, done)

                total_reward += reward
                state = next_state
                iteraction += 1

            print('[Training] Episode: {}, total_reward: {:.2f}'.format(ep, total_reward))
