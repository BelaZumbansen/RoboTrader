import analysis
import datetime
import yfinance as yf
import numpy as np
import pandas_market_calendars as mcal
import pandas as pd

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

def generate_sale_transaction(ticker : str, date : str, amount : int, sell_price : float, buy_price : float) -> dict:
    """
    Generate a log of a stock sale transaction containing all relevant information:
    Ticker, Transaction Date, Amount, Buy Price, Sell Price, Profit Made on Trade
    """

    return { 'ticker': ticker, 'date': date, 'amount': amount, 'sell_price': sell_price,
    'buy_price': buy_price, 'profit': ((buy_price - sell_price) / sell_price)*100}

def generate_buy_transaction(ticker : str, date : str, amount : int, buy_price : float) -> dict:
    """
    Generate a log of a stock buy transaction containing all relevant information:
    Ticker, Transaction Date, Amount, Buy Price
    """

    return {'ticker': ticker, 'date': date, 'amount': amount, 'buy_price': buy_price}

def enter_positions(tickers : list[str], date : str, balance : float, positions : dict, logs : list[dict], backtest=False) -> float:
    """
    Make an Investment in the passed stock. Portion of balance will be allocated to the purchase.
    If backtesting, the opening price on the purchase date will be used.
    Otherwise, we use the current market price at the time of the transaction.
    """

    if len(tickers) == 0:
        return balance

    new_balance = balance

    # Divide funds between stocks we wish to buy
    allocated_each = int((balance)/len(tickers))

    # Perform each transaction
    for ticker in tickers:

        # Check if we are already invested
        try:
            buy_positions = positions[ticker]
        except:
            buy_positions = []

        # If not backtesting, retrieve current market price
        if not backtest:
            sell_price = analysis.current_price(ticker)
        # If backtesting, retrieve historical opening price
        else:
            buy_price = get_opening_price(ticker, date)

        # Determine how many stocks we can buy with the allocated funds
        amount_to_buy = int(allocated_each/buy_price)

        # If we have enough funds to make a purchase, go through with it
        if amount_to_buy > 0:
            
            # Update balance and create transaction log
            new_balance -= amount_to_buy*buy_price
            log = generate_buy_transaction(ticker, date, amount_to_buy, buy_price)
            buy_positions.append(log)
            logs.append(log)

            # Store active position
            positions[ticker] = buy_positions
    
    # Return our balance after all transactions have been made
    return new_balance

def exit_all_positions(date : str, positions : dict, logs : list[dict], backtest=False) -> float:
    """
    Pull all funds out of the market
    """

    # Determine which stocks we are invested in
    tickers = list(positions.keys())

    # Exit positions and return updated balance
    return exit_positions(tickers, date, positions, logs, backtest=backtest)

def get_opening_price(ticker : str, date : str) -> float:
    """
    Retrieve the historical opening price of a stock
    """

    ticker_item = yf.Ticker(ticker)
    
    # Retrieve History from Yahoo Finance
    historical = ticker_item.history(period='1w', interval='1d', start=date)
    
    # Seperate open prices
    open_price = historical['Open']
    # First index will contain price on date as this was the beginning of our search range
    return open_price[0]

def exit_positions(tickers : list[str], date : str, positions : dict, logs : list[dict], 
                   backtest=False) -> float:
    """
    Pull out of given stocks and return the amount of funds liquidated by the sale. The sale is logged and
    the profit made on the trade is tracked.
    """

    liquidated = 0

    # Iterate over positions to pull out of
    for ticker in tickers:

        # Retrieve list of open positions, one per buy since the last sell
        sell_positions = positions.pop(ticker, None)

        # If we have open positions, pull out of all of them
        if sell_positions:

            # If not backtesting, base the selling price on the current open market price
            if not backtest:
                sell_price = analysis.current_price(ticker)
            # If backtesting, get the opening price on the day of the sale
            else:
                sell_price = get_opening_price(ticker, date)

            # Sell all positions in this stock
            for sell_position in sell_positions:
                liquidated += sell_price*sell_position['amount']
                
                # Create transaction log
                log = generate_sale_transaction(ticker, date, sell_position['amount'], sell_price, sell_position['buy_price'])
                logs.append(log)

    # Return the amount of funds freed up by this sale
    return liquidated

def simulate_daily_trades(tickers : list[str], today_date : str, positions : dict,
                          balance : float, logs : list[dict]):
    """
    Simulate buy and sell for today's date based on analysis up to closing on the previous trading date.
    """

    dates = get_trading_days('2023-01-01', today_date)

    return trading_day(tickers, dates[-1], dates[-2], positions, balance, logs)


def trading_day(tickers : list[str], today_date : str, last_trading_day : str, positions : dict,
                balance : float, logs : list[dict], backtest=False) -> float:
    """
    Execute trading strategy on a Trading Day. Strategy involves calculating buy and sell signals to 
    determine when to buy in to and exit from positions. We calculate trends and decide which stocks
    are giving us which signals. If we receive a buy signal we buy into and if we receive a sell signal
    for a stock we are currently holding, we back out.
    This method updates the positions dictionary and log list.
    Returns the updated balance after the day of trading.
    """

    yesterday_date = ''
    try:
        # Parse the date
        date_split = today_date.split('-')
        year, month, day = [date_split[i] for i in (0, 1, 2)]

        # Determine when to start our analysis. We choose to do 2 years ago
        start_year = int(year) - 2
        # Account for leap years
        if month == 2 and day == 28:
            start_date = str(start_year) + '-' + month + '-' + str(int(day) - 1)
        else:
            start_date = str(start_year) + '-' + month + '-' + day
        
        # We end our analysis at the current date
        end_date = year + '-' + month + '-' + day
        #yesterday_date = (datetime.date(int(year), int(month), int(day) - datetime.timedelta(1))).strftime('%Y-%m-%d')
    except:
        print('Date was passed in the wrong format.')
        return

    exit_list = []
    shopping_list = []

    # Execute strategy on each stock we would like to trade on
    for ticker in tickers:

        # Evaluate market trends and determine dates on which they tell us to sell or buy
        trends, buy_dates, sell_dates = analysis.evaluate_trends(ticker, start_date=start_date, end_date=end_date)

        # Check if last trading day is in buy dates
        # Flagged day will be the last trading day if we wish to buy today as the strategy operates on
        # buying as soon as the market opens by analyzing closing prices.
        if last_trading_day in buy_dates:
            shopping_list.append(ticker)
            # Do not check for back out if we know we are buying today.
            continue
        
        # Check if last trading day is in the sell dates
        if last_trading_day in sell_dates:
            exit_list.append(ticker)

    # Back out of positions and update balance with freed funds
    balance += exit_positions(exit_list, today_date, positions, logs, backtest=backtest)
    # Enter new positions
    balance = enter_positions(shopping_list, today_date, balance, positions, logs, backtest=backtest)

    # Exit Trading Day, all trades have been completed
    return balance


        


