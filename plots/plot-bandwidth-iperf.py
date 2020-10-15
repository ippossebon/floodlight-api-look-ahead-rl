import pandas as pd
import numpy as np

import matplotlib.pyplot as plt

fig, axes = plt.subplots(2)

df = pd.read_csv('./data/server-iperf-data.csv', delimiter=';')
df2 = pd.read_csv('./data/server-iperf-data-2.csv', delimiter=';')

df.plot(
    kind='line',
    x='Timestep',
    y='Bandwidth (Mbps)',
    color='red',
    title='Bandwidth over time',
    ax=axes[0]
)

df2.plot(
    kind='line',
    x='Timestep',
    y='Bandwidth (Mbps)',
    color='green',
    title='Bandwidth over time',
    ax=axes[1]
)

plt.xlabel('Time step')
plt.ylabel('Bandwidth (Mbps)')

plt.savefig('./images/server-iperf-data-2.pdf')
