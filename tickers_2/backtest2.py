import sys
import json
import numpy as np
import talib
import datetime


FILE_PATH_5M = sys.argv[1] # 5 minute interval kline's file path
TRADE_SYMBOL = sys.argv[2]
TRADE_INTERVAL = sys.argv[3]
DIR = sys.argv[4]

result = f'{TRADE_SYMBOL}_{TRADE_INTERVAL}\n'

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

max_values = []
min_values = []

rsi_max_values = []
rsi_min_values = []

last_red_index = 0
last_green_index = 0

# signal_index = -1
trend_up_index = -1
trend_down_index = -1
bearish_divergence_index = -1
bullish_divergence_index = -1
bullish_divergence_ema21_index = -1
bullish_divergence_then_positive_apo_index = -1
bearish_divergence_3_index = -1
bearish_divergence_below_ema21 = -1
bearish_divergence_below_rsi40 = -1
macd_price_bullish_index = -1
ema_4x_above_index = -1
ema_4x_below_index = -1
bullish_divergence_canceled_ll_index = -1
is_last_bullish = False
last_bullish_for_cancel = 0
stoploss = 0

is_last_bearish_divergence = 0

green_to_red_indexes = []
red_to_green_indexes = []

for i in range(1, len(closes)):
    # extreme_volume_up
    if c[i] and closes[i] > ema8[i] and closes[i] > ema233[i] and opens[i] < closes[i]:
        stoploss = round(100 - (( ema21[i] / closes[i] ) * 100), 2)
        print_date_time(rows[i][0], end=f'   extreme_volume_up  {stoploss} \n')
        create_order("extreme_volume_up_tp_2", 2, stoploss, closes[i], rows[i][6])
        create_order("extreme_volume_up", 4, stoploss, closes[i], rows[i][6])
        create_order("extreme_volume_up_rsi45_below", 4, stoploss, closes[i], rows[i][6])
    
    # extreme_volume_down
    if c[i] and closes[i] < ema8[i] and closes[i] < ema233[i] and opens[i] > closes[i]:
        stoploss = round(100 - ((  closes[i] / ema21[i] ) * 100), 2)
        print_date_time(rows[i][0], end=f'   extreme_volume_down  {stoploss} \n')
        create_order("extreme_volume_down_tp_2", 2, stoploss, closes[i], rows[i][6])
        create_order("extreme_volume_down", 4, stoploss, closes[i], rows[i][6])
        create_order("extreme_volume_down_rsi55_above", 4, stoploss, closes[i], rows[i][6])
    
    
    temp_orders = []
    for order in orders:
        [strategy, takeprofit, stoploss, entry_price, entry_time] = order
        mn = 100 - (lows[i] / entry_price) * 100;
        mx = 100 - (entry_price / highs[i]) * 100;


        if strategy == "extreme_volume_up_tp_2":
            if mn >= stoploss:
                close_order(order, lows[i], rows[i][6], 0, -stoploss)
            elif mx >= takeprofit:
                close_order(order, highs[i], rows[i][6], 1, takeprofit)
            else:
                temp_orders.append(order)


        if strategy == "extreme_volume_down_tp_2":
            if mx >= stoploss:
                close_order(order, highs[i], rows[i][6], 0, -stoploss)
            elif mn >= takeprofit:
                close_order(order, lows[i], rows[i][6], 1, takeprofit)
            else:
                temp_orders.append(order)


        if strategy == "extreme_volume_up":
            if mn >= stoploss:
                close_order(order, lows[i], rows[i][6], 0, -stoploss)
            elif closes[i] < ema21[i]:
                tp = round(100 - (( entry_price / closes[i] ) * 100), 2)
                close_order(order, closes[i], rows[i][6], 1, tp)
            else:
                temp_orders.append(order)
                
        if strategy == "extreme_volume_up_rsi45_below":
            if mn >= stoploss:
                close_order(order, lows[i], rows[i][6], 0, -stoploss)
            elif rsi[i] < 45:
                tp = round(100 - (( entry_price / closes[i] ) * 100), 2)
                close_order(order, closes[i], rows[i][6], 1, tp)
            else:
                temp_orders.append(order)
                
        if strategy == "extreme_volume_down":
            if mx >= stoploss:
                close_order(order, highs[i], rows[i][6], 0, -stoploss)
            elif closes[i] > ema21[i]:
                tp = round(100 - (( closes[i] / entry_price ) * 100), 2)
                close_order(order, closes[i], rows[i][6], 1, tp)
            else:
                temp_orders.append(order)
                
        if strategy == "extreme_volume_down_rsi55_above":
            if mn >= stoploss:
                close_order(order, lows[i], rows[i][6], 0, -stoploss)
            elif rsi[i] > 55:
                tp = round(100 - (( closes[i] / entry_price ) * 100), 2)
                close_order(order, closes[i], rows[i][6], 1, tp)
            else:
                temp_orders.append(order)
                
                
    orders = temp_orders
    
    
log_file_name = f"{DIR}/{TRADE_SYMBOL}_{TRADE_INTERVAL}_orders.json"
with open(log_file_name, "w") as outfile:
    json.dump(closed_orders, outfile)
