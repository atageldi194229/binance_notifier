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
DIR = sys.argv[4]

result = f'{TRADE_SYMBOL}_{TRADE_INTERVAL}\n'

takeprofit = 4

# [[strategy, takeprofit, stoploss, entry_price, entry_time, close_price, close_time, win]]

orders = [];
closed_orders = [];


def create_order(strategy, takeprofit, stoploss, entry_price, entry_time): 
    orders.append([strategy, takeprofit, stoploss, entry_price, entry_time]);

def close_order(order, close_price, close_time, win, win_percentage):
    [strategy, takeprofit, stoploss, entry_price, entry_time] = order
    # closed_orders.append([strategy, takeprofit, stoploss, entry_price, entry_time, close_price, close_time, win, win_percentage])
    closed_orders.append({
        "trade_symbol": TRADE_SYMBOL, 
        "trade_interval": TRADE_INTERVAL,
        "strategy": strategy, 
        "takeprofit": takeprofit, 
        "stoploss": stoploss, 
        "entry_price": entry_price, 
        "entry_time": entry_time, 
        "close_price": close_price, 
        "close_time": close_time, 
        "win": win, 
        "win_percentage": win_percentage
        })

def custom_print(text, end='\n'):
    global result
    result = f'{result}{text}{end}'
    

def print_date_time(ms, end = '\n', print_method = custom_print):
    s = ms / 1000.0
    print_method(datetime.datetime.fromtimestamp(s).strftime('%Y-%m-%d %H:%M:%S'), end=end)

def isCandleAboveEMA(ema, op, cl):
    return ema < op and ema < cl

def isEMA4Down(ema233, ema55, ema21, ema8):
    return ema233 >= ema55 and ema55 >= ema21 and ema21 >= ema8

def isEMA4Up(ema233, ema55, ema21, ema8):
    return ema233 <= ema55 and ema55 <= ema21 and ema21 <= ema8


# read json file and calculate
with open(FILE_PATH_5M) as json_file:
    data_5m = json.load(json_file)

rows = data_5m
opens = np.array(rows)[:,1]
opens = list(map(float, opens))
closes = np.array(rows)[:,4]
closes = list(map(float, closes))
highs = np.array(rows)[:,2]
highs = list(map(float, highs))
lows = np.array(rows)[:,3]
lows = list(map(float, lows))
volumes = np.array(rows)[:,5]
volumes = list(map(float, volumes))


np_closes = np.array(closes)
macd, macdsignal, macdhist = talib.MACD(np_closes, fastperiod=12, slowperiod=26, signalperiod=9)
# apo = talib.APO(np_closes, fastperiod=8, slowperiod=21)
ema233 = talib.EMA(np_closes, timeperiod=233)
ema55 = talib.EMA(np_closes, timeperiod=55)
ema21 = talib.EMA(np_closes, timeperiod=21)
ema8 = talib.EMA(np_closes, timeperiod=8)


# sma volumer
multiplier = 3

np_volumes = np.array(volumes)
v1 = talib.SMA(np_volumes, timeperiod=20) 
v9 = v1 * multiplier
c = np_volumes > v9


rsi = talib.RSI(np_closes, timeperiod=14)

# print(len(closes), len(macdhist))

max_values = []
min_values = []

rsi_max_values = []
rsi_min_values = []

last_red_index = 0
last_green_index = 0

red_to_green_indexes = []
green_to_red_indexes = []

bearish_divergence_index = -1

# signal_index = -1
stoploss = 0


volume_trend_long_index = -1
extreme_volume_up_index = -1
extreme_volume_down_index = -1

green_to_red_indexes = []
red_to_green_indexes = []

