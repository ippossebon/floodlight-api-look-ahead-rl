from parseClientIperfData import generateClientCSVs
from parseServerIperfData import generateServerCSVs

import pandas as pd
import numpy as np

import matplotlib.pyplot as plt

client_filenames = [
    '../../experiments-data/A1-10-flows/client-46110-A1-10flows',
    '../../experiments-data/A1-10-flows/client-46112-A1-10flows',
    '../../experiments-data/A1-10-flows/client-46114-A1-10flows',
    '../../experiments-data/A1-10-flows/client-46116-A1-10flows',
    '../../experiments-data/A1-10-flows/client-46118-A1-10flows',
    '../../experiments-data/A1-10-flows/client-46120-A1-10flows',
    '../../experiments-data/A1-10-flows/client-46122-A1-10flows',
    '../../experiments-data/A1-10-flows/client-46124-A1-10flows',
    '../../experiments-data/A1-10-flows/client-46126-A1-10flows',
    '../../experiments-data/A1-10-flows/client-46128-A1-10flows'
]
generateClientCSVs(client_filenames)


server_filenames = [
    '../../experiments-data/A1-10-flows/server-5201-A1-10flows',
    '../../experiments-data/A1-10-flows/server-5202-A1-10flows',
    '../../experiments-data/A1-10-flows/server-5203-A1-10flows',
    '../../experiments-data/A1-10-flows/server-5204-A1-10flows',
    '../../experiments-data/A1-10-flows/server-5205-A1-10flows',
    '../../experiments-data/A1-10-flows/server-5206-A1-10flows',
    '../../experiments-data/A1-10-flows/server-5207-A1-10flows',
    '../../experiments-data/A1-10-flows/server-5208-A1-10flows',
    '../../experiments-data/A1-10-flows/server-5209-A1-10flows',
    '../../experiments-data/A1-10-flows/server-5210-A1-10flows'
]
generateServerCSVs(server_filenames)

num_iperfs = 10
fig, axes = plt.subplots(2, num_iperfs, figsize=(60, 10))

colors = ['orange', 'red', 'pink', 'blue', 'purple', 'orange', 'red', 'pink', 'blue', 'purple']
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

plt.savefig('../../experiments-data/A1-10-flows/A1-10-bandwidth.pdf')
