import pandas as pd
import datetime as dt
import yfinance as yf
import numpy as np
import matplotlib.pyplot as plt

def calc_HF(high, low):
  return (high + low)/2

# Calculate the Average True Range
def calc_ATR(high, low, close, atr_period):

  # max[(high-low), |high — previous close|, |previous close — low|]
  highMinusLow = high - low
  highMinusPrevClose = abs(high - close.shift())
  prevCloseMinusLow = abs(low - close.shift())

  # True Range
  tr = pd.concat([highMinusLow, highMinusPrevClose, prevCloseMinusLow], axis=1)
  # Take the Maximum
  tr = tr.max(axis=1)

  # Take the average using the ATR period parameter
  atr = tr.ewm(alpha=(1/atr_period), min_periods=atr_period).mean()

  return atr

# Generate a super trend reading on the data using the passed constants
def supertrend(data, atr_period, atr_multiplier):
  
  # Parse data for necessary values
  high = data['High']
  low = data['Low']
  close = data['Close']

  # Calculate HF value for data
  HF = calc_HF(high, low)

  # Calculate Average True Range for data
  ATR = calc_ATR(high, low, close, atr_period)

  # Initialize upper band
  final_upper_band = HF + (atr_multiplier*ATR)

  # Initialize lower band
  final_lower_band = HF - (atr_multiplier*ATR)

  # Initialize trend reading
  trend = [True] * len(data)

  for i in range(1, len(data.index)):

    if close[i] > final_upper_band[i-1]:
      trend[i] = True
    
    elif close[i] < final_lower_band[i-1]:
      trend[i] = False
    
    else:

      trend[i] = trend[i-1]

      if trend[i] and final_lower_band[i] < final_lower_band[i-1]:
        final_lower_band[i] = final_lower_band[i-1]

      if not trend[i] and final_upper_band[i] > final_upper_band[i-1]:
        final_upper_band[i] = final_upper_band[i-1]

    if trend[i]:
      final_upper_band[i] = np.nan
    else:
      final_lower_band[i] = np.nan

  return pd.DataFrame({
    'Trend': trend,
    'Lower Band': final_lower_band,
    'Upper Band': final_upper_band
  })

def generate_trend(data, visualize=False):

  constants = [(12, 3), (10, 1), (11, 2)]
  trend_data = []
  trends = []
  upper_bands = []
  lower_bands = []

  for const_tuple in constants:
    trend = supertrend(data, atr_period=const_tuple[0], atr_multiplier=const_tuple[1])
    trend_data.append(trend)
    trends.append(trend['Trend'])
    upper_bands.append(trend['Upper Band'])
    lower_bands.append(trend['Lower Band'])

  combined_trends = pd.concat(trends, axis=1)
  combined_trends = combined_trends.all(axis=1)

  clb = pd.concat(lower_bands, axis=1)
  clb = clb.assign(FinalLowerBand=clb.mean(axis=1))

  cub = pd.concat(upper_bands, axis=1)
  cub = cub.assign(FinalUpperBand=cub.mean(axis=1))

  final_trend = pd.concat([combined_trends, clb['FinalLowerBand'], cub['FinalUpperBand']], axis=1)
  final_trend.columns = ['Trend', 'Final Lower Band', 'Final Upper Band']

  final_trend.loc[final_trend['Trend'] == True, 'Final Upper Band'] = np.nan
  final_trend.loc[final_trend['Trend'] == False, 'Final Lower Band'] = np.nan
  
  if visualize:
    
    plt.plot(data['Close'], label='Close Price')
    plt.plot(final_trend['Final Lower Band'], 'g', label = 'Final Lowerband ')
    plt.plot(final_trend['Final Upper Band'], 'r', label = 'Final Upperband ')

    plt.show()

  return final_trend




    



