class Security:
  def __init__(self, ticker):
    self.ticker = ticker
    self.invested = False
    self.holdings = 0
    self.buy_price = 0
    self.risk_level = 0