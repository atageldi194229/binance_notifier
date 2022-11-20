import json
import sys
import json
import numpy as np
import talib
import bot
import pandas
import datetime


class StrategyManager:
    def __init__(self, filepath, trade_symbol, trade_interval):
        # read json file and calculate
        with open(filepath) as json_file:
            rows = json.load(json_file)
        
        opens = np.array(rows)[:,1]
        self.opens = list(map(float, opens))
        closes = np.array(rows)[:,4]
        self.closes = list(map(float, closes))
        highs = np.array(rows)[:,2]
        self.highs = list(map(float, highs))
        lows = np.array(rows)[:,3]
        self.lows = list(map(float, lows))
        
        np_closes = np.array(closes)
        self.macd, self.macdsignal, self.macdhist = talib.MACD(np_closes, fastperiod=12, slowperiod=26, signalperiod=9)
        # apo = talib.APO(np_closes, fastperiod=8, slowperiod=21)
        self.ema233 = talib.EMA(np_closes, timeperiod=233)
        self.ema55 = talib.EMA(np_closes, timeperiod=55)
        self.ema21 = talib.EMA(np_closes, timeperiod=21)
        self.ema8 = talib.EMA(np_closes, timeperiod=8)

        self.rsi = talib.RSI(np_closes, timeperiod=14)

