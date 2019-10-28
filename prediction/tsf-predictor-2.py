import pandas as pd
import numpy as np
import matplotlib.pylab as plt

FILENAME = '../snapshots/flow-files-with-int-features/fluxo-0-size-102518.5062828064-mb-100.11572879180312-gb.csv'

"""
This is a very important concept in Time Series Analysis. In order to apply a time series model, it is important for the Time series to be stationary; in other words all its statistical properties (mean,variance) remain constant over time. This is done basically because if you take a certain behavior over time, it is important that this behavior is same in the future in order for us to forecast the series. There are a lot of statistical theories to explore stationary series than non-stationary series. (Thus we can bring the fight to our home ground!)
"""



data =  pd.read_csv(FILENAME)
print(data.head())
print('\nData Types:')
print(data.dtypes)