for i in range(1, len(closes)):
    h_a = rsi[i - 1]
    h_b = rsi[i]
    
    is_seq = ema8[i] > ema21[i] and ema21[i] > ema55[i] and ema55[i] > ema233[i]
    if c[i] and closes[i] > ema8[i] and closes[i] > ema233[i] and opens[i] < closes[i] and is_seq and len(max_values) > 1 and max_values[-1] < closes[i] and rsi[i - 1] >= 50 and rsi[i] > 50:
        rsi50_low_index = i - 1
        
        is_under_ema21 = False
        is_under_ema55 = False
        
        for j in range(i - 1, 2, -1):
            if rsi[j] < 50:
                break
            if lows[i] < ema21[j]:
                is_under_ema21 = True
            if lows[i] < ema55[j]:
                is_under_ema55 = True
            
        if not is_under_ema55 and len(orders) == 0:
            create_order("extremium_trend", stoploss, "ema55" if is_under_ema21 else "ema21", closes[i], rows[i][6])


    if h_a < 70 and h_b >= 70:
        last_red_index = i - 1
        red_to_green_indexes.append(last_red_index)
        
        min_value = min(lows[last_green_index + 1: last_red_index + 1])
        min_values.append(min_value)
        
        # rsi min values
        rsi_min_value = min(rsi[last_green_index + 1: last_red_index + 1])
        rsi_min_values.append(rsi_min_value)
        
        
    if h_a > 70 and h_b <= 70:
        last_green_index = i - 1
        green_to_red_indexes.append(last_green_index)

        max_value = max(highs[last_red_index + 1: last_green_index + 1])
        max_values.append(max_value)
        
        rsi_max_value = max(rsi[last_red_index + 1: last_green_index + 1])
        rsi_max_values.append(rsi_max_value)
        
    temp_orders = []
    for order in orders:
        [strategy, takeprofit, stoploss, entry_price, entry_time] = order
        mn = 100 - (lows[i] / entry_price) * 100
        mx = 100 - (entry_price / highs[i]) * 100
        
        pnl = 100 - (entry_price / closes[i]) * 100
        
        if strategy == "extremium_trend":
            if (stoploss == "ema21" and lows[i] < ema21[i]) or (stoploss == "ema55" and lows[i] < ema55[i]):
                close_order(order, lows[i], rows[i][6], 0 if pnl < 0 else 1, pnl)

            if rsi[i] < 45:
                close_order(order, closes[i], rows[i][6], 0 if pnl < 0 else 1, pnl)
        
        # if strategy in ["bearish_divergence", "bearish_divergence_1-3", "bearish_divergence_below_ema21", "bearish_divergence_below_rsi40"]:
        #     if mx >= stoploss:
        #         close_order(order, highs[i], rows[i][6], 0, -stoploss)
        #     elif mn >= takeprofit:
        #         close_order(order, lows[i], rows[i][6], 1, takeprofit)
        #     else:
        #         temp_orders.append(order)

        # if strategy in ["bullish_divergence", "bullish_divergence_above_ema21"]:
        #     if mn >= stoploss:
        #         close_order(order, lows[i], rows[i][6], 0, -stoploss)
        #     elif mx >= takeprofit:
        #         close_order(order, highs[i], rows[i][6], 1, takeprofit)
        #     else:
        #         temp_orders.append(order)
        
        # if strategy == "volume_trend_long":
        #     if mn >= stoploss:
        #         close_order(order, lows[i], rows[i][6], 0, -stoploss)
        #     elif closes[i] < ema21[i]:
        #         tp = round(100 - (( closes[i] / order[3] ) * 100), 2)
        #         close_order(order, closes[i], rows[i][6], 1, tp)
        #     else:
        #         temp_orders.append(order)
                
        # if strategy == "volume_trend_long_rsi50_below":
        #     if mn >= stoploss:
        #         close_order(order, lows[i], rows[i][6], 0, -stoploss)
        #     elif rsi[i] < 50:
        #         tp = round(100 - (( closes[i] / order[3] ) * 100), 2)
        #         close_order(order, closes[i], rows[i][6], 1, tp)
        #     else:
        #         temp_orders.append(order)
    orders = temp_orders



log_file_name = f"{DIR}/{TRADE_SYMBOL}_{TRADE_INTERVAL}_orders.json"
with open(log_file_name, "w") as outfile:
    json.dump(closed_orders, outfile)
