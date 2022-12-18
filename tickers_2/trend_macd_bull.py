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

# # check if macdhist is changing colors
macdhist_last_a, macdhist_last_b = macdhist[-2], macdhist[-1]
# apo_last_a, apo_last_b = apo[-2], apo[-1]

# b1 = apo[-2] < 0 and apo[-1] >= 0
b2 = macdhist[-2] < 0 and macdhist[-1] >= 0
b3 = macdhist[-2] > 0 and macdhist[-1] <= 0
# b4 = ema55[-1] < opens[-1] and ema55[-1] < closes[-1]
b4 = isCandleAboveEMA(ema21[-1], opens[-1], closes[-1])
# b5 = not isEMA4Down(ema233[-2], ema55[-2], ema21[-2], ema8[-2]) and isEMA4Down(ema233[-1], ema55[-1], ema21[-1], ema8[-1])
# b6 = not isEMA4Up(ema233[-2], ema55[-2], ema21[-2], ema8[-2]) and isEMA4Up(ema233[-1], ema55[-1], ema21[-1], ema8[-1])

# if  not (b2 or b3 or b4):
#     sys.exit()

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

volume_trend_long_index = -1
extreme_volume_up_index = -1
extreme_volume_down_index = -1

is_last_bearish_divergence = 0

green_to_red_indexes = []
red_to_green_indexes = []

for i in range(1, len(macdhist)):
    # extreme_volume_up
    if c[i] and opens[i] > ema8[i] and opens[i] > ema233[i] and opens[i] < closes[i]:
        stoploss = round(100 - (( ema21[i] / closes[i] ) * 100), 2)
        print_date_time(rows[i][0], end=f'   extreme_volume_up  {stoploss} \n')
        extreme_volume_up_index = i
    
    # continue
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
        
        
        if last_bullish_for_cancel == 2:
            last_bullish_for_cancel = 0
        
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
                last_bullish_for_cancel = 1
                is_last_bearish_divergence = 0
                stoploss = round(100 - (( b_min / closes[i] ) * 100), 2)
                print_date_time(rows[i][0], end=f'   bullish_divergence  {stoploss} \n')

        # # macd price bullish
        # if len(min_values) > 1:
        #     green_max_value = max_values[-1]
        #     red_max_value = max(highs[last_green_index + 1: last_red_index + 1])
        #     if green_max_value < red_max_value and min_values[-2] < min_values[-1]:
        #         macd_price_bullish_index = i
        #         is_last_bullish = False
        #         stoploss = round(100 - (( min_values[-1] / closes[i] ) * 100), 2)
        #         print_date_time(rows[i][0], end=f'   macd_price_bullish  {stoploss}\n')
    
    if h_a > 0 and h_b <= 0:
        last_green_index = i - 1
        green_to_red_indexes.append(last_green_index)

        max_value = max(highs[last_red_index + 1: last_green_index + 1])
        max_values.append(max_value)
        
        rsi_max_value = max(rsi[last_red_index + 1: last_green_index + 1])
        rsi_max_values.append(rsi_max_value)
        
        if last_bullish_for_cancel == 1:
            last_bullish_for_cancel = 2
        
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
                last_bullish_for_cancel = 0
                is_last_bearish_divergence = 1
                stoploss = round(100 - (( closes[i] / b_max ) * 100), 2)
                print_date_time(rows[i][0], end=f'   bearish_divergence  {stoploss}\n')

        # bearish divergence 3
        if len(max_values) > 2 and len(rsi_max_values) > 2:
            a_max, b_max, c_max = max_values[-3], max_values[-2], max_values[-1]
            rsi_a_max, rsi_b_max, rsi_c_max = rsi_max_values[-3], rsi_max_values[-2], rsi_max_values[-1]
            if a_max < b_max and b_max < c_max and rsi_a_max > rsi_b_max and rsi_a_max > rsi_c_max and rsi_a_max > 70:
                bearish_divergence_3_index = i
                is_last_bullish = False
                last_bullish_for_cancel = 0
                is_last_bearish_divergence = 1
                stoploss = round(100 - (( closes[i] / c_max ) * 100), 2)
                print_date_time(rows[i][0], end=f'   bearish_divergence_1-3  {stoploss}\n')



    # apo_a, apo_b = apo[i - 1], apo[i]
    # if ((apo[i - 2] < 0 and apo[i] >= 1) or (apo[i - 1] < 0 and apo[i] >= 1)) and is_last_bullish: 
    #     bullish_divergence_then_positive_apo_index = i
    #     print_date_time(rows[i][0], end=f'   bullish_divergence_then_positive_apo\n')


    # bullish divergence above
    if (not isCandleAboveEMA(ema21[i-1], opens[i-1], closes[i-1])) and isCandleAboveEMA(ema21[i], opens[i], closes[i]) and is_last_bullish: 
        bullish_divergence_ema21_index = i
        is_last_bullish = False
        stoploss = round(100 - (( min_values[-1] / closes[i] ) * 100), 2)
        print_date_time(rows[i][0], end=f'   bullish_divergence_above_ema21  {stoploss}\n')

    if last_bullish_for_cancel == 2 and min_values[-1] > lows[i] and rsi_min_values[-1] > rsi[i]:
        bullish_divergence_canceled_ll_index = i
        last_bullish_for_cancel = 0
        print_date_time(rows[i][0], end=f'   bullish_divergence_canceled_ll  0\n')
    
    if is_last_bearish_divergence == 1 and closes[i] < ema21[i]:
        is_last_bearish_divergence = 2
        bearish_divergence_below_ema21 = i
        stoploss = round(100 - (( closes[i] / max_values[-1] ) * 100), 2)
        print_date_time(rows[i][0], end=f'   bearish_divergence_below_ema21  {stoploss}\n')

    if is_last_bearish_divergence == 2 and rsi[i] <= 40:
        is_last_bearish_divergence = 0
        bearish_divergence_below_rsi40 = i
        stoploss = round(100 - (( closes[i] / max_values[-1] ) * 100), 2)
        print_date_time(rows[i][0], end=f'   bearish_divergence_below_rsi40  {stoploss}\n')
    
    
    # if not isEMA4Down(ema233[i-1], ema21[i-1], ema21[i-1], ema8[i-1]) and isEMA4Down(ema233[i], ema55[i], ema21[i], ema8[i]):
    #     ema_4x_above_index = i
    #     print_date_time(rows[i][0], end=f'   EMA 4x above, down\n')
    #     bot.bot_send_message(result)

    # if not isEMA4Up(ema233[i-1], ema55[i-1], ema21[i-1], ema8[i-1]) and isEMA4Up(ema233[i], ema55[i], ema21[i], ema8[i]):
    #     ema_4x_below_index = i
    #     print_date_time(rows[i][0], end=f'   EMA 4x below, up\n')
    #     bot.bot_send_message(result)

last_signal_index = max([
    # trend_up_index,
    # trend_down_index,
    bearish_divergence_index,
    # bullish_divergence_index,
    bearish_divergence_3_index,
    bullish_divergence_ema21_index,
    bearish_divergence_below_ema21,
    bearish_divergence_below_rsi40,
    bullish_divergence_canceled_ll_index,
    extreme_volume_up_index,
    # ema_4x_above_index,
    # ema_4x_below_index,
    # macd_price_bullish_index
])

if last_signal_index == -1:
    sys.exit()

if last_signal_index == len(macdhist) - 1:
    print(result)
    bot.bot_send_message(result)