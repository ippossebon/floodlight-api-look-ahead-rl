import pandas as pd
import numpy as np

import matplotlib.pyplot as plt

df = pd.read_csv('./data/output-app-15-set-1.csv', delimiter=';')

df.plot(kind='line', x='Step', y='Reward', color='blue', title='Reward value over time')

plt.xlabel('Step')
plt.ylabel('Reward')

plt.savefig('./images/reward-x-time-15-set-1.pdf')
