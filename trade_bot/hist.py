import datetime
import math
import time
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt


df = pd.read_csv("backtest_data_2.csv", usecols=['win', 'stoploss', 'trade_interval', 'strategy', 'win_percentage'])

df = df[df['trade_interval'] == '5m']
# ['bullish_divergence' 'bullish_divergence_above_ema21'
#  'bearish_divergence' 'bearish_divergence_below_ema21'
#  'bearish_divergence_below_rsi40' 'bearish_divergence_1-3']
# df = df[df['strategy'] == 'bearish_divergence']
df = df[df['strategy'] == 'extreme_volume_up']

# df2 = df.copy()
# df = df[df['win'] == 0]

wins = df.copy()
wins = wins[wins['win_percentage'] > 0]


losses = df.copy()
losses = losses[losses['win_percentage'] < 0]

# df.hist(column='stoploss', bins=50, by='win')

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

plt.hist([wins['stoploss'], losses['stoploss']], bins=200, label=['win', 'loss'])
plt.show()