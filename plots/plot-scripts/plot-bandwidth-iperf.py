import pandas as pd
import numpy as np

import matplotlib.pyplot as plt

fig, axes = plt.subplots(2)

df_client1 = pd.read_csv('./data/teste-1-A1_v2/46110-A1_v2.txt', delimiter=';')
df_client2 = pd.read_csv('./data/teste-1-A1_v2/46112-A1_v2.txt', delimiter=';')
df_client3 = pd.read_csv('./data/teste-1-A1_v2/46114-A1_v2.txt', delimiter=';')
df_client4 = pd.read_csv('./data/teste-1-A1_v2/46116-A1_v2.txt', delimiter=';')
df_client5 = pd.read_csv('./data/teste-1-A1_v2/46118-A1_v2.txt', delimiter=';')

df_colors = {
    df_client1: 'yellow',
    df_client2: 'orange',
    df_client3: 'red',
    df_client4: 'blue',
    df_client5: 'purple'
}

for frame in [df_client1, df_client2, df_client3, df_client4, df_client5]:
    plt.plot(x=frame['Timestep'], y=frame['Bandwidth (Mbps)'], color=df_colors[df_client1], linewidth=2)

## Client
# df.plot(
#     kind='line',
#     x='Timestep',
#     y='Bandwidth (Mbps)',
#     color='red',
#     title='Clients Bandwidth over time',
#     ax=axes[0]
# )
#
#
# ## Server
# df2.plot(
#     kind='line',
#     x='Timestep',
#     y='Bandwidth (Mbps)',
#     color='green',
#     title='Servers Bandwidth over time',
#     ax=axes[1]
# )

plt.xlabel('Time step')
plt.ylabel('Bandwidth (Mbps)')

plt.savefig('./images/A1_v2-clients.pdf')
