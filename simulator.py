import analysis
from datetime import *
import yfinance as yf

def generate_sale_transaction(ticker, date, amount, sell_price, buy_price):
    return { 'ticker': ticker, 'date': date, 'amount': amount, 'sell_price': sell_price,
    'buy_price': buy_price, 'profit': (buy_price / sell_price)*100}

def generate_buy_transaction(ticker, date, amount, buy_price):
    return {'ticker': ticker, 'date': date, 'amount': amount, 'buy_price': buy_price}

def enter_positions(tickers, date, balance, positions, logs):

    new_balance = balance
    allocated_each = int((balance)/len(tickers))

    for ticker in tickers:

        buy_positions = positions[ticker]
        
        if not buy_positions:
            buy_positions = []

        stock = yf.Ticker(ticker)
        buy_price = stock.info['regularMarketPrice']

        amount_to_buy = int(allocated_each/buy_price)
        if amount_to_buy > 0:
            
            new_balance -= amount_to_buy*buy_price
            log = generate_buy_transaction(ticker, date, amount_to_buy, buy_price)
            buy_positions.append(log)
            logs.append(log)
            positions[ticker] = buy_positions
    
    return new_balance

def exit_all_positions(date, positions, logs):
    tickers = positions.keys()
    return exit_positions(tickers, date, positions, logs)

def exit_positions(tickers, date, positions, logs):

    liquidated = 0

    for ticker in tickers:

        sell_positions = positions.pop(ticker, None)
        if sell_positions:

            stock = yf.Ticker(ticker)
            sell_price = stock.info['regularMarketPrice']

            for sell_position in sell_positions:
                liquidated += sell_price*sell_position['amount']
                log = generate_sale_transaction(ticker, date, sell_position['amount'], sell_price, sell_position['buy_price'])
                logs.append(log)

    return liquidated
    
def trading_day(tickers, today_date, positions, balance, logs):

    try:
        date_split = today_date.split('-')
        year, month, day = [date_split[i] for i in (0, 1, 2)]

        start_year = int(year) - 2
        start_date = str(start_year) + '-' + month + '-' + day
        end_date = year + '-' + month + '-' + day
    except:
        print('Date was passed in the wrong format.')
        return

    exit_list = []
    shopping_list = []

    for ticker in tickers:

        trends, buy_signals, sell_signals = analysis.evaluate_trends(ticker, start_date=start_date, end_date=end_date)
        
        today = date(int(year), int(month), int(day))
        buy_dates = buy_signals['Date'].values()
        sell_dates = sell_signals['Date'].values()

        buying = False

        for buy_date in buy_dates:
            if date(buy_date) == today:
                shopping_list.append(ticker)
                buying = True

        if buying:
            continue

        for sell_date in sell_dates:
            if date(sell_date) == today:
                exit_list.append(ticker)

    balance += exit_positions(exit_list, date(year, month, day), positions, logs)
    balance = enter_positions(shopping_list, date(year, month, day), balance, positions, logs)

    # Exit Trading Day, all trades have been completed
    return balance


        


