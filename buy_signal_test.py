import simulator as sim
import macd_analysis
import yfinance as yf

def macd_test(ticker, start_date, end_date):

    data = yf.download(ticker, start=start_date, end=end_date, period='1d', progress=False)
    macd_res = macd_analysis.evaluate_MACD(data, True)

def enter_position(ticker, date):

    positions = dict()
    logs = []
    sim.enter_positions([ticker], date, 100000, positions, logs, historical_date=date)

    print(positions)

# Test Cases
#macd_test('AAPL', '2019-01-01', '2020-11-07')
enter_position('AAPL', '2020-11-06')