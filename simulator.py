import analysis
import datetime
import yfinance as yf

def generate_sale_transaction(ticker : str, date : str, amount : int, sell_price : int, buy_price : int) -> dict:
    """
    Generate a log of a stock sale transaction containing all relevant information:
    Ticker, Transaction Date, Amount, Buy Price, Sell Price, Profit Made on Trade
    """

    return { 'ticker': ticker, 'date': date, 'amount': amount, 'sell_price': sell_price,
    'buy_price': buy_price, 'profit': (buy_price / sell_price)*100}

def generate_buy_transaction(ticker : str, date : str, amount : int, buy_price : int) -> dict:
    """
    Generate a log of a stock buy transaction containing all relevant information:
    Ticker, Transaction Date, Amount, Buy Price
    """

    return {'ticker': ticker, 'date': date, 'amount': amount, 'buy_price': buy_price}

def enter_positions(tickers : list[str], date : str, balance : int, positions : dict, logs : list[dict], backtest=False) -> int:
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
            stock = yf.Ticker(ticker)
            buy_price = stock.info['regularMarketPrice']
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

def exit_all_positions(date, positions, logs, backtest=False):
    """
    Pull all funds out of the market
    """

    # Determine which stocks we are invested in
    tickers = list(positions.keys())

    # Exit positions and return updated balance
    return exit_positions(tickers, date, positions, logs, backtest=backtest)

def get_opening_price(ticker, date):
    """
    Retrieve the historical opening price of a stock
    """

    ticker_item = yf.Ticker(ticker)
    historical = ticker_item.history(period='1w', interval='1d', start=date)
    open_price = historical['Open']
    return open_price[0]

def exit_positions(tickers, date, positions, logs, backtest=False):

    liquidated = 0

    for ticker in tickers:

        sell_positions = positions.pop(ticker, None)
        if sell_positions:
            
            if not backtest:
                stock = yf.Ticker(ticker)
                sell_price = stock.info['regularMarketPrice']
            else:
                sell_price = get_opening_price(ticker, date)

            for sell_position in sell_positions:
                liquidated += sell_price*sell_position['amount']
                log = generate_sale_transaction(ticker, date, sell_position['amount'], sell_price, sell_position['buy_price'])
                logs.append(log)

    return liquidated
    
def trading_day(tickers, today_date, last_trading_day, positions, balance, logs, backtest=False):

    yesterday_date = ''
    try:
        date_split = today_date.split('-')
        year, month, day = [date_split[i] for i in (0, 1, 2)]

        start_year = int(year) - 2
        start_date = str(start_year) + '-' + month + '-' + day
        end_date = year + '-' + month + '-' + day

        #yesterday_date = (datetime.date(int(year), int(month), int(day) - datetime.timedelta(1))).strftime('%Y-%m-%d')
    except:
        print('Date was passed in the wrong format.')
        return

    exit_list = []
    shopping_list = []

    for ticker in tickers:

        trends, buy_dates, sell_dates = analysis.evaluate_trends(ticker, start_date=start_date, end_date=end_date)
        
        buying = False

        for buy_date in buy_dates:
            if buy_date == last_trading_day:
                shopping_list.append(ticker)
                buying = True

        if buying:
            continue

        for sell_date in sell_dates:
            if sell_date == last_trading_day:
                exit_list.append(ticker)

    balance += exit_positions(exit_list, today_date, positions, logs, backtest=backtest)
    balance = enter_positions(shopping_list, today_date, balance, positions, logs, backtest=backtest)

    # Exit Trading Day, all trades have been completed
    return balance


        


