import pandas as pd
import numpy as np

import matplotlib.pyplot as plt

fig, axes = plt.subplots(2)


#  S1.1;S1.2;S1.3;S2.1;S2.2;S2.3;S2.4;S3.1;S3.2;S3.3;S3.4;S4.1;S4.2;S4.3;S5.1;S5.2

data = pd.read_csv('./data/output-app-15-set-1_new.csv', delimiter=';')
dataframe_to_plot = pd.DataFrame({
    'S1.1': data['S1.1'],
    'S1.2': data['S1.2'],
    'S1.3': data['S1.3'],
    'S2.1': data['S2.1'],
    'S2.2': data['S2.2'],
    'S2.3': data['S2.3'],
    'S2.4': data['S2.4'],
    'S3.1': data['S3.1'],
    'S3.2': data['S3.2'],
    'S3.3': data['S3.3'],
    'S3.4': data['S3.4'],
    'S4.1': data['S4.1'],
    'S4.2': data['S4.2'],
    'S4.3': data['S4.3'],
    'S5.1': data['S5.1'],
    'S5.2': data['S5.2'],
    },
index=range(0,500))

dataframe_to_plot.plot.line(figsize=(10, 10), title='RX over time', xticks=10)

plt.xlabel('Step')
plt.ylabel('Port RX (bps)')
plt.savefig('./images/rx-time-15-set-1-temp.pdf')
