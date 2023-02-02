import pandas_market_calendars as mcal
import pandas as pd
import numpy as np
import simulator as sim
import datetime
import progressbar

def get_trading_days(start_date : str, end_date : str) -> np.ndarray:
  """
  Retrieve all valid Tradings days on the New York Stock Exchange between the given
  start date and end date. Return as Numpy Array.
  """

  # Initialize NYSE Calendar
  nyse = mcal.get_calendar('NYSE')

  # Format Date Range
  schedule = nyse.schedule(start_date=start_date, end_date=end_date)
  date_range = mcal.date_range(schedule, frequency='1D')

  # Convert to Numpy Array
  date_series = pd.Series(date_range.format())
  days = np.asarray(date_series)

  # Truncate the Date strings to 'YYYY-MM-DD'
  for i in range(len(days)):
    days[i] = days[i][:10]
  
  return days

def get_backtest_tickers() -> list[str]:
  """
  Return Tickers you would like to use to run your backtesting.
  """
  return ['AAPL', '^GSPC', 'MSFT', 'AMZN']

def backtest():
  """
  Backtest Trading Strategy on historical date range and ticker set of your choice
  """

  # Retrieve valid trading Days
  trading_days = get_trading_days('2019-01-01', '2020-12-31')

  bar = progressbar.ProgressBar(maxval=len(trading_days), \
    widgets=[progressbar.Bar('=', '[', ']'), ' ', progressbar.Percentage()])

  # Start with $100000
  balance = 100000

  # No Past Transactions and no Open Positions
  transaction_log = []
  positions = dict()

  # Retrieve Tickers we wish to use for this simulation
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
  print('Holding Positions')
  print(positions)
  balance += sim.exit_all_positions(trading_days[-1], positions, transaction_log, backtest=True)

  print('Invested $100000 and ended up with $' + str(balance) + '. This is a profit of ' + str(int(((balance - 100000)/100000)*100)) + '%')
  print(transaction_log)

if __name__ == "__main__":
  backtest()
