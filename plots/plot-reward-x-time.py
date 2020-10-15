import pandas as pd
import numpy as np

import matplotlib.pyplot as plt

df = pd.read_csv('./teste-app.csv', delimiter=';')

df.plot(kind='line', x='Step', y='Reward', color='blue', title='Reward value over time')

plt.xlabel('Step')
plt.ylabel('Reward')

plt.savefig('./images/teste-reward-x-time.pdf')
