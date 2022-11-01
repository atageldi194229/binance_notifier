import sys
import json
import numpy as np
import talib
import bot


FILE_PATH_5M = sys.argv[1] # 5 minute interval kline's file path
FILE_PATH_15M = sys.argv[2] # 15 minute interval kline's file path

def rsi_calc(closes):
    np_closes = np.array(closes)
    rsi = talib.RSI(np_closes, timeperiod=14)    

    for i in reversed(range(len(rsi))):
        el = rsi[i]
        if el < 30:
            return i

    return -1

def apo_calc(closes):
    np_closes = np.array(closes)
    apo = talib.APO(np_closes, fastperiod=10, slowperiod=20)
    
    for i in reversed(range(len(apo) - 2)):
        a = apo[i]
        b = apo[i + 2]
        
        if a < 0 and b > 0:
            return i + 2
    
    return -1

def macd_calc(closes):
    np_closes = np.array(closes)
    macd, macdsignal, macdhist = talib.MACD(closes, fastperiod=12, slowperiod=26, signalperiod=9)
    
    

# read json file and calculate
with open(FILE_PATH_5M) as json_file:
    data_5m = json.load(json_file)
with open(FILE_PATH_15M) as json_file:
    data_15m = json.load(json_file)



rows = data_5m[-252:]
closes = np.array(rows)[:,4]
closes = list(map(float, closes))
rsi_calc(closes)
