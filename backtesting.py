import pandas_market_calendars as mcal
import pandas as pd
import numpy as np
import simulator as sim
import datetime

def get_trading_days(start_date, end_date):

  nyse = mcal.get_calendar('NYSE')
  schedule = nyse.schedule(start_date=start_date, end_date=end_date)
  date_range = mcal.date_range(schedule, frequency='1D')

  date_series = pd.Series(date_range.format())
  days = np.asarray(date_series)

  for i in range(len(days)):
    days[i] = days[i][:10]
  
  return days

def get_backtest_tickers():
  return ['AAPL', '^GSPC', 'MSFT', 'AMZN']

def backtest():

  # Retrieve valid trading Days
  trading_days = get_trading_days('2019-01-01', '2023-01-01')

  # Start with $100 000
  balance = 100000

  # No Past Transactions and no Open Positions
  transaction_log = []
  positions = dict()

  # Retrieve Tickers we wish to use for this simulation
  tickers = get_backtest_tickers()

  for date in trading_days:
    balance = sim.trading_day(tickers, date, positions, balance, transaction_log)
  
  # Exit all positions to see how well the simulation did
  balance += sim.exit_all_positions(trading_days[-1], positions, transaction_log)

  print('Invested $100 000 and ended up with $' + str(balance) + '. This is a profit of ' + str(int((balance - 100000)/100000)*100) + '%')

  


  


if __name__ == "__main__":
  backtest()
