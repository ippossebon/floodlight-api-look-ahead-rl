import gym
import load_balance_gym

# initial_usage = {
#     'A': 100,
#     'B': 50,
#     'C': 10,
#     'D': 30,
#     'E': 100,
#     'F': 20,
#     'G': 90,
#     'H': 60,
#     'I': 10
# }

initial_usage = {
    'A': 0,
    'B': 0,
    'C': 0,
    'D': 0,
    'E': 0,
    'F': 0,
    'G': 0,
    'H': 0,
    'I': 0
}
env = gym.make('Load-Balance-v1', usage=initial_usage)

obs = env.reset()
n_steps = 10

print('env.action_space', env.action_space)

for step in range(n_steps):
    # Random action
    print('step = ', step)

    action = env.action_space.sample()
    print('action = ', action)

    state, reward, done, info = env.step(action)
    print('state = ', state)
    print('reward = ', reward)
