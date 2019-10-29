import gym
import json
import datetime as dt
import pandas as pd

from stable_baselines.common.policies import MlpPolicy
from stable_baselines.common.vec_env import DummyVecEnv
from stable_baselines import PPO2
from loadBalanceEnv import LoadBalanceEnv


dataframe = pd.read_csv('./data/AAPL.csv')
dataframe = dataframe.sort_values('Date')

# The algorithms require a vectorized environment to run
env = DummyVecEnv([lambda: LoadBalanceEnv(dataframe)])

model = PPO2(MlpPolicy, env, verbose=1)
model.learn(total_timesteps=20000)

obs = env.reset()

for i in range(2000):
    action, _states = model.predict(obs)
    obs, rewards, done, info = env.step(action)
    env.render()
