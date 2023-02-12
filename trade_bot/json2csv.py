import sys
import json
import numpy as np
import pandas as pd
import datetime

with open("BTCUSDT_5m.json") as json_file:
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

for i in range(1, len(df)):
    df.loc[i, 'Change'] = ( df.loc[i, 'Close'] - df.loc[i - 1, 'Close'] ) / 100

df.to_csv("./btc.csv")