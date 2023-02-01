from setuptools import setup

setup(
  name='robotrader',
  version='0.1',
  description='Robotic Trader',
  url='https://github.com/BelaZumbansen/RoboTrader',
  author='Bela Zumbansen',
  author_email='bela.zbansen@gmail.com',
  license='MIT',
  packages=['robotrader'],
  install_requires=[
    'pandas',
    'numpy',
    'pandas_market_calendars',
    'yfinance',
  ],
)