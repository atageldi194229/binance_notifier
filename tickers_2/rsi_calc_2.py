from collections import deque
import json
import logging
import math
import sys
import traceback
import numpy as np
import talib
import bot


# FILE_PATH=".json"
# TRADE_SYMBOL="ETHUSDT"
# RSI_PERIOD = 14
# RSI_OVERBOUGHT = 70
# RSI_OVERSOLD = 30
FILE_PATH = sys.argv[1]
TRADE_SYMBOL = sys.argv[2]
RSI_PERIOD = int(sys.argv[3])
RSI_OVERBOUGHT = int(sys.argv[4])
RSI_OVERSOLD = int(sys.argv[5])
RSI_OVERBOUGHT_MESSAGE = sys.argv[6]
RSI_OVERSOLD_MESSAGE = sys.argv[7]

def overbought_notifier(logs):
    # mess = f"\U2197	RSI BIGGER THAN 70, {self.symbol.upper()} {self.kline_interval} \n{logs}"
    
    # if self.kline_interval == "15m":
    #     mess = "\u1f4cc " + mess  
    mess = f"{RSI_OVERBOUGHT_MESSAGE} \n{logs}"
    bot.bot_send_message(mess)
    print(mess)

def oversold_notifier(logs):
    # mess = f"\U2198 RSI LESS THAN 30, {self.symbol.upper()} {self.kline_interval} \n{logs}"
    
    # if self.kline_interval == "15m":
    #     mess = "\u1f4cc " + mess
    
    mess = f"{RSI_OVERSOLD_MESSAGE} \n{logs}"
    bot.bot_send_message(mess)
    print(mess)

def rsi_calc(closes, symbol, rsi_period, rsi_overbought, rsi_oversold):
    np_closes = np.array(closes)
    rsi = talib.RSI(np_closes, timeperiod=rsi_period)
    
    last_rsi = rsi[-1]
    print("")
    print(f"{symbol} rsi  is {last_rsi}")

    if last_rsi > rsi_overbought:
        overbought_notifier(json.dumps(last_rsi, indent=2))

    if last_rsi < rsi_oversold and last_rsi > 1.0:
        oversold_notifier(json.dumps(last_rsi, indent=2))


# read json file and calculate
with open(FILE_PATH) as json_file:
    data = json.load(json_file)
    rows = data[-252:]
    if len(rows) > 250:
        closes = np.array(rows)[:,4]
        closes = list(map(float, closes))
        rsi_calc(closes, TRADE_SYMBOL, RSI_PERIOD, RSI_OVERBOUGHT,RSI_OVERSOLD)
