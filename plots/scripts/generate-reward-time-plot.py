import pandas as pd
import numpy as np

import matplotlib.pyplot as plt

from parseAppOutput import parseAppOutput

filename =  '../../experiments-data/A1-2-flows/A1-2flows'

parsed_filename = parseAppOutput(filename)

df = pd.read_csv(parsed_filename, delimiter=';')

df.plot(kind='line', x='Step', y='Reward', color='coral', title='Reward value over time')

plt.xlabel('Step')
plt.ylabel('Reward')

plt.savefig('../../experiments-data/A1-2-flows/A1-2-reward.pdf')
