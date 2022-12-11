import datetime
import math
import time
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt


df = pd.read_csv("backtest_data.csv", usecols=['win', 'stoploss', 'trade_interval', 'strategy'])

df = df[df['trade_interval'] == '5m']
df = df[df['strategy'] == 'bearish_divergence']

# df2 = df.copy()
# df = df[df['win'] == 0]

df.hist(column='stoploss', bins=50, by='win')

# df.plot(kind='hist',
#         alpha=0.7,
#         bins=50,
#         title='Stoploss and wins',
#         # row=45,
#         grid=True,
#         figsize=(12,8),
#         fontsize=15,
#         color=['#A0E8AF', '#FFCF56'])

# plt.xlabel('Stoploss')
# plt.ylabel('Wins, Loss')

plt.show()