import datetime
import math
import time
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt


class TradeBot:
    def __init__(self, cash=10000, max_position_count = 10) -> None:
        self.cash = cash
        self.max_position_count = max_position_count
        self.all = []
        self.positions = []
        self.percentage = 0
        self.today_percentage = 0
        self.last_day = 0
        self.block_trading_until = 0
    
    def open_position(self, pos):
        if pos['entry_time'] <= self.block_trading_until:
            return None;
        
        empty = self.max_position_count - len(self.positions)
        
        if empty > 0:
            pos.amount = 10
            # pos.amount = self.cash / empty
            self.cash = self.cash - pos.amount
            self.positions.append(pos)
            return True
        
        return False
    
    def close_position(self, pos):
        self.positions.remove(pos)
        self.all.append(pos)
        
        self.cash += pos.amount * (pos.win_percentage / 10 + 1)
        
        self.percentage = self.percentage + pos.win_percentage
        self.today_percentage = self.today_percentage + pos.win_percentage
        
        if self.today_percentage <= -5:
            dt = datetime.datetime.fromtimestamp(pos['close_time'] / 1000)
            dt += datetime.timedelta(days=1)
            dt = dt.replace(hour=0, minute=0, second=0, microsecond=0)
            
            self.close_all_positions()
            self.today_percentage = 0
            self.block_trading_until = dt.timestamp() * 1000

    def get_position_with_min_close_time(self):
        if len(self.positions) == 0:
            return ""
        
        min_time = self.positions[0]['close_time']
        min_index = 0
        
        for i in range(len(self.positions)):
            time = self.positions[i]['close_time']
            
            if time < min_time:
                min_time = time
                min_index = i
        
        return self.positions[min_index]


    def close_all_positions(self):
        for pos in self.positions:
            self.close_position(pos)
    

    def update_time(self, ms):
        dt = datetime.datetime.fromtimestamp(ms / 1000)
        if self.last_day != dt.weekday():
            self.last_day = dt.weekday()
            self.today_percentage = 0
        

    def handle_position(self, pos):
        self.update_time(pos['entry_time'])
        
        c_pos = self.get_position_with_min_close_time()
        
        if not isinstance(c_pos, str):
            if pos['entry_time'] < c_pos['close_time']:
                return
            else:
                self.close_position(c_pos)
        
        self.open_position(pos)


def run():
  t_start = time.time()

  df = pd.read_csv("result_test.csv")
  df = df.sort_values(['entry_time', 'trade_symbol'])

  # Filters
  df = df[df['trade_interval'] == '15m']
  df = df[df['strategy'] == 'bearish_divergence']
  df = df[(df['stoploss'] > 1) & (df['stoploss'] < 10)]
  df = df[(df['entry_time'] > 1617217200000) & (df['entry_time'] < 1619809200000)]

  bot = TradeBot()

  for i, pos in df.iterrows():
      bot.handle_position(pos)
    #   print(pos)
    #   break


  t_end = time.time()

  print("All positions: {}".format(df.shape))
  print("Percentage: {}".format(bot.percentage))
  print("Cash: {}".format(bot.cash))
  print("Opened pos: {}".format(len(bot.all)))
  print("The time taken: ", t_end - t_start, "seconds")
  
  pd.DataFrame(bot.all).to_csv('result.csv')
  
if __name__ == "__main__":
    run()