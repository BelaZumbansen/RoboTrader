import pandas as pd
import datetime as dt
import yfinance as yf
import numpy as np
import math
import matplotlib.pyplot as plt
import supertrend
import macd_analysis

def calculate_volatility(ticker:str, period='5y', visualize=False) :
  
  stock = yf.download(ticker, period=period)

  stock = stock['Adj Close']
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


def evaluate_trends(ticker, start_date='2022-01-01', end_date=None, visualize=False):

  data = None
  if end_date:
    data = yf.download(ticker, start=start_date, end=end_date, period='1d')
  else:
    data = yf.download(ticker, start=start_date, period='1d')

  
  super_trend_res = supertrend.generate_trend(data, visualize)
  macd_res = macd_analysis.evaluate_MACD(data, visualize)

  trend_analysis = pd.concat([super_trend_res, macd_res], axis=1)

  buy_locs = trend_analysis.loc[(trend_analysis['Trend'] == True) & (trend_analysis['Buy'] == True)]
  sell_locs = trend_analysis.loc[(trend_analysis['Trend'] == False) | (trend_analysis['Sell'] == True)]

  print(buy_locs)

  return trend_analysis, buy_locs, sell_locs


def calculate_high(ticker, period='5d'):

  stock = yf.download(ticker, period=period)
  stock = stock['Adj Close']

  return max(stock)

def current_price(ticker):

  stock = yf.Ticker(ticker)
  return stock.info['currentPrice']

#calculate_volatility('AAPL', visualize=True)
evaluate_trends('AAPL')
