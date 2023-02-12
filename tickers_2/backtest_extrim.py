import sys
import json
import numpy as np
import talib
import bot
import pandas as pd
import datetime

# # ARGS
# FILE_PATH = sys.argv[1]
# OUTPUT_FILE = sys.argv[2]


FILE_PATH_5M = sys.argv[1] # 5 minute interval kline's file path
TRADE_SYMBOL = sys.argv[2]
TRADE_INTERVAL = sys.argv[3]
DIR = sys.argv[4]

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




# read json file and data initialization
with open(FILE_PATH) as json_file:
    data = json.load(json_file)

df = pd.DataFrame(data, columns=["Open time",
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


closes = df["Close"].astype('float64').values
lows = df["Low"].astype('float64').values
highs = df["High"].astype('float64').values
volumes = df["Volume"].astype('float64').values

df["Close"] = closes
df["Low"] = lows
df["High"] = highs
df["Volume"] = volumes

f = lambda ms: datetime.datetime.fromtimestamp(ms / 1000).strftime('%Y-%m-%d %H:%M:%S')
close_times_string = np.vectorize(f)(df["Close time"].values)

df["Close time text"] = close_times_string

# sma volumer
multiplier = 3
v1 = talib.SMA(volumes, timeperiod=20) 
v9 = v1 * multiplier
df["extremium"] = volumes > v9

# ema init
ema233 = talib.EMA(closes, timeperiod=233)
ema55 = talib.EMA(closes, timeperiod=55)
ema21 = talib.EMA(closes, timeperiod=21)
ema8 = talib.EMA(closes, timeperiod=8)

# rsi
rsi = talib.RSI(closes, timeperiod=14)
df["rsi"] = rsi

df["ema233"] = ema233
df["ema55"] = ema55
df["ema21"] = ema21
df["ema8"] = ema8


# ######################
# rsi max close 70 up
# ######################
max_values = [0]
min_values = [0]

last_red_index = 0
last_green_index = 0


df["max values"] = rsi
for i in range(1, len(df)):
    df.at[i, 'max values'] = max_values[-1]

    if rsi[i - 1] < 70 and rsi[i] >= 70:
        last_red_index = i - 1
        min_value = min(lows[last_green_index: last_red_index + 1])
        min_values.append(min_value)
        
    if rsi[i - 1] > 70 and rsi[i] <= 70:
        last_green_index = i - 1
        max_value = max(highs[last_red_index: last_green_index + 1])
        max_values.append(max_value)



df["accessible"] = df["max values"] < df["Close"]
df["accessible"] = df["extremium"] & df["accessible"]
df["accessible"] = df["accessible"] & df["ema8"] > df["ema21"] 
df["accessible"] = df["accessible"] & df["ema21"] > df["ema55"] 
df["accessible"] = df["accessible"] & df["Close"] > df["ema233"]

df = df[df["Close time"] > 1670800799999]

for i in range(1, len(df)):
    temp_orders = []
    for order in orders:
        [strategy, stoploss, ema_type, entry_price, entry_time] = order
        pnl = 100 - (entry_price / closes[i]) * 100
        
        if strategy == "extremium_trend":
            if closes[i] < stoploss:
                close_order(order, lows[i], df["Close time text"].iloc[i], 0 if pnl < 0 else 1, pnl)
            elif (ema_type == "ema21" and lows[i] < ema21[i]) or (ema_type == "ema55" and lows[i] < ema55[i]):
                close_order(order, lows[i], df["Close time text"].iloc[i], 0 if pnl < 0 else 1, pnl)

    orders = temp_orders

    if df["accessible"].iloc[i] and len(orders) == 0:
        is_under_ema21 = False
        is_under_ema55 = False

        for j in range(i - 1, 2, -1):
            if rsi[j - 1] < 50:
                break
            if lows[j] < ema21[j]:
                is_under_ema21 = True
            if lows[j] < ema55[j]:
                is_under_ema55 = True

        create_order("extremium_trend", ema55[i] if is_under_ema21 else ema21[i], "ema55" if is_under_ema21 else "ema21", closes[i], df["Close time text"].iloc[i])


log_file_name = f"{DIR}/{TRADE_SYMBOL}_{TRADE_INTERVAL}_orders.json"
with open(log_file_name, "w") as outfile:
    json.dump(closed_orders, outfile)
