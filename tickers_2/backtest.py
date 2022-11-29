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

takeprofit = 2

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


np_closes = np.array(closes)
macd, macdsignal, macdhist = talib.MACD(np_closes, fastperiod=12, slowperiod=26, signalperiod=9)
# apo = talib.APO(np_closes, fastperiod=8, slowperiod=21)
ema233 = talib.EMA(np_closes, timeperiod=233)
ema55 = talib.EMA(np_closes, timeperiod=55)
ema21 = talib.EMA(np_closes, timeperiod=21)
ema8 = talib.EMA(np_closes, timeperiod=8)

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

is_last_bearish_divergence = 0

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
                create_order("bullish_divergence", takeprofit, stoploss, closes[i], rows[i][6])

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
                create_order("bearish_divergence", takeprofit, stoploss, closes[i], rows[i][6])

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
                create_order("bearish_divergence_1-3", takeprofit, stoploss, closes[i], rows[i][6])



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
        create_order("bullish_divergence_above_ema21", takeprofit, stoploss, closes[i], rows[i][6])


    if last_bullish_for_cancel == 2 and min_values[-1] > lows[i] and rsi_min_values[-1] > rsi[i]:
        bullish_divergence_canceled_ll_index = i
        last_bullish_for_cancel = 0
        print_date_time(rows[i][0], end=f'   bullish_divergence_canceled_ll  0\n')
        # create_order("bullish_divergence_canceled_ll", takeprofit, stoploss, closes[i], rows[i][6])
    
    if is_last_bearish_divergence == 1 and closes[i] < ema21[i]:
        is_last_bearish_divergence = 2
        bearish_divergence_below_ema21 = i
        stoploss = round(100 - (( closes[i] / max_values[-1] ) * 100), 2)
        print_date_time(rows[i][0], end=f'   bearish_divergence_below_ema21  {stoploss}\n')
        create_order("bearish_divergence_below_ema21", takeprofit, stoploss, closes[i], rows[i][6])

    if is_last_bearish_divergence == 2 and rsi[i] <= 40:
        is_last_bearish_divergence = 0
        bearish_divergence_below_rsi40 = i
        stoploss = round(100 - (( closes[i] / max_values[-1] ) * 100), 2)
        print_date_time(rows[i][0], end=f'   bearish_divergence_below_rsi40  {stoploss}\n')
        create_order("bearish_divergence_below_rsi40", takeprofit, stoploss, closes[i], rows[i][6])
    
    
    # if not isEMA4Down(ema233[i-1], ema21[i-1], ema21[i-1], ema8[i-1]) and isEMA4Down(ema233[i], ema55[i], ema21[i], ema8[i]):
    #     ema_4x_above_index = i
    #     print_date_time(rows[i][0], end=f'   EMA 4x above, down\n')
    #     bot.bot_send_message(result)

    # if not isEMA4Up(ema233[i-1], ema55[i-1], ema21[i-1], ema8[i-1]) and isEMA4Up(ema233[i], ema55[i], ema21[i], ema8[i]):
    #     ema_4x_below_index = i
    #     print_date_time(rows[i][0], end=f'   EMA 4x below, up\n')
    #     bot.bot_send_message(result)


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

        if strategy in ["bullish_divergence", "bullish_divergence_above_ema21"]:
            if mn >= stoploss:
                close_order(order, lows[i], rows[i][6], 0, -stoploss)
            elif mx >= takeprofit:
                close_order(order, highs[i], rows[i][6], 1, takeprofit)
            else:
                temp_orders.append(order)
    orders = temp_orders    
            
log_file_name = f"{DIR}/{TRADE_SYMBOL}_{TRADE_INTERVAL}_orders.json"
with open(log_file_name, "w") as outfile:
    json.dump(closed_orders, outfile)
