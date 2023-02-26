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


FILE_PATH = sys.argv[1] # 5 minute interval kline's file path
TRADE_SYMBOL = sys.argv[2]
TRADE_INTERVAL = sys.argv[3]
DIR = sys.argv[4]
# BTC_FILE_PATH = sys.argv[5]


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

# with open(BTC_FILE_PATH) as json_file:
#     btc_data = json.load(json_file)

KLINE_COLUMNS = ["Open time",
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
                "Ignore"]

df = pd.DataFrame(data, columns=KLINE_COLUMNS)
# btc_df = pd.DataFrame(btc_data, columns=KLINE_COLUMNS)

# btc_df["Close"] = btc_df["Close"].astype('float64').values

opens = df["Open"].astype('float64').values
closes = df["Close"].astype('float64').values
lows = df["Low"].astype('float64').values
highs = df["High"].astype('float64').values
volumes = df["Volume"].astype('float64').values

df["Open"] = opens
df["Close"] = closes
df["Low"] = lows
df["High"] = highs
df["Volume"] = volumes

f = lambda ms: datetime.datetime.fromtimestamp(ms / 1000).strftime('%Y-%m-%d %H:%M:%S')
close_times_string = np.vectorize(f)(df["Close time"].values)

df["Close time text"] = close_times_string

# sma volumer
multiplier = 2
v1 = talib.SMA(volumes, timeperiod=20) 
v9 = v1 * multiplier
df["extremium"] = volumes > v9

# ema init
ema233 = talib.EMA(closes, timeperiod=233)
ema55 = talib.EMA(closes, timeperiod=55)
ema21 = talib.EMA(closes, timeperiod=21)
ema8 = talib.EMA(closes, timeperiod=8)

# btc emas
# btc_df["ema233"] = talib.EMA(btc_df["Close"], timeperiod=233)
# btc_df["ema55"] = talib.EMA(btc_df["Close"], timeperiod=55)
# btc_df["ema21"] = talib.EMA(btc_df["Close"], timeperiod=21)
# btc_df["ema8"] = talib.EMA(btc_df["Close"], timeperiod=8)

# rsi
rsi = talib.RSI(closes, timeperiod=14)
df["rsi"] = rsi

# STOCHRSI
fastk, fastd = talib.STOCHRSI(closes)

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
# df["accessible"] = df["accessible"] & df["extremium"]
# df["accessible"] = df["accessible"] & df["ema8"] > df["ema21"] 
# df["accessible"] = df["accessible"] & df["ema21"] > df["ema55"] 
# df["accessible"] = df["accessible"] & df["Close"] > df["ema233"]

# df = df[df["Close time"] > 1670800799999]


# init
max_values = [0,0]
max_rsi_values = [0,0]
btc_i = 0
last_open = 0

# loop
for i in range(1, len(df)):
    # data collector for bearish divergence
    if fastd[i - 1] < 80 and fastd[i] >= 80:
        last_open = i
    if fastd[i - 1] > 80 and fastd[i] <= 80:
        max_values.append( max(highs[last_open: i + 1]) )
        max_rsi_values.append( max(fastd[last_open: i + 1]) )

    # bearish divergence finder
    is_bearish_divergence = max_values[-2] < max_values[-1] and max_rsi_values[-2] > max_rsi_values[-1]


    # ##################
    # order closer
    temp_orders = []
    for order in orders:
        [strategy, stoploss, ema_type, entry_price, entry_time] = order
        pnl = 100 - (entry_price / closes[i]) * 100
        # pnl2 = 100 - (entry_price / highs[i]) * 100

        if strategy == "extremium_trend":
            # if pnl > 2:
                # close_order(order, lows[i], df["Close time text"].iloc[i], 0 if pnl < 0 else 1, pnl)
            # if pnl2 > 1:
                # close_order(order, lows[i], df["Close time text"].iloc[i], 0 if pnl < 0 else 1, 1)
            if lows[i] < stoploss:
                order[2]="stoploss_" + order[2]
                pnl2 = 100 - (entry_price / stoploss) * 100
                close_order(order, lows[i], df["Close time text"].iloc[i], 0 if pnl2 <= 0 else 1, pnl2)
            elif fastd[i - 1] > 80 and fastd[i] <= 80 and is_bearish_divergence:
                order[2]="bear_div_" + order[2]
                close_order(order, lows[i], df["Close time text"].iloc[i], 0 if pnl < 0 else 1, pnl)
            elif (ema_type == "ema8" and lows[i] < ema8[i]) or (ema_type == "ema21" and lows[i] < ema21[i]):
                close_order(order, lows[i], df["Close time text"].iloc[i], 0 if pnl < 0 else 1, pnl)
            else:
                temp_orders.append(order)
    orders = temp_orders
    # 2order closer end
    # ##################



    # btc counter
    # while btc_df["Close time"].iloc[btc_i] < df["Close time"].iloc[i]:
    #     btc_i += 1



    # order opener
    # btc_condition = btc_df["ema8"].iloc[btc_i] > btc_df["ema21"].iloc[btc_i] and btc_df["ema21"].iloc[btc_i] > btc_df["ema55"].iloc[btc_i] and btc_df["Close"].iloc[btc_i] > btc_df["ema233"].iloc[btc_i]
    cond = df["accessible"].iloc[i] and df["extremium"].iloc[i] and df["ema8"].iloc[i] > df["ema21"].iloc[i] and df["ema21"].iloc[i] > df["ema55"].iloc[i] and df["Close"].iloc[i] > df["ema233"].iloc[i]
    if opens[i] < closes[i] and cond and len(orders) == 0: # and btc_condition: # df["accessible"].iloc[i]
        is_under_ema21 = False
        is_under_ema8 = False

        # under in which ema
        for j in range(i - 1, 2, -1):
            if rsi[j - 1] < 50:
                break
            if closes[j] < ema21[j]:
                is_under_ema21 = True
            if closes[j] < ema8[j]:
                is_under_ema8 = True

        # create_order("extremium_trend", ema21[i] if is_under_ema8 else ema8[i], "ema21" if is_under_ema8 else "ema8", closes[i], df["Close time text"].iloc[i])
        create_order("extremium_trend", closes[i] * 0.995, "ema21" if is_under_ema8 else "ema8", closes[i], df["Close time text"].iloc[i])


# save result as json file
log_file_name = f"{DIR}/{TRADE_SYMBOL}_{TRADE_INTERVAL}_orders.json"
with open(log_file_name, "w") as outfile:
    json.dump(closed_orders, outfile)
