import gym
import load_balance_gym

from agent.DQNAgent import DQNAgent

initial_usage = [
    200,    # A
    200,    # B
    0,      # C
    0,      # D
    0,      # E
    200,    # F
    0,      # G
    0,      # H
    200     # I
]

env = gym.make('Load-Balance-v1', usage=initial_usage)
print('----------> Starting Environment <----------')
print('--> Observation space ', env.observation_space)
print('--> Action space', env.action_space)

num_episodes = 100

agent = DQNAgent(env)


for ep in range(num_episodes):
    state = env.reset()
    total_reward = 0
    done = False
    while not done:
        print('--> State = ', state)

        action = agent.getAction(state)
        print('--> Action = ', action)

        next_state, reward, done, info = env.step(action)
        print('--> next_state = ', next_state)
        print('--> reward = ', reward)
        print('-------------------------')


        agent.train(state, action, next_state, reward, done)

        total_reward += reward
        state = next_state

    print('Episode: {}, total_reward: {:.2f}'.format(ep, total_reward))

# for episode in range(num_episodes):
#     # Random action
#     print('episode = ', episode)
#
#     action = env.action_space.sample()
#     print('action = ', action)
#
#     state, reward, done, info = env.step(action)
#     print('state = ', state)
#     print('reward = ', reward)
