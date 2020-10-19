from parseClientIperfData import generateClientCSVs
from parseServerIperfData import generateServerCSVs

import pandas as pd
import numpy as np

import matplotlib.pyplot as plt

client_filenames = [
    '../../experiments-data/A1-2-flows/client-46110-A1-2flows',
    '../../experiments-data/A1-2-flows/client-46112-A1-2flows'
]
generateClientCSVs(client_filenames)


server_filenames = [
    '../../experiments-data/A1-2-flows/server-5201-A1-2flows',
    '../../experiments-data/A1-2-flows/server-5202-A1-2flows'
]
generateServerCSVs(server_filenames)

num_clients = 2
num_servers = 2
fig, axes = plt.subplots(num_clients, num_servers, figsize=(15, 10))

colors = ['yellow', 'orange', 'red', 'blue', 'purple']
index_data = 0

for filename in client_filenames:
    filename_csv = filename + '.csv'
    dataframe = pd.read_csv(filename_csv, delimiter=';')
    dataframe_scaled = dataframe.iloc[::10, :]

    axes[0, index_data].set(xlabel='Time step', ylabel='Bandwidth (Mbps)')
    axes[0, index_data].plot(
        dataframe_scaled['Timestep'],
        dataframe_scaled['Bandwidth (Mbps)'],
        color=colors[index_data]
    )
    axes[0,index_data].set_title('Client {0} bandwidth'.format(index_data+1))
    index_data = index_data + 1


index_data = 0
for filename in server_filenames:
    filename_csv = filename + '.csv'
    dataframe = pd.read_csv(filename_csv, delimiter=';')
    dataframe_scaled = dataframe.iloc[::10, :]

    axes[1, index_data].set(xlabel='Time step', ylabel='Bandwidth (Mbps)')
    axes[1, index_data].plot(
        dataframe_scaled['Timestep'],
        dataframe_scaled['Bandwidth (Mbps)'],
        color=colors[index_data]
    )
    axes[1,index_data].set_title('Server {0} bandwidth'.format(index_data+1))
    index_data = index_data + 1

plt.savefig('../../experiments-data/A1-2-flows/bandwidth-clients.pdf')
