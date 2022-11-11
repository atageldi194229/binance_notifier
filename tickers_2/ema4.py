import sys
import json
import numpy as np
import talib
import bot
import pandas
import datetime


FILE_PATH_5M = sys.argv[1] # 5 minute interval kline's file path
TRADE_SYMBOL = sys.argv[2]
TRADE_INTERVAL = sys.argv[3]

result = f'{TRADE_SYMBOL}_{TRADE_INTERVAL}\n'

def custom_print(text, end='\n'):
    global result
    result = f'{result}{text}{end}'
    

def print_date_time(ms, end = '\n', print_method = custom_print):
    s = ms / 1000.0
    print_method(datetime.datetime.fromtimestamp(s).strftime('%Y-%m-%d %H:%M:%S'), end=end)


# read json file and calculate
with open(FILE_PATH_5M) as json_file:
    data_5m = json.load(json_file)

rows = data_5m[-400:]
closes = np.array(rows)[:,4]
closes = list(map(float, closes))

np_closes = np.array(closes)
ema233 = talib.EMA(np_closes, timeperiod=233)
ema55 = talib.EMA(np_closes, timeperiod=55)
ema21 = talib.EMA(np_closes, timeperiod=21)
ema8 = talib.EMA(np_closes, timeperiod=8)

def isEMA4Down(ema233, ema55, ema21, ema8):
    return ema233 >= ema55 and ema55 >= ema21 and ema21 >= ema8


def isEMA4Up(ema233, ema55, ema21, ema8):
    return ema233 <= ema55 and ema55 <= ema21 and ema21 <= ema8


if not isEMA4Down(ema233[-2], ema55[-2], ema21[-2], ema8[-2]) and isEMA4Down(ema233[-1], ema55[-1], ema21[-1], ema8[-1]):
    print_date_time(rows[-1][0], end=f'   EMA 4x above, down\n')
    bot.bot_send_message(result)

if not isEMA4Up(ema233[-2], ema55[-2], ema21[-2], ema8[-2]) and isEMA4Up(ema233[-1], ema55[-1], ema21[-1], ema8[-1]):
    print_date_time(rows[-1][0], end=f'   EMA 4x below, up\n')
    bot.bot_send_message(result)