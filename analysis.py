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


def parse_days(buy_signals, sell_signals):
    
  buy_date_series = pd.Series(buy_signals.index.format(), dtype=pd.StringDtype())
  sell_date_series = pd.Series(sell_signals.index.format(), dtype=pd.StringDtype())

  buy_days = np.asarray(buy_date_series)
  sell_days = np.asarray(sell_date_series)

  for i in range(len(buy_days)):
    buy_days[i] = buy_days[i][:10]

  for i in range(len(sell_days)):
    sell_days[i] = sell_days[i][:10]

  return buy_days, sell_days

def evaluate_trends(ticker, start_date='2022-01-01', end_date=None, visualize=False):

  data = None
  if end_date:
    data = yf.download(ticker, start=start_date, end=end_date, period='1d', progress=False)
  else:
    data = yf.download(ticker, start=start_date, period='1d', progress=False)

  super_trend_res = supertrend.generate_trend(data, visualize)
  macd_res = macd_analysis.evaluate_MACD(data, visualize)

  trend_analysis = pd.concat([super_trend_res, macd_res], axis=1)

  buy_locs = trend_analysis.loc[(trend_analysis['Trend'] == True) | (trend_analysis['Buy'] == True)]
  sell_locs = trend_analysis.loc[(trend_analysis['Trend'] == False) | (trend_analysis['Sell'] == True)]

  buy_days, sell_days = parse_days(buy_locs, sell_locs)

  return trend_analysis, buy_days, sell_days


def calculate_high(ticker, period='5d'):

  stock = yf.download(ticker, period=period)
  stock = stock['Adj Close']

  return max(stock)

def current_price(ticker):

  stock = yf.Ticker(ticker)
  return stock.info['currentPrice']
