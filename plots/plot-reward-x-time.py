import pandas as pd
import numpy as np

import plotly.express as px

df = pd.read_csv('./teste-app.csv')

fig = px.line(df, x = 'Step', y = 'Reward', title='Reward over time step')
fig.show()
fig.write_image('images/teste-reward-x-time.pdf')
