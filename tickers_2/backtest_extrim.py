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

f = lambda ms: datetime.datetime.fromtimestamp(ms / 1000).strftime('%Y-%m-%d %H:%M:%S')
close_times_string = np.vectorize(f)(df["Close time"].values)

df["Close time text"] = close_times_string

# sma volumer
multiplier = 3
v1 = talib.SMA(volumes, timeperiod=20) 
v9 = v1 * multiplier
c = volumes > v9

# ema init
ema233 = talib.EMA(closes, timeperiod=233)
ema55 = talib.EMA(closes, timeperiod=55)
ema21 = talib.EMA(closes, timeperiod=21)
ema8 = talib.EMA(closes, timeperiod=8)

df["ema233"] = ema233
df["ema55"] = ema55
df["ema21"] = ema21
df["ema8"] = ema8

df = df[(df["ema8"] > df["ema21"]) & (df["ema21"] > df["ema55"]) & (df["Close"] > df["ema233"])]
df = df[df["Close time"] > 1670800799999]

# save to csv file
df.to_csv(OUTPUT_FILE)

