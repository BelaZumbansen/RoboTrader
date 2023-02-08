import pandas_market_calendars as mcal
import pandas as pd
import numpy as np
import simulator as sim
import datetime
import progressbar

def get_backtest_tickers() -> list[str]:
  """
  Return Tickers you would like to use to run your backtesting.
  """
  return ['AAPL', '^GSPC', 'MSFT', 'AMZN']

def backtest(starting_balance=100000, start_date='2019-01-01', end_date='2020-12-31', tickers=None) -> str:
  """
  Backtest Trading Strategy on historical date range and ticker set of your choice
  """

  # Retrieve valid trading Days
  trading_days = sim.get_trading_days(start_date, end_date)

  bar = progressbar.ProgressBar(maxval=len(trading_days), \
    widgets=[progressbar.Bar('=', '[', ']'), ' ', progressbar.Percentage()])

  # Start with $100000
  if not starting_balance:
    balance = 100000
  else:
    balance = starting_balance

  starting_balance = balance

  # No Past Transactions and no Open Positions
  transaction_log = []
  positions = dict()

  # Retrieve Tickers we wish to use for this simulation
  if not tickers:
    tickers = get_backtest_tickers()

  # Start up the progress bar
  bar.start()

  # Execute Trading Strategy on each market day of the specified date range
  # Note: We are operating under the guise that analysis is done directly prior to the market opening at 9am EST
  # and we utilize the opening price on that day if we buy or sell
  for i in range(1, len(trading_days)):
    balance = sim.trading_day(tickers, trading_days[i], trading_days[i-1], positions, balance, transaction_log, backtest=True)
    bar.update(i)

  # Mark Progress as Finished
  bar.finish()

  # Exit all current positions to see how well the simulation did
  #print('Holding Positions')
  #print(positions)
  balance += sim.exit_all_positions(trading_days[-1], positions, transaction_log, backtest=True)

  result_msg = ''.join(['Invested $', str(starting_balance), ' and ended up with $', 
  str(balance), 
  '. This is a profit of ', 
  str(int(((balance - starting_balance)/starting_balance)*100)),
  '%'])

  #print(result_msg)
  #print(transaction_log)

  return result_msg


if __name__ == "__main__":
  backtest()
