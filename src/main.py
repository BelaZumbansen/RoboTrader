from typing import Union

from fastapi import FastAPI
from backtesting import backtest
from pydantic import BaseModel 

class BacktestRequest(BaseModel):
    tickers: Union[list[str], None] = None
    starting_balance: int
    start_date: Union[str, None] = None
    end_date: Union[str, None] = None

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