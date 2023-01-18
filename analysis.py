import pandas_datareader as pdr
import datetime as dt
import yfinance as yf
import numpy as np
import math
import matplotlib.pyplot as plt
from security import StockPosition
from security import Security

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

def calculate_high(ticker, period='5d'):

  stock = yf.download(ticker, period=period)
  stock = stock['Adj Close']

  return max(stock)

def current_price(ticker):

  stock = yf.Ticker(ticker)
  return stock.info['currentPrice']

def reached_risk_level(position : StockPosition):
  return (position.buy_price * position.risk_level) >= current_price(position.ticker)

calculate_volatility('AAPL', visualize=True)