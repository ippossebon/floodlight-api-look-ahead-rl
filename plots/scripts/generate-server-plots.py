from parseServerIperfData import generateServerCSVs

import pandas as pd
import numpy as np

import matplotlib.pyplot as plt

filenames = [
    '../../experiments-data/A1-2-flows/server-5201-2flows',
    '../../experiments-data/A1-2-flows/server-5202-2flows'
]
generateServerCSVs(filenames)

colors = ['yellow', 'orange', 'red', 'blue', 'purple']
index_data = 0
plt.figure(figsize=(10,7))

for filenamne in filenames:
    filename_csv = filenamne + '.csv'
    dataframe = pd.read_csv(filename_csv, delimiter=';')
    dataframe_scaled = dataframe.iloc[::21, :]

    plt.plot(
        dataframe_scaled['Timestep'],
        dataframe_scaled['Bandwidth (Mbps)'],
        color=colors[index_data]
    )
    index_data = index_data + 1

plt.xlabel('Time step')
plt.ylabel('Bandwidth (Mbps)')
# plt.ylim(top=100)
# plt.show()
plt.savefig('../../experiments-data/A1-2-flows/bandwidth-servers.pdf')
