import pandas as pd
import datetime as dt
import yfinance as yf
import numpy as np
import math
import matplotlib.pyplot as plt
import supertrend
import macd_analysis

def calculate_volatility(ticker:str, period='5y', visualize=False) -> float:
  """
  Calculate the volatility of a stock based on analysis done on the given time period
  """

  # Retrieve historical stock data
  stock = yf.download(ticker, period=period)

  # We will perform our analysis using the Adjusted Closing price
  stock = stock['Adj Close']

  # Get log return
  stock_log_return = np.log(stock/stock.shift())

  stock_volatility = stock_log_return.std() * np.sqrt(252)
  stock_volatility = stock_volatility * 100

  if visualize:
    str_vol = str(round(stock_volatility, 4))

    fig, ax = plt.subplots()
    stock_log_return.hist(ax=ax, bins=50, alpha=0.6, color='b')
    ax.set_xlabel("Log return")
    ax.set_ylabel("Freq of log return")
    ax.set_title(ticker + " Volatility: " + str_vol + "%")

    plt.show()
  
  return stock_volatility


def parse_days(buy_signals : pd.DataFrame, sell_signals : pd.DataFrame):
  """
  Helper method to retrieve Numpy Arrays of the Buy and Sell Dates so they can be indexed properly
  """

  # Convert the indices to Pandas Series
  buy_date_series = pd.Series(buy_signals.index.format(), dtype=pd.StringDtype())
  sell_date_series = pd.Series(sell_signals.index.format(), dtype=pd.StringDtype())

  # Convert to Numpy Arrays
  buy_days = np.asarray(buy_date_series)
  sell_days = np.asarray(sell_date_series)

  # Truncate dates to format 'YYYY-MM-DD'
  for i in range(len(buy_days)):
    buy_days[i] = buy_days[i][:10]

  # Truncate dates to format 'YYYY-MM-DD'
  for i in range(len(sell_days)):
    sell_days[i] = sell_days[i][:10]

  return buy_days, sell_days

def evaluate_trends(ticker : str, start_date='2022-01-01', end_date=None, visualize=False):
  """
  Perform market analysis on the givwn stock. This analysis will consist of analyzing two different types of
  trends.
  Generate a buy signal if either trend indicates to buy.
  Generate a sell signal if either trend indicates to sell.
  """

  data = None
  # Download historical stock data using the Yahoo Finance API
  if end_date:
    data = yf.download(ticker, start=start_date, end=end_date, period='1d', progress=False)
  else:
    data = yf.download(ticker, start=start_date, period='1d', progress=False)

  # Apply adjusted Supertrend Analysis
  super_trend_res = supertrend.generate_trend(data, visualize)
  
  # Apply MACD Analysis
  macd_res = macd_analysis.evaluate_MACD(data, visualize)

  # Concatenate results
  trend_analysis = pd.concat([super_trend_res, macd_res], axis=1)

  # Find all rows where either trend indicates that we should be buying
  buy_locs = trend_analysis.loc[(trend_analysis['Trend'] == True) | (trend_analysis['Buy'] == True)]

  # Find all rows where either trend indicates that we should sell
  sell_locs = trend_analysis.loc[(trend_analysis['Trend'] == False) | (trend_analysis['Sell'] == True)]

  # Reformat the dates
  buy_days, sell_days = parse_days(buy_locs, sell_locs)

  # Return the analysis in case the client wishes to further use it and the list of buy and sell dates
  return trend_analysis, buy_days, sell_days


def calculate_high(ticker : str, period='5d') -> float:
  """
  Determine the highest price of this stock within the given time period.
  """

  stock = yf.download(ticker, period=period)
  stock = stock['Adj Close']

  return max(stock)

def current_price(ticker : str) -> float:
  """
  Retrieve the current price of a stock
  """

  stock = yf.Ticker(ticker)
  return stock.info['currentPrice']
