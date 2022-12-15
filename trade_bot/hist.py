import datetime
import math
import time
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt


df = pd.read_csv("Result_TP_4.csv", usecols=['win', 'stoploss', 'trade_interval', 'strategy'])

df = df[df['trade_interval'] == '15m']
# ['bullish_divergence' 'bullish_divergence_above_ema21'
#  'bearish_divergence' 'bearish_divergence_below_ema21'
#  'bearish_divergence_below_rsi40' 'bearish_divergence_1-3']
# df = df[df['strategy'] == 'bearish_divergence']
df = df[df['strategy'] == 'bearish_divergence_1-3']

# df2 = df.copy()
# df = df[df['win'] == 0]

wins = df.copy()
wins = wins[wins['win'] == 1]


losses = df.copy()
losses = losses[losses['win'] == 0]

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