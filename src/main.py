from typing import Union

from fastapi import FastAPI
from backtesting import backtest
import simulator as sim
from pydantic import BaseModel 
from datetime import datetime 

class BacktestRequest(BaseModel):
    tickers: Union[list[str], None] = None
    starting_balance: float
    start_date: Union[str, None] = None
    end_date: Union[str, None] = None

class UserRequest(BaseModel):
    tickers: list[str]
    positions: dict
    logs: list[dict]
    balance: float

app = FastAPI()

@app.get("/")
async def root():
    return {"Project":"RoboTrader"}

@app.post("/backtest/")
async def create_backtest_request(req : BacktestRequest):

    params = {
        "tickers": req.tickers,
        "starting_balance": req.starting_balance,
        "start_date": req.start_date,
        "end_date": req.end_date,
    }

    not_none_params = {k:v for k, v in params.items() if v is not None}
    return backtest(**not_none_params)

@app.post("/trading_day/")
async def trading_day(req : UserRequest):

    today = datetime.today().strftime('%Y-%m-%d')

    params = {
        "tickers": req.tickers,
        "today_date": today,
        "positions": req.positions,
        "balance": req.balance,
        "logs": req.logs
    }

    return sim.simulate_daily_trade(**params)