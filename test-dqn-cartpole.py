
import gym
from agent.DQNAgent import DQNAgent



env_name = "CartPole-v0"
env = gym.make(env_name)

agent = DQNAgent(env)
num_episodes = 400

for ep in range(num_episodes):
    state = env.reset()
    total_reward = 0
    done = False
    while not done:
        action = agent.getAction(state)
        print('state', state)
        next_state, reward, done, info = env.step(action)
        agent.train(state, action, next_state, reward, done)
        total_reward += reward
        state = next_state

    # print("Episode: {}, total_reward: {:.2f}".format(ep, total_reward))
