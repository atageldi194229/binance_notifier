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

for i in range(1, len(closes)):
    h_a = rsi[i - 1]
    h_b = rsi[i]
    
    if h_a < 65 and h_b >= 65:
        last_red_index = i - 1
        red_to_green_indexes.append(last_red_index)
        
        min_value = min(lows[last_green_index + 1: last_red_index + 1])
        min_values.append(min_value)
        
        # rsi min values
        rsi_min_value = min(rsi[last_green_index + 1: last_red_index + 1])
        rsi_min_values.append(rsi_min_value)
        
        
    if h_a > 65 and h_b <= 65:
        last_green_index = i - 1
        green_to_red_indexes.append(last_green_index)

        max_value = max(highs[last_red_index + 1: last_green_index + 1])
        max_values.append(max_value)
        
        rsi_max_value = max(rsi[last_red_index + 1: last_green_index + 1])
        rsi_max_values.append(rsi_max_value)
        
        # bearish divergence
        if len(max_values) > 1 and len(rsi_max_values) > 1:
            a_max, b_max = max_values[-2], max_values[-1]
            rsi_a_max, rsi_b_max = rsi_max_values[-2], rsi_max_values[-1]
            stoploss = round(100 - (( closes[i] / b_max ) * 100), 2)
            if a_max < b_max and rsi_a_max > rsi_b_max and ema233[i] > closes[i]:
                bearish_divergence_index = i
                print_date_time(rows[i][0], end=f'   bearish_divergence  {stoploss}\n')
                create_order("bearish_divergence", stoploss*3, stoploss, closes[i], rows[i][6])

    temp_orders = []
    for order in orders:
        [strategy, takeprofit, stoploss, entry_price, entry_time] = order
        mn = 100 - (lows[i] / entry_price) * 100;
        mx = 100 - (entry_price / highs[i]) * 100;
        
        if strategy in ["bearish_divergence", "bearish_divergence_1-3", "bearish_divergence_below_ema21", "bearish_divergence_below_rsi40"]:
            if mx >= stoploss:
                close_order(order, highs[i], rows[i][6], 0, -stoploss)
            elif mn >= takeprofit:
                close_order(order, lows[i], rows[i][6], 1, takeprofit)
            else:
                temp_orders.append(order)

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
