from security import Security
from analysis import *
import math

class User:
  def __init__(self, email, funds, securities):
    self.email = email
    self.funds = funds
    self.securities = securities

  def executeTransaction(self, requested_holdings, security : Security):

    if requested_holdings > 0:

      buy_price = current_price(security.ticker)

      if buy_price*requested_holdings > self.funds:     
        print('Insufficient Funds')
        return False
      
      security.buy_price = buy_price
      security.holdings += requested_holdings
      self.funds -= (buy_price*requested_holdings)
      security.invested = True
    
    else:

      sell_price = current_price(security.ticker)

      if requested_holdings < security.holdings:
        print('Attempting to sell more holdings than are owned.')
        return False
      
      security.holdings += requested_holdings
      
      if security.holdings == 0:
        security.invested  = False
        security.buy_price = 0
      
    return True

  def simpleAnalysisTrader(self):

    for security in self.securities:

      # Ensure that this object has the right type
      if not isinstance(security, Security):
        continue

      if security.invested:

        if reached_risk_level(security):
          self.executeTransaction(-security.holdings, security)
        else:
          # Perform further analysis whether it is time to sell
          print('Further analysis missing')   
      else:

        cur_price = current_price(security.ticker)

        if cur_price >= calculate_high(security.ticker, period='5d'):
          
          # Until further analysis established we will always purchase either 1 (if possible) stock or around 10% of our funds worth
          position_size = math.ciel(math.floor(self.funds / cur_price)*0.1)

          self.executeTransaction(position_size, security)


    