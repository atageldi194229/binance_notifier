import sys
import json
import numpy as np
import talib
import bot
import pandas
import datetime


def print_date_time(ms):
    s = ms / 1000.0
    print(datetime.datetime.fromtimestamp(s).strftime('%Y-%m-%d %H:%M:%S.%f'))


FILE_PATH_5M = sys.argv[1] # 5 minute interval kline's file path
# TRADE_SYMBOL = sys.argv[2]
# TRADE_INTERVAL = sys.argv[3]

# read json file and calculate
with open(FILE_PATH_5M) as json_file:
    data_5m = json.load(json_file)

rows = data_5m[-400:]
closes = np.array(rows)[:,4]
closes = list(map(float, closes))
highs = np.array(rows)[:,2]
highs = list(map(float, highs))
lows = np.array(rows)[:,3]
lows = list(map(float, lows))


np_closes = np.array(closes)
macd, macdsignal, macdhist = talib.MACD(np_closes, fastperiod=12, slowperiod=26, signalperiod=9)
rsi = talib.RSI(np_closes, timeperiod=14)

# print(len(closes), len(macdhist))


max_values = []
min_values = []
rsi_max_values = []

last_red_index = 0
last_green_index = 0

signal_index = -1

for i in range(20, len(macdhist)):
    h_a = macdhist[i - 1]
    h_b = macdhist[i]
    
    if h_a < 0 and h_b >= 0:
        last_red_index = i - 1
        
        min_value = max(lows[last_green_index + 1: last_red_index + 1])
        min_values.append(min_value)
        
    
    if h_a > 0 and h_b <= 0:
        last_green_index = i - 1

        max_value = max(highs[last_red_index + 1: last_green_index + 1])
        max_values.append(max_value)
        
        rsi_max_value = max(rsi[last_red_index + 1: last_green_index + 1])
        rsi_max_values.append(rsi_max_value)
        
        if len(max_values) > 1:
            a_max, b_max = max_values[-2], max_values[-1]
            rsi_a_max, rsi_b_max = rsi_max_values[-2], rsi_max_values[-1]
            if a_max < b_max and rsi_a_max > rsi_b_max:
                signal_index = i
                print(a_max, '-', b_max, end='   =>   ')
                print_date_time(rows[i][0])

# print()
print(max_values)

if signal_index - 1 == last_red_index and last_red_index == len(macdhist) - 2:
    print("BOT_MESSAGE")
    bot.bot_send_message("BOT_MESSAGE")