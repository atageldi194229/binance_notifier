import sys
import json
import numpy as np
import talib
import bot
import pandas as pd
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

df = pd.DataFrame(data_5m, columns=["Open time",
                                 "Open", 
                                 "High", 
                                 "Low", 
                                 "Close", 
                                 "Volume", 
                                 "Close time", 
                                 "Quote asset volume", 
                                 "Number of trades", 
                                 "Taker buy base asset volume", 
                                 "Taker buy quote asset volume", 
                                 "Ignore"])

ms_15m = 1000 * 60 * 15
ms_1h = 1000 * 60 * 60

df_15m = df[(df["Close time"] + 1) % ms_15m == 0]
df_1h = df[(df["Close time"] + 1) % ms_1h == 0]

closes_5m = df["Close"].astype('float64').values
closes_15m = df_15m["Close"].astype('float64').values
closes_1h = df_1h["Close"].astype('float64').values
lows_5m = df["Low"].astype('float64').values
highs_5m = df["High"].astype('float64').values

f = lambda ms: datetime.datetime.fromtimestamp(ms / 1000).strftime('%Y-%m-%d %H:%M:%S')
close_times_5m = np.vectorize(f)(df["Close time"].values)



ema50_15m = talib.EMA(closes_15m, timeperiod=50)
ema50_1h = talib.EMA(closes_1h, timeperiod=50)

macd, macdsignal, macdhist = talib.MACD(closes_5m, fastperiod=12, slowperiod=26, signalperiod=9)

max_values = []
min_values = []

macd_max_values = []
macd_min_values = []

last_red_index = 0
last_green_index = 0

# signal_index = -1
bearish_divergence_index = -1
bullish_divergence_index = -1
stoploss = 0

green_to_red_indexes = []
red_to_green_indexes = []

for i in range(600, len(closes_5m)):
    h_a = macdhist[i - 1]
    h_b = macdhist[i]
    
    if h_a < 0 and h_b >= 0:
        last_red_index = i - 1
        red_to_green_indexes.append(last_red_index)
        
        min_value = min(lows_5m[last_green_index + 1: last_red_index + 1])
        min_values.append(min_value)
        
        # macd min values
        macd_min_value = min(macd[last_green_index + 1: last_red_index + 1])
        macd_min_values.append(macd_min_value)
        
        
        # bullish divergence
        if len(min_values) > 1 and len(macd_min_values) > 1:
            a_min, b_min = min_values[-2], min_values[-1]
            macd_a_min, macd_b_min = macd_min_values[-2], macd_min_values[-1]

            is_ema50_15m_above_1h = ema50_15m[i // 3] > ema50_1h[i // 12]
            
            is_macd_below_zero = (macd[red_to_green_indexes[-2]:green_to_red_indexes[-1]] < 0).all()
            
            if a_min > b_min and macd_a_min < macd_b_min and is_ema50_15m_above_1h and is_macd_below_zero:
                bullish_divergence_index = i
                stoploss = round(100 - (( b_min / closes_5m[i] ) * 100), 2)
                print_date_time(df["Open time"][i], end=f'   bullish_divergence  {stoploss} \n')
                create_order("bullish_divergence", stoploss * 2, stoploss, closes_5m[i], close_times_5m[i])

    if h_a > 0 and h_b <= 0:
        last_green_index = i - 1
        green_to_red_indexes.append(last_green_index)

        max_value = max(highs_5m[last_red_index + 1: last_green_index + 1])
        max_values.append(max_value)
        
        macd_max_value = max(macd[last_red_index + 1: last_green_index + 1])
        macd_max_values.append(macd_max_value)
        
        # bearish divergence
        if len(max_values) > 1 and len(macd_max_values) > 1:
            a_max, b_max = max_values[-2], max_values[-1]
            macd_a_max, macd_b_max = macd_max_values[-2], macd_max_values[-1]
            
            is_ema50_15m_below_1h = ema50_15m[i // 3] < ema50_1h[i // 12]
            
            is_macd_below_zero = (macd[green_to_red_indexes[-2]:red_to_green_indexes[-1]] > 0).all()
            
            if a_max < b_max and macd_a_max > macd_b_max and is_ema50_15m_below_1h and is_macd_below_zero:
                bearish_divergence_index = i
                stoploss = round(100 - (( closes_5m[i] / b_max ) * 100), 2)
                print_date_time(df["Open time"][i], end=f'   bearish_divergence  {stoploss}\n')
                create_order("bearish_divergence", stoploss * 2, stoploss, closes_5m[i], close_times_5m[i])

    temp_orders = []
    for order in orders:
        [strategy, takeprofit, stoploss, entry_price, entry_time] = order
        mn = 100 - (lows_5m[i] / entry_price) * 100;
        mx = 100 - (entry_price / highs_5m[i]) * 100;
        
        if strategy in ["bearish_divergence"]:
            if mx >= stoploss:
                close_order(order, highs_5m[i], close_times_5m[i], 0, -stoploss)
            elif mn >= takeprofit:
                close_order(order, lows_5m[i], close_times_5m[i], 1, takeprofit)
            else:
                temp_orders.append(order)

        if strategy in ["bullish_divergence"]:
            if mn >= stoploss:
                close_order(order, lows_5m[i], close_times_5m[i], 0, -stoploss)
            elif mx >= takeprofit:
                close_order(order, highs_5m[i], close_times_5m[i], 1, takeprofit)
            else:
                temp_orders.append(order)
        
    orders = temp_orders
    
    
    
log_file_name = f"{DIR}/{TRADE_SYMBOL}_{TRADE_INTERVAL}_orders.json"
with open(log_file_name, "w") as outfile:
    json.dump(closed_orders, outfile)
