import pandas as pd
import numpy as np

import matplotlib.pyplot as plt

from parseAppOutput import parseAppOutput

filename =  '../../experiments-data/A1-10-flows/A1-10flows'

parsed_filename = parseAppOutput(filename)

df = pd.read_csv('../../experiments-data/A1-10-flows/A1-10flows-parsed.csv', delimiter=';')

df.plot(kind='line', x='Step', y='Reward', color='coral', title='Reward value over time')

plt.xlabel('Step')
plt.ylabel('Reward')

plt.savefig('../../experiments-data/A1-10-flows/A1-10-reward.pdf')
