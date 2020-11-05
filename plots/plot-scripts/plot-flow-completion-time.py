from parseClientIperfData import generateClientCSVs
from parseServerIperfData import generateServerCSVs

import pandas as pd
import numpy as np

import matplotlib.pyplot as plt

colors = ['orange', 'red', 'pink', 'blue', 'purple', 'orange', 'red', 'pink', 'blue', 'purple']
agents = ['A1']

def createFlowCompletionTimePlots(num_iperfs):
    index_data = 0

    for filename in client_filenames:
        filename_csv = filename + '.csv'
        dataframe = pd.read_csv(filename_csv, delimiter=';')
        dataframe_scaled = dataframe.iloc[::10, :]

        plt.plot(
            dataframe_scaled['Timestep'],
            dataframe_scaled['Bandwidth (Mbps)'],
            color=colors[index_data]
        )
        plt.set_title('Client {0} bandwidth'.format(index_data+1))
        index_data = index_data + 1


    plt.savefig('../../experiments-data/A1-10-flows/A1-10-bandwidth.pdf')


if __name__ == '__main__':
    createFlowCompletionTimePlots()
