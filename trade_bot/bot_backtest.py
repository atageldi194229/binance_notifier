import datetime
import math
import time
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt


class TradeBot:
    def __init__(self, cash=100, max_position_count = 10) -> None:
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
        
        empty = self.posision_available()
        
        if empty > 0:
            pos.amount = 10
            # pos.amount = self.cash / empty
            self.cash = self.cash - pos.amount
            self.positions.append(pos)
            return True
        
        return False
    
    def close_position(self, pos):
        positions = []
        
        for e in self.positions:
            # print(type(e), type(pos))
            if not e.equals(pos):
                positions.append(e)
        
        self.positions = positions
        
        
        # self.positions.remove(pos)
        self.all.append(pos)
        
        self.cash += pos.amount * (pos.win_percentage / 10 + 1)
        
        self.percentage = self.percentage + pos.win_percentage
        self.today_percentage = self.today_percentage + pos.win_percentage
        
        if self.today_percentage <= -5:
            dt = datetime.datetime.fromtimestamp(pos['entry_time'] / 1000)
            dt += datetime.timedelta(days=1)
            dt = dt.replace(hour=0, minute=0, second=0, microsecond=0)
            
            self.close_all_positions()
            self.today_percentage = 0
            self.block_trading_until = dt.timestamp() * 1000

    def close_all_positions_under_time(self, time):
        closables = []
        
        for pos in self.positions:
            if pos['close_time'] < time:
                closables.append(pos)
        
        for pos in closables:
            self.close_position(pos)
            
    
    def close_all_positions(self):
        for pos in self.positions:
            self.close_position(pos)
    

    def update_time(self, ms):
        dt = datetime.datetime.fromtimestamp(ms / 1000)
        if self.last_day != dt.weekday():
            self.last_day = dt.weekday()
            self.today_percentage = 0
        

    def posision_available(self):
        return self.max_position_count - len(self.positions);


    def handle_position(self, pos):
        self.update_time(pos['entry_time'])
        
        self.close_all_positions_under_time(pos['entry_time'])
        
        res = self.open_position(pos)
        
        if res == None:
            return (-1, -1)
        elif res == False:
            return (0, -1)
        else:
            return (1, len(self.positions))
        


def strategy_backtest(df, strategy):
    t_start = time.time()
    
    # Filters
    df2 = df.copy()
    df2 = df2[df2['trade_interval'] == '15m']
    df2 = df2[df2['strategy'] == strategy]
    df2 = df2[(df2['stoploss'] > 1) & (df2['stoploss'] < 10)]
    #   df = df[(df['entry_time'] > 1617217200000) & (df['entry_time'] < 1619809200000)]

    actions = []
    position_counts = []
    bot = TradeBot()
    
    for i, pos in df2.iterrows():
        action, pos_count = bot.handle_position(pos)
        actions.append(action)
        position_counts.append(pos_count)
    
    bot.close_all_positions()

    df2['action'] = actions
    df2['position_count'] = position_counts
      
    df2.to_csv(f'./result_debug_{strategy}.csv', )
    pd.DataFrame(bot.all).to_csv(f'./result_{strategy}.csv')

    print("For Strategy: ", strategy)
    print("All positions: {}".format(df2.shape))
    print("Percentage: {}".format(bot.percentage))
    print("Cash: {}".format(bot.cash))
    print("Opened pos: {}".format(len(bot.all)))
    t_end = time.time()
    print("The time taken: ", t_end - t_start, "seconds")
    print("\n")
    


def run():

  df = pd.read_csv("backtest_data.csv")
  df = df.sort_values(['entry_time', 'trade_symbol'])

  print(df['strategy'].unique())

  for strategy in df['strategy'].unique():
    strategy_backtest(df, strategy)
    

if __name__ == "__main__":
    run()