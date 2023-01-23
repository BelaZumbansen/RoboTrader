import pandas as pd
import yfinance as yf
import numpy as np
import matplotlib.pyplot as plt

def EMA(data, window):
  
  ema = data.ewm(
    span = window,
    adjust=False).mean()
  ema.columns = ['EMA']
  return ema

def MACD(data, a=12, b=26, c=9):

  MACD_line = EMA(data, a) - EMA(data, b)
  signal_line = MACD_line.ewm(span=c, adjust=False).mean()
  histogram = MACD_line - signal_line

  return MACD_line, signal_line, histogram

def evaluate_MACD(data, visualize=False):

  df = data
  close = data['Close']

  MACD_line, signal_line, histogram = MACD(close)

  if visualize:
    plt.plot(MACD_line, 'g', label = 'MACD Line')
    plt.plot(signal_line, 'r', label = 'Signal Line')
    plt.axhline(0)
    plt.show()

  MACD_list = MACD_line.tolist()
  signal_list = signal_line.tolist()

  buy_signal = [False] * len(MACD_list)
  sell_signal = [False] * len(MACD_list)

  macd = 1
  signal = 2

  prev = -1
  for i in range(len(MACD_list)):

    greater = -1
    if MACD_list[i] >= signal_list[i]:
      greater = macd
    else:
      greater = signal
    
    if greater != prev:

      if not prev == -1 and (prev == signal and MACD_list[i] < 0):
        buy_signal[i] = True
      elif not prev == -1 and (prev == macd and MACD_list[i] > 0):
        sell_signal[i] = True

    prev = greater

  output = pd.DataFrame({
    'Close': close
  })

  output['MACD'] = MACD_list
  output['Signal'] = signal_list
  output['Buy'] = buy_signal
  output['Sell'] = sell_signal

  buy_locs = output.loc[output['Buy'] == True] 
  sell_locs = output.loc[output['Sell'] == True]

  if visualize:
    print('Buy Signals')
    print(buy_locs)

    print('---------------------------------------')
    print('Sell Signals')
    print(sell_locs)

  return output

