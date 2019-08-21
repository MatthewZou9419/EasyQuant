# -*- coding: utf-8 -*-
"""
Created on 2019/8/8 上午11:51 
@file: EStrategyLocalTest.py
@author: ZouHao
"""
from collections import deque
import numpy as np

from EasyEngine.EStrategyEngine import Engine
from EasyUtil.EMongoUtil import MongoClient
from EasyUtil.EReportingUtil import plot_performance

client = MongoClient()

# --------------------------初始化参数设定--------------------------
start_date = '2005-1-1'
end_date = '2019-1-1'
frequency = 'day'
portfolio_params = {
    '_starting_cash': 1000000,
}
reference_symbol = '000001.XSHE'

e = Engine(
    _start_date=start_date,
    _end_date=end_date,
    _frequency=frequency,
    _portfolio_params=portfolio_params,
    _reference_symbol=reference_symbol
)

reference = e.get_reference()

# --------------------------策略撰写--------------------------
atr_window = 14
atr_n = 1
add_pct = 0.1
stop_win_pct = 0.1
stop_loss_pct = 0.1
tr_q = deque(maxlen=atr_window)
close_q = deque(maxlen=2)
open_q = deque(maxlen=2)
code = '000001.XSHE'
for bar in reference:
    e.update(bar['time'])

    high = bar['high']
    low = bar['low']
    close = bar['close']
    close_q.append(close)
    if len(close_q) < 2:
        continue
    tr = max([high - low, abs(high - close_q[0]), abs(close_q[0] - low)])
    tr_q.append(tr)
    if len(tr_q) < atr_window:
        continue
    atr = np.mean(tr_q)
    # first open
    if e.context.portfolio[0].positions_value == 0 and close - close_q[0] > atr_n * atr:
        cash = e.context.portfolio[0].available_cash * add_pct
        amount = int((cash / close) / 100)
        order = e.order(code, amount)
        open_q.append(order.avg_cost)
    # add position
    elif close > np.mean(open_q) * (1 + stop_win_pct):
        cash = e.context.portfolio[0].available_cash * add_pct
        amount = int((cash / close) / 100)
        order = e.order(code, amount)
        open_q.append(order.avg_cost)
    # close
    elif close < np.mean(open_q) * (1 - stop_loss_pct):
        e.order_target(code, 0)
        open_q.clear()

performance_df, order_df = e.get_report()
plot_performance(performance_df)
