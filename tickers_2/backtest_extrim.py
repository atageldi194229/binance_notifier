import sys
import json
import numpy as np
import talib
import bot
import pandas as pd
import datetime


FILE_PATH = sys.argv[1]
OUTPUT_FILE = sys.argv[2]

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
df["accessible"] = df["extremium"] and df["accessible"] and df["ema8"] > df["ema21"] and df["ema21"] > df["ema55"] and df["Close"] > df["ema233"]

df = df[df["Close time"] > 1670800799999]

# save to csv file
df.to_csv(OUTPUT_FILE)

