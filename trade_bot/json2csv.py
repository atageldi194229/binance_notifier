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

df.pct_change(1, "Close")

df.to_csv("./btc.csv")