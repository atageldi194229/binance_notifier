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

def isCandleAboveEMA55(ema55, op, cl):
    return ema55 < op and ema55 < cl

# read json file and calculate
with open(FILE_PATH_5M) as json_file:
    data_5m = json.load(json_file)

rows = data_5m
opens = np.array(rows)[:,4]
opens = list(map(float, opens))
closes = np.array(rows)[:,4]
closes = list(map(float, closes))
highs = np.array(rows)[:,2]
highs = list(map(float, highs))
lows = np.array(rows)[:,3]
lows = list(map(float, lows))


np_closes = np.array(closes)
macd, macdsignal, macdhist = talib.MACD(np_closes, fastperiod=12, slowperiod=26, signalperiod=9)
# apo = talib.APO(np_closes, fastperiod=8, slowperiod=21)
ema55 = talib.EMA(np_closes, timeperiod=55)

# # check if macdhist is changing colors
macdhist_last_a, macdhist_last_b = macdhist[-2], macdhist[-1]
# apo_last_a, apo_last_b = apo[-2], apo[-1]

# b1 = apo[-2] < 0 and apo[-1] >= 0
b2 = macdhist[-2] < 0 and macdhist[-1] >= 0
b3 = macdhist[-2] > 0 and macdhist[-1] <= 0
# b4 = ema55[-1] < opens[-1] and ema55[-1] < closes[-1]
b4 = isCandleAboveEMA55(ema55[-1], opens[-1], closes[-1])

if  not (b2 or b3 or b4):
    sys.exit()

rsi = talib.RSI(np_closes, timeperiod=14)

# print(len(closes), len(macdhist))

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
bullish_divergence_ema55_index = -1
bullish_divergence_then_positive_apo_index = -1
bearish_divergence_3_index = -1
is_last_bullish = False

green_to_red_indexes = []
red_to_green_indexes = []

for i in range(1, len(macdhist)):
    h_a = macdhist[i - 1]
    h_b = macdhist[i]
    
    if h_a < 0 and h_b >= 0:
        last_red_index = i - 1
        red_to_green_indexes.append(last_red_index)
        
        min_value = min(lows[last_green_index + 1: last_red_index + 1])
        min_values.append(min_value)
        
        # rsi min values
        rsi_min_value = min(rsi[last_green_index + 1: last_red_index + 1])
        rsi_min_values.append(rsi_min_value)
        
        # # trend up
        # if len(max_values) > 1 and len(min_values) > 1:
        #     a_max, b_max = max_values[-2], max_values[-1]
        #     a_min, b_min = min_values[-2], min_values[-1]
        #     if a_max < b_max and a_min < b_min:
        #         trend_up_index = i
        #         print_date_time(rows[i][0], end=f"   trend_up\n")
        
        
        # bullish divergence
        if len(min_values) > 1 and len(rsi_min_values) > 1:
            a_min, b_min = min_values[-2], min_values[-1]
            rsi_a_min, rsi_b_min = rsi_min_values[-2], rsi_min_values[-1]
            if a_min > b_min and rsi_a_min < rsi_b_min and rsi_a_min < 30:
                bullish_divergence_index = i
                is_last_bullish = True
                print_date_time(rows[i][0], end=f'   bullish_divergence\n')

    
    if h_a > 0 and h_b <= 0:
        last_green_index = i - 1
        green_to_red_indexes.append(last_green_index)

        max_value = max(highs[last_red_index + 1: last_green_index + 1])
        max_values.append(max_value)
        
        rsi_max_value = max(rsi[last_red_index + 1: last_green_index + 1])
        rsi_max_values.append(rsi_max_value)
        
        
        # # trend down
        # if len(max_values) > 1 and len(min_values) > 1:
        #     a_max, b_max = max_values[-2], max_values[-1]
        #     a_min, b_min = min_values[-2], min_values[-1]
        #     if a_max > b_max and a_min < b_min:
        #         trend_down_index = i
        #         print_date_time(rows[i][0], end=f"   tren_down\n")
        
        # bearish divergence
        if len(max_values) > 1 and len(rsi_max_values) > 1:
            a_max, b_max = max_values[-2], max_values[-1]
            rsi_a_max, rsi_b_max = rsi_max_values[-2], rsi_max_values[-1]
            if a_max < b_max and rsi_a_max > rsi_b_max and rsi_a_max > 70:
                bearish_divergence_index = i
                is_last_bullish = False
                print_date_time(rows[i][0], end=f'   bearish_divergence\n')

        # bearish divergence 3
        if len(max_values) > 2 and len(rsi_max_values) > 2:
            a_max, b_max, c_max = max_values[-3], max_values[-2], max_values[-1]
            rsi_a_max, rsi_b_max, rsi_c_max = rsi_max_values[-3], rsi_max_values[-2], rsi_max_values[-1]
            if a_max < b_max and a_max < c_max and rsi_a_max > rsi_b_max and rsi_a_max > rsi_c_max and rsi_a_max > 70:
                bearish_divergence_3_index = i
                is_last_bullish = False
                print_date_time(rows[i][0], end=f'   bearish_divergence_1-3\n')



    # apo_a, apo_b = apo[i - 1], apo[i]
    # if ((apo[i - 2] < 0 and apo[i] >= 1) or (apo[i - 1] < 0 and apo[i] >= 1)) and is_last_bullish: 
    #     bullish_divergence_then_positive_apo_index = i
    #     print_date_time(rows[i][0], end=f'   bullish_divergence_then_positive_apo\n')


    if (not isCandleAboveEMA55(ema55[i-1], opens[i-1], closes[i-1])) and isCandleAboveEMA55(ema55[i], opens[i], closes[i]) and is_last_bullish: 
        bullish_divergence_ema55_index = i
        is_last_bullish = False
        print_date_time(rows[i][0], end=f'   bullish_divergence_above_ema55\n{(ema55[i-1])} {ema55[i]}')

last_signal_index = max([
    trend_up_index,
    trend_down_index,
    bearish_divergence_index,
    # bullish_divergence_index,
    bearish_divergence_3_index,
    bullish_divergence_ema55_index
])

if last_signal_index == -1:
    sys.exit()

if last_signal_index == len(macdhist) - 1:
    print(result)
    bot.bot_send_message(result)